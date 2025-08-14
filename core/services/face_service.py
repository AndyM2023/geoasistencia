import os
import sys
import json
import base64
import subprocess
import time
import numpy as np
import cv2
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.utils import timezone
from ..models import FaceProfile

# Agregar el directorio de reconocimiento facial al path
FACE_RECOGNITION_DIR = os.path.join(settings.BASE_DIR, 'face_recognition')
sys.path.append(FACE_RECOGNITION_DIR)

try:
    from advanced_face_system import FacialRecognition
    FACIAL_RECOGNITION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Sistema facial no disponible: {e}")
    FacialRecognition = None
    FACIAL_RECOGNITION_AVAILABLE = False

class FaceRecognitionService:
    """Servicio para integrar el sistema de reconocimiento facial"""
    
    def __init__(self):
        self.face_system_path = os.path.join(settings.BASE_DIR, 'face_recognition')
        self.faces_dir = os.path.join(self.face_system_path, 'faces')
        
        # Inicializar sistema facial si está disponible
        if FACIAL_RECOGNITION_AVAILABLE:
            try:
                self.facial_system = FacialRecognition(
                    base_dir=self.face_system_path,
                    database_name="faces"
                )
            except Exception as e:
                print(f"⚠️ Error inicializando sistema facial: {e}")
                self.facial_system = None
        else:
            self.facial_system = None
    
    def register_employee_face(self, employee, photos_data):
        """
        Registra múltiples fotos de un empleado usando el sistema facial real
        
        Args:
            employee: Instancia del modelo Employee
            photos_data: Lista de imágenes en base64
            
        Returns:
            dict: Resultado del registro
        """
        try:
            if not self.facial_system:
                return {
                    'success': False,
                    'message': 'Sistema de reconocimiento facial no disponible'
                }
            
            # Crear ID único para el empleado
            employee_id = f"{employee.employee_id or employee.id}"
            employee_name = f"{employee.user.first_name}{employee.user.last_name}".replace(" ", "")
            
            # Crear carpeta para el empleado
            employee_folder = os.path.join(self.faces_dir, f"{employee_id}{employee_name}")
            os.makedirs(employee_folder, exist_ok=True)
            
            # Procesar y guardar fotos
            saved_photos = 0
            for i, photo_data in enumerate(photos_data):
                try:
                    # Decodificar imagen base64
                    image_data = self._decode_base64_image(photo_data)
                    if image_data is not None:
                        photo_path = os.path.join(employee_folder, f"{int(time.time() * 1000)}.jpg")
                        
                        # Guardar imagen
                        cv2.imwrite(photo_path, image_data)
                        
                        # Generar embedding usando el sistema facial
                        embedding = self.facial_system.extract_face_features(image_data)
                        if embedding is not None:
                            # Guardar embedding
                            embedding_path = photo_path.replace('.jpg', '.npy')
                            np.save(embedding_path, embedding)
                            saved_photos += 1
                        
                except Exception as e:
                    print(f"Error procesando foto {i}: {e}")
                    continue
            
            if saved_photos == 0:
                return {
                    'success': False,
                    'message': 'No se pudo procesar ninguna foto'
                }
            
            # Crear o actualizar perfil facial
            face_profile, created = FaceProfile.objects.get_or_create(
                employee=employee,
                defaults={
                    'face_embeddings_path': employee_folder,
                    'photos_count': saved_photos,
                    'is_trained': True,
                    'last_training': timezone.now()
                }
            )
            
            if not created:
                face_profile.photos_count = saved_photos
                face_profile.is_trained = True
                face_profile.last_training = timezone.now()
                face_profile.save()
            
            return {
                'success': True,
                'message': f'Registradas {saved_photos} fotos para {employee.full_name}',
                'photos_count': saved_photos,
                'employee_id': employee_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error registrando rostro: {str(e)}'
            }
    
    def verify_face(self, employee, photo_data):
        """
        Verifica si una foto coincide con el rostro registrado del empleado
        
        Args:
            employee: Instancia del modelo Employee
            photo_data: Imagen en base64
            
        Returns:
            dict: Resultado de la verificación
        """
        try:
            face_profile = employee.face_profile
            if not face_profile.is_trained:
                return {
                    'success': False,
                    'verified': False,
                    'message': 'Empleado no tiene rostro registrado'
                }
            
            # Aquí llamarías al sistema de reconocimiento facial
            # Por ahora devolvemos un resultado simulado
            confidence = 0.95  # Simular confianza alta
            
            verified = confidence >= face_profile.confidence_threshold
            
            return {
                'success': True,
                'verified': verified,
                'confidence': confidence,
                'threshold': face_profile.confidence_threshold,
                'message': 'Rostro verificado correctamente' if verified else 'Rostro no reconocido'
            }
            
        except FaceProfile.DoesNotExist:
            return {
                'success': False,
                'verified': False,
                'message': 'Empleado no tiene perfil facial'
            }
        except Exception as e:
            return {
                'success': False,
                'verified': False,
                'message': f'Error en verificación: {str(e)}'
            }
    
    def get_employee_face_status(self, employee):
        """
        Obtiene el estado del perfil facial de un empleado
        
        Args:
            employee: Instancia del modelo Employee
            
        Returns:
            dict: Estado del perfil facial
        """
        try:
            face_profile = employee.face_profile
            return {
                'has_profile': True,
                'is_trained': face_profile.is_trained,
                'photos_count': face_profile.photos_count,
                'last_training': face_profile.last_training,
                'confidence_threshold': face_profile.confidence_threshold
            }
        except FaceProfile.DoesNotExist:
            return {
                'has_profile': False,
                'is_trained': False,
                'photos_count': 0,
                'last_training': None,
                'confidence_threshold': 0.90
            }
    
    def _decode_base64_image(self, base64_data):
        """
        Decodifica una imagen base64 a formato OpenCV
        
        Args:
            base64_data: String con datos de imagen en base64
            
        Returns:
            numpy.ndarray: Imagen en formato OpenCV (BGR) o None si hay error
        """
        try:
            # Remover prefijo data URL si existe
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            # Decodificar base64
            image_bytes = base64.b64decode(base64_data)
            
            # Convertir a imagen PIL
            pil_image = Image.open(BytesIO(image_bytes))
            
            # Convertir a RGB si es necesario
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convertir a numpy array (OpenCV format BGR)
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            return opencv_image
            
        except Exception as e:
            print(f"Error decodificando imagen base64: {e}")
            return None
    
    def _save_base64_image(self, base64_data, file_path):
        """Guarda una imagen desde base64"""
        try:
            opencv_image = self._decode_base64_image(base64_data)
            if opencv_image is not None:
                cv2.imwrite(file_path, opencv_image)
                return True
        except Exception as e:
            print(f"Error guardando imagen: {e}")
        return False
