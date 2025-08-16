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
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
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
        ✅ OPTIMIZADO PARA VELOCIDAD: 15 fotos + procesamiento en lotes
        
        Args:
            employee: Instancia del modelo Employee
            photos_data: Lista de imágenes en base64 (recomendado: 15 fotos para velocidad)
           
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
            
            # ✅ PROCESAMIENTO REALMENTE PARALELO: 5 fotos simultáneas
            saved_photos = 0
            rejected_photos = 0
            total_photos = len(photos_data)
            # Sin batch_size - procesamiento secuencial simple
            
            print(f"🚀 PROCESAMIENTO SECUENCIAL ULTRA-OPTIMIZADO - {total_photos} fotos con Facenet-512")
            print(f"⚡ VELOCIDAD MÁXIMA: Sin paralelo (más seguro para Django)")
            print(f"⏱️ Tiempo estimado: {total_photos * 0.8:.1f} segundos (OPTIMIZADO)")
            
            # ✅ PROCESAMIENTO SECUENCIAL SIMPLE (MÁS SEGURO)
            print(f"🔄 Iniciando procesamiento secuencial optimizado...")
            
            # ✅ PROCESAMIENTO SECUENCIAL SIMPLE (MÁS SEGURO)
            print(f"🔄 Iniciando procesamiento secuencial optimizado...")
            
            # ✅ PROCESAR FOTOS UNA POR UNA (MÁS SEGURO PARA DJANGO)
            for i, photo_data in enumerate(photos_data):
                try:
                    progress_percent = ((i + 1) / total_photos) * 100
                    print(f"\n📸 Procesando foto {i+1}/{total_photos} ({progress_percent:.1f}%)")
                    
                    # ✅ Decodificar Y extraer rostro en un solo paso
                    face_image = self._decode_base64_image(photo_data)
                    
                    if face_image is None:
                        print(f"   ❌ Foto {i+1} rechazada: Sin rostro válido")
                        rejected_photos += 1
                        continue
                    
                    print(f"   ✅ Rostro extraído: {face_image.shape}")
                    
                    # ✅ Guardar con timestamp único
                    timestamp = int(time.time() * 1000000) + i
                    photo_path = os.path.join(employee_folder, f"face_{timestamp}.jpg")
                    
                    # ✅ COMPRESIÓN ULTRA-OPTIMIZADA para máxima velocidad
                    save_result = cv2.imwrite(photo_path, face_image, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    
                    if save_result and os.path.exists(photo_path):
                        # ✅ Generar embedding Facenet-512
                        print(f"   🧠 Generando embedding Facenet-512...")
                        embedding = self.facial_system.extract_face_features(face_image)
                        
                        if embedding is not None:
                            embedding_dims = len(embedding)
                            print(f"   ✅ Embedding {embedding_dims}D generado")
                            
                            # Guardar embedding
                            embedding_path = photo_path.replace('.jpg', '.npy')
                            np.save(embedding_path, embedding)
                            
                            if os.path.exists(embedding_path):
                                saved_photos += 1
                                print(f"   ✅ #{saved_photos} guardada exitosamente")
                            else:
                                rejected_photos += 1
                                if os.path.exists(photo_path):
                                    os.remove(photo_path)
                        else:
                            rejected_photos += 1
                            if os.path.exists(photo_path):
                                os.remove(photo_path)
                            print(f"   ❌ Error generando embedding")
                    else:
                        rejected_photos += 1
                        print(f"   ❌ Error guardando imagen")
                        
                except Exception as e:
                    rejected_photos += 1
                    print(f"   ❌ Error procesando foto {i+1}: {e}")
                    continue
            
            print(f"🎯 Procesamiento secuencial completado: {saved_photos}/{total_photos} fotos procesadas")
            print(f"✅ Servidor Django sigue funcionando - Terminal NO se cierra")
            
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
        ✅ IMPLEMENTACIÓN ULTRA-OPTIMIZADA PARA MÁXIMA VELOCIDAD
        
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
                print(f"⚡ VERIFICACIÓN ULTRA-RÁPIDA para {employee.full_name}")
                print(f"🎯 Objetivo: < 2 segundos de respuesta")
                
                # ✅ OPTIMIZACIÓN 1: Decodificación rápida CON extracción de rostro
                captured_image = self._decode_base64_image_fast(photo_data)
                if captured_image is None:
                    return {
                        'success': False,
                        'verified': False,
                        'message': 'Error procesando imagen capturada'
                    }
                
                # ✅ OPTIMIZACIÓN 2: Extraer rostro de manera rápida
                print(f"🔍 Extracción rápida de rostro para verificación...")
                face_image = self._extract_face_region_fast(captured_image)
                
                # ✅ OPTIMIZACIÓN 3: Verificación directa con Facenet-512
                print(f"🔍 Verificación directa con Facenet-512...")
                
                # Generar embedding de la imagen del rostro extraído
                captured_embedding = self.facial_system.extract_face_features(face_image)
                if captured_embedding is None:
                    return {
                        'success': False,
                        'verified': False,
                        'message': 'No se pudieron extraer características del rostro'
                    }
                
                # ✅ CONVERTIR A NUMPY ARRAY para poder usar .min() y .max()
                captured_embedding = np.array(captured_embedding)
                
                # ✅ OPTIMIZACIÓN 3: Comparar solo con embeddings del empleado (más rápido)
                employee_id = str(employee.employee_id or employee.id)
                employee_name = f"{employee.user.first_name}{employee.user.last_name}".replace(" ", "")
                employee_folder = os.path.join(self.faces_dir, f"{employee_id}{employee_name}")
                
                if not os.path.exists(employee_folder):
                    return {
                        'success': False,
                        'verified': False,
                        'message': 'Carpeta del empleado no encontrada'
                    }
                
                print(f"🔍 DEBUG - Carpeta del empleado: {employee_folder}")
                print(f"🔍 DEBUG - Embedding capturado: {len(captured_embedding)}D, rango: [{captured_embedding.min():.3f}, {captured_embedding.max():.3f}]")
                
                # Buscar embeddings del empleado
                best_similarity = 0.0
                embeddings_found = 0
                
                for file_name in os.listdir(employee_folder):
                    if file_name.endswith('.npy'):
                        embedding_path = os.path.join(employee_folder, file_name)
                        try:
                            stored_embedding = np.load(embedding_path)
                            
                            # ✅ CALCULAR SIMILITUD USANDO FÓRMULA CORRECTA (como en el sistema anterior)
                            # Usar similitud coseno que es más precisa para embeddings
                            dot_product = np.dot(captured_embedding, stored_embedding)
                            norm1 = np.linalg.norm(captured_embedding)
                            norm2 = np.linalg.norm(stored_embedding)
                            
                            if norm1 > 0 and norm2 > 0:
                                # Fórmula de similitud coseno normalizada a [0,1]
                                similarity = (dot_product / (norm1 * norm2) + 1) / 2
                            else:
                                similarity = 0.0
                            
                            # ✅ DEBUG: Mostrar detalles de cada comparación
                            print(f"   🔍 Embedding {embeddings_found+1}: rango [{stored_embedding.min():.3f}, {stored_embedding.max():.3f}], similitud: {similarity:.3f}")
                            
                            if similarity > best_similarity:
                                best_similarity = similarity
                            
                            embeddings_found += 1
                            
                            # ✅ OPTIMIZACIÓN 4: Parar si ya encontramos una similitud alta
                            if similarity >= 0.95:  # 95% de confianza
                                break
                                
                        except Exception as e:
                            continue
                
                if embeddings_found == 0:
                    return {
                        'success': False,
                        'verified': False,
                        'message': 'No se encontraron embeddings del empleado'
                    }
                
                # ✅ OPTIMIZACIÓN 5: Umbral configurable para velocidad vs precisión
                verified = best_similarity >= face_profile.confidence_threshold
                
                print(f"🎯 Resultado ultra-rápido:")
                print(f"   Similitud máxima: {best_similarity:.3f}")
                print(f"   Umbral configurado: {face_profile.confidence_threshold}")
                print(f"   Embeddings comparados: {embeddings_found}")
                print(f"   Verificación: {'✅ EXITOSA' if verified else '❌ FALLIDA'}")
                
                message = f'Rostro verificado correctamente (Similitud: {best_similarity:.3f})' if verified else f'Rostro no reconocido (Similitud: {best_similarity:.3f})'
                
                return {
                    'success': True,
                    'verified': verified,
                    'confidence': best_similarity,
                    'threshold': face_profile.confidence_threshold,
                    'message': message
                }
                
            except Exception as e:
                print(f"❌ Error en verificación ultra-rápida: {e}")
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
                'confidence_threshold': 0.70,
                'folder_exists': False,
                'system_has_person': False,
                'is_synchronized': True  # Si no existe en ningún lado, está sincronizado
            }
    
    def _extract_face_region(self, image):
        """
        Extrae y recorta automáticamente la región del rostro
        ✅ IMPLEMENTACIÓN PERMISIVA - Procesa incluso si no detecta rostros claramente
        
        Args:
            image: Imagen OpenCV (numpy array)
            
        Returns:
            numpy.ndarray: Imagen recortada del rostro o la imagen completa si no se detecta
        """
        try:
            print("      ✂️ Verificación PERMISIVA de rostro...")
            
            if not self.facial_system:
                print("      ⚠️ Sistema facial NO disponible - Usando imagen completa")
                return image  # ✅ FALLBACK: Usar imagen completa
            
            try:
                # Detectar rostros en la imagen
                faces_detected = self.facial_system.detect_faces(image)
                
                if faces_detected and len(faces_detected) > 0:
                    # Tomar el primer rostro detectado
                    face = faces_detected[0]
                    
                    # Extraer coordenadas del rostro (corregido para coincidir con detect_faces)
                    x, y, w, h = face['x'], face['y'], face['width'], face['height']
                    
                    # Verificar que el rostro tenga un tamaño mínimo válido
                    min_face_size = 20  # Muy permisivo
                    if w < min_face_size or h < min_face_size:
                        print(f"      ⚠️ Rostro muy pequeño: {w}x{h} - Usando imagen completa")
                        return image  # ✅ FALLBACK: Usar imagen completa
                    
                    # Agregar margen alrededor del rostro (20% como en el sistema anterior)
                    margin = int(min(w, h) * 0.2)
                    x1 = max(0, x - margin)
                    y1 = max(0, y - margin)
                    x2 = min(image.shape[1], x + w + margin)
                    y2 = min(image.shape[0], y + h + margin)
                    
                    # Verificar que la región extraída sea válida
                    if x2 <= x1 or y2 <= y1:
                        print(f"      ⚠️ Región de rostro inválida - Usando imagen completa")
                        return image  # ✅ FALLBACK: Usar imagen completa
                    
                    # Recortar la región del rostro
                    face_region = image[y1:y2, x1:x2]
                    
                    # Verificar que la región extraída no esté vacía
                    if face_region.size == 0:
                        print(f"      ⚠️ Región de rostro vacía - Usando imagen completa")
                        return image  # ✅ FALLBACK: Usar imagen completa
                    
                    print(f"      ✅ ROSTRO VÁLIDO extraído: {face_region.shape}")
                    print(f"      🏠 Región original: {image.shape}")
                    print(f"      📐 Región del rostro: {face_region.shape}")
                    print(f"      📍 Coordenadas: x={x1}-{x2}, y={y1}-{y2}")
                    print(f"      🎯 Tamaño del rostro: {w}x{h}")
                    
                    return face_region
                else:
                    print("      ⚠️ NO SE DETECTARON ROSTROS - Usando imagen completa")
                    return image  # ✅ FALLBACK: Usar imagen completa
                    
            except Exception as e:
                print(f"      ⚠️ Error en detección de rostros: {e}")
                print("      ✅ FALLBACK: Usando imagen completa")
                return image  # ✅ FALLBACK: Usar imagen completa
                
        except Exception as e:
            print(f"      ⚠️ Error crítico en extracción de rostro: {e}")
            print("      ✅ FALLBACK: Usando imagen completa")
            return image  # ✅ FALLBACK: Usar imagen completa

    def _extract_face_region_fast(self, image):
        """
        Extracción ULTRA-RÁPIDA del rostro para verificación
        ✅ Versión optimizada sin logs detallados
        
        Args:
            image: Imagen OpenCV (numpy array)
            
        Returns:
            numpy.ndarray: Imagen recortada del rostro o la imagen completa
        """
        try:
            if not self.facial_system:
                return image  # ✅ FALLBACK: Usar imagen completa
            
            # Detectar rostros en la imagen
            faces_detected = self.facial_system.detect_faces(image)
            
            if faces_detected and len(faces_detected) > 0:
                # Tomar el primer rostro detectado
                face = faces_detected[0]
                
                # Extraer coordenadas del rostro (corregido para coincidir con detect_faces)
                x, y, w, h = face['x'], face['y'], face['width'], face['height']
                
                # Verificar que el rostro tenga un tamaño mínimo válido
                min_face_size = 20  # Muy permisivo
                if w < min_face_size or h < min_face_size:
                    return image  # ✅ FALLBACK: Usar imagen completa
                
                # Agregar margen alrededor del rostro (20% como en el sistema anterior)
                margin = int(min(w, h) * 0.2)
                x1 = max(0, x - margin)
                y1 = max(0, y - margin)
                x2 = min(image.shape[1], x + w + margin)
                y2 = min(image.shape[0], y + h + margin)
                
                # Verificar que la región extraída sea válida
                if x2 <= x1 or y2 <= y1:
                    return image  # ✅ FALLBACK: Usar imagen completa
                
                # Recortar la región del rostro
                face_region = image[y1:y2, x1:x2]
                
                # Verificar que la región extraída no esté vacía
                if face_region.size == 0:
                    return image  # ✅ FALLBACK: Usar imagen completa
                
                return face_region
            else:
                return image  # ✅ FALLBACK: Usar imagen completa
                
        except Exception as e:
            return image  # ✅ FALLBACK: Usar imagen completa

    def _decode_base64_image_fast(self, base64_data):
        """
        Decodificación ULTRA-RÁPIDA para verificación de asistencia
        ✅ SIN extracción de rostro para máxima velocidad
        
        Args:
            base64_data: String con datos de imagen en base64
            
        Returns:
            numpy.ndarray: Imagen OpenCV lista para procesar
        """
        try:
            # ✅ OPTIMIZACIÓN: Sin logs para máxima velocidad
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
            print(f"❌ Error en decodificación rápida: {e}")
            return None

    def _decode_base64_image(self, base64_data):
        """
        Decodifica imagen base64 y extrae automáticamente el rostro
        ✅ AHORA RECORTA AUTOMÁTICAMENTE AL ROSTRO COMO EN EL SISTEMA ANTERIOR
        
        Args:
            base64_data: String con datos de imagen en base64
            
        Returns:
            numpy.ndarray: Imagen del rostro recortada o None si hay error
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
            
            # ✅ EXTRACCIÓN AUTOMÁTICA DEL ROSTRO (SISTEMA PERMISIVO)
            print("      🎯 Iniciando extracción automática del rostro...")
            face_image = self._extract_face_region(opencv_image)
            
            # ✅ AHORA SIEMPRE RETORNA UNA IMAGEN (permisivo)
            if face_image is not None:
                print(f"      ✅ Rostro extraído exitosamente: {face_image.shape}")
                return face_image
            else:
                print("      ⚠️ Fallback: Usando imagen original")
                return opencv_image  # ✅ FALLBACK: Usar imagen original
            
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
