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
        """Alias para mantener compatibilidad - redirige al método principal"""
        return self.register_or_update_employee_face(employee, photos_data)
    
    def register_or_update_employee_face(self, employee, photos_data):
        """
        Registra o actualiza múltiples fotos de un empleado usando el sistema facial real
        
        Args:
            employee: Instancia del modelo Employee
            photos_data: Lista de imágenes en base64
            
        Returns:
            dict: Resultado del registro/actualización
        """
        try:
            # Verificar si ya existe un perfil facial
            is_update = False
            try:
                existing_profile = employee.face_profile
                is_update = True
                print(f"🔄 ACTUALIZANDO REGISTRO FACIAL PARA EMPLEADO: {employee.full_name}")
                print(f"📸 Fotos anteriores: {existing_profile.photos_count}")
            except FaceProfile.DoesNotExist:
                print(f"🆕 NUEVO REGISTRO FACIAL PARA EMPLEADO: {employee.full_name}")
            
            print(f"📸 Fotos nuevas recibidas: {len(photos_data)}")
            
            if not self.facial_system:
                print("❌ Sistema facial no disponible")
                return {
                    'success': False,
                    'message': 'Sistema de reconocimiento facial no disponible'
                }
            
            # Crear ID único para el empleado
            employee_id = f"{employee.employee_id or employee.id}"
            employee_name = f"{employee.user.first_name}{employee.user.last_name}".replace(" ", "")
            
            print(f"🆔 ID del empleado: {employee_id}")
            print(f"📝 Nombre del empleado: {employee_name}")
            
            # Crear carpeta para el empleado
            employee_folder = os.path.join(self.faces_dir, f"{employee_id}{employee_name}")
            
            # Si es actualización, limpiar carpeta anterior
            if is_update and os.path.exists(employee_folder):
                print(f"🧹 Limpiando carpeta anterior: {employee_folder}")
                import shutil
                shutil.rmtree(employee_folder)
                print(f"✅ Carpeta anterior eliminada")
            
            os.makedirs(employee_folder, exist_ok=True)
            
            print(f"📁 Carpeta creada: {employee_folder}")
            print(f"📁 Carpeta existe: {os.path.exists(employee_folder)}")
            
            # Procesar y guardar fotos
            saved_photos = 0
            for i, photo_data in enumerate(photos_data):
                try:
                    print(f"\n🔄 Procesando foto {i+1}/{len(photos_data)}")
                    
                    # Decodificar imagen base64
                    print("   📥 Decodificando imagen base64...")
                    image_data = self._decode_base64_image(photo_data)
                    
                    if image_data is not None:
                        print(f"   ✅ Imagen decodificada: {image_data.shape}")
                        
                        # Guardar imagen
                        photo_path = os.path.join(employee_folder, f"{int(time.time() * 1000)}.jpg")
                        print(f"   💾 Guardando imagen en: {photo_path}")
                        
                        save_result = cv2.imwrite(photo_path, image_data)
                        print(f"   💾 Resultado del guardado: {save_result}")
                        
                        # Verificar que se guardó
                        if os.path.exists(photo_path):
                            print(f"   ✅ Archivo guardado: {os.path.getsize(photo_path)} bytes")
                        else:
                            print(f"   ❌ Archivo NO se guardó")
                            continue
                        
                        # Generar embedding usando el sistema facial
                        print("   🧠 Generando embedding facial...")
                        embedding = self.facial_system.extract_face_features(image_data)
                        
                        if embedding is not None:
                            print(f"   ✅ Embedding generado: {len(embedding)} características")
                            
                            # Guardar embedding
                            embedding_path = photo_path.replace('.jpg', '.npy')
                            np.save(embedding_path, embedding)
                            
                            if os.path.exists(embedding_path):
                                print(f"   ✅ Embedding guardado: {os.path.getsize(embedding_path)} bytes")
                                saved_photos += 1
                            else:
                                print(f"   ❌ Embedding NO se guardó")
                        else:
                            print("   ❌ No se pudo generar embedding")
                        
                except Exception as e:
                    print(f"   ❌ Error procesando foto {i}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            print(f"\n📊 RESUMEN DEL PROCESAMIENTO:")
            print(f"   📸 Fotos procesadas: {saved_photos}")
            print(f"   📁 Archivos en carpeta: {len(os.listdir(employee_folder)) if os.path.exists(employee_folder) else 0}")
            
            if saved_photos == 0:
                print("❌ No se pudo procesar ninguna foto")
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
            
            # Verificación facial real usando el sistema de reconocimiento
            if not self.facial_system:
                return {
                    'success': False,
                    'verified': False,
                    'message': 'Sistema de reconocimiento facial no disponible'
                }
            
            try:
                # Decodificar imagen capturada
                captured_image = self._decode_base64_image(photo_data)
                if captured_image is None:
                    return {
                        'success': False,
                        'verified': False,
                        'message': 'Error procesando imagen capturada'
                    }
                
                # Verificar rostro usando el sistema facial real
                print(f"🔍 Verificando rostro de {employee.full_name}...")
                print(f"📁 Carpeta del empleado: {employee.employee_id}")
                
                # Llamar al sistema de reconocimiento facial real
                verification_result = self.facial_system.identify_person(
                    image=captured_image,
                    similarity_threshold=face_profile.confidence_threshold
                )
                
                print(f"🎯 Resultado de verificación: {verification_result}")
                
                # Extraer resultados reales del sistema de identificación
                if not verification_result.get('success', False):
                    return {
                        'success': False,
                        'verified': False,
                        'message': f"Error en identificación: {verification_result.get('error', 'Error desconocido')}"
                    }
                
                similarity = verification_result.get('similarity', 0.0)
                person_identified = verification_result.get('person_identified')
                
                # Verificar si la persona identificada coincide con el empleado
                print(f"🔍 DEBUG - Comparando IDs:")
                print(f"   ID del sistema facial: {person_identified.get('id') if person_identified else 'None'}")
                print(f"   ID del empleado: {employee.employee_id}")
                print(f"   Tipo ID facial: {type(person_identified.get('id') if person_identified else None)}")
                print(f"   Tipo ID empleado: {type(employee.employee_id)}")
                
                # Comparar IDs (el sistema facial devuelve solo números, no "EMP006")
                facial_id = str(person_identified.get('id')) if person_identified else None
                employee_id_str = str(employee.employee_id)
                
                # Extraer solo el número del employee_id (EMP006 -> 6)
                if employee_id_str.startswith('EMP'):
                    employee_number = employee_id_str[3:]  # Quitar "EMP"
                else:
                    employee_number = employee_id_str
                
                print(f"   ID facial limpio: {facial_id}")
                print(f"   Número del empleado: {employee_number}")
                
                if person_identified and facial_id == employee_number:
                    verified = similarity >= face_profile.confidence_threshold
                    message = f'Rostro verificado correctamente (Similitud: {similarity:.2f})' if verified else f'Rostro no reconocido (Similitud: {similarity:.2f})'
                else:
                    verified = False
                    message = f'Rostro no coincide con el empleado (Similitud: {similarity:.2f}) - ID facial: {facial_id}, ID empleado: {employee_number}'
                
                return {
                    'success': True,
                    'verified': verified,
                    'confidence': similarity,
                    'threshold': face_profile.confidence_threshold,
                    'message': message
                }
                
            except Exception as e:
                print(f"❌ Error en verificación facial real: {e}")
                return {
                    'success': False,
                    'verified': False,
                    'message': f'Error en verificación: {str(e)}'
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
        Obtiene el estado del perfil facial de un empleado con verificación de sincronización
        
        Args:
            employee: Instancia del modelo Employee
            
        Returns:
            dict: Estado del perfil facial
        """
        try:
            face_profile = employee.face_profile
            
            # Verificar si existe carpeta física
            employee_id = str(employee.employee_id or employee.id)
            employee_name = f"{employee.user.first_name}{employee.user.last_name}".replace(" ", "")
            employee_folder = os.path.join(self.faces_dir, f"{employee_id}{employee_name}")
            folder_exists = os.path.exists(employee_folder)
            
            # Verificar si está en el sistema facial
            system_has_person = False
            if self.facial_system:
                try:
                    result = self.facial_system.list_all_persons()
                    if result.get('success'):
                        for person in result.get('persons', []):
                            if person.get('id') == employee_id:
                                system_has_person = True
                                break
                except:
                    pass
            
            return {
                'has_profile': True,
                'is_trained': face_profile.is_trained,
                'photos_count': face_profile.photos_count,
                'last_training': face_profile.last_training,
                'confidence_threshold': face_profile.confidence_threshold,
                'folder_exists': folder_exists,
                'system_has_person': system_has_person,
                'is_synchronized': folder_exists and system_has_person
            }
        except FaceProfile.DoesNotExist:
            return {
                'has_profile': False,
                'is_trained': False,
                'photos_count': 0,
                'last_training': None,
                'confidence_threshold': 0.80,
                'folder_exists': False,
                'system_has_person': False,
                'is_synchronized': True  # Si no existe en ningún lado, está sincronizado
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
            print(f"      📥 Decodificando imagen base64...")
            print(f"      📏 Longitud de datos: {len(base64_data)} caracteres")
            
            # Remover prefijo data URL si existe
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
                print(f"      🔧 Prefijo data URL removido")
            
            # Decodificar base64
            print(f"      🔓 Decodificando base64...")
            image_bytes = base64.b64decode(base64_data)
            print(f"      📦 Bytes decodificados: {len(image_bytes)} bytes")
            
            # Convertir a imagen PIL
            print(f"      🖼️  Convirtiendo a imagen PIL...")
            pil_image = Image.open(BytesIO(image_bytes))
            print(f"      📐 Dimensiones PIL: {pil_image.size} | Modo: {pil_image.mode}")
            
            # Convertir a RGB si es necesario
            if pil_image.mode != 'RGB':
                print(f"      🔄 Convirtiendo modo de {pil_image.mode} a RGB...")
                pil_image = pil_image.convert('RGB')
            
            # Convertir a numpy array (OpenCV format BGR)
            print(f"      🔄 Convirtiendo a formato OpenCV (BGR)...")
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            print(f"      ✅ Imagen OpenCV creada: {opencv_image.shape}")
            
            return opencv_image
            
        except Exception as e:
            print(f"      ❌ Error decodificando imagen base64: {e}")
            import traceback
            traceback.print_exc()
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
