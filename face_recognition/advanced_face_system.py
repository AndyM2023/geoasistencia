import cv2
import numpy as np
import os
import time
import shutil
from deepface import DeepFace

class FacialRecognition:
    def __init__(self, base_dir=None, database_name="faces"):
        """
        Inicializa el sistema de reconocimiento facial genérico
        
        Args:
            base_dir: Directorio base donde se guardarán los rostros
            database_name: Nombre de la carpeta para la base de datos de rostros
        """
        if base_dir is None:
            base_dir = os.path.abspath(os.path.dirname(__file__))
        
        self.base_dir = base_dir
        self.face_dir = os.path.join(base_dir, database_name)
        
        # Crear directorio de rostros si no existe
        if not os.path.exists(self.face_dir):
            os.makedirs(self.face_dir)
        
        # Pre-cargar modelos de DeepFace
        self._preload_models()
    
    def _preload_models(self):
        """Pre-carga los modelos de DeepFace para evitar demoras"""
        print("Inicializando modelos de DeepFace...")
        dummy_image = np.ones((224, 224, 3), dtype=np.uint8) * 128
        try:
            DeepFace.extract_faces(dummy_image, detector_backend='retinaface', enforce_detection=False)
            DeepFace.represent(dummy_image, model_name="Facenet", detector_backend='retinaface', enforce_detection=False)
            print("✅ Modelos de DeepFace cargados correctamente")
        except Exception as e:
            print(f"⚠ Advertencia al pre-cargar modelos: {e}")
    
    def detect_faces(self, image):
        """
        Detecta rostros en una imagen usando RetinaFace
        
        Args:
            image: Imagen en formato numpy array (BGR)
            
        Returns:
            Lista de diccionarios con coordenadas de rostros detectados
        """
        try:
            faces = DeepFace.extract_faces(
                image, 
                detector_backend='retinaface',
                align=False,
                enforce_detection=True
            )
            face_list = []
            for face in faces:
                facial_area = face['facial_area']
                face_list.append({
                    'x': facial_area['x'],
                    'y': facial_area['y'],
                    'width': facial_area['w'],
                    'height': facial_area['h']
                })
            return face_list
        except Exception as e:
            print(f"Error en detección facial: {e}")
            return []
    
    def extract_face_features(self, face_image):
        """
        Extrae características (embeddings) de un rostro usando Facenet
        
        Args:
            face_image: Imagen del rostro en formato numpy array
            
        Returns:
            Array numpy con las características del rostro o None si hay error
        """
        try:
            embedding = DeepFace.represent(
                face_image,
                model_name="Facenet",
                detector_backend='skip',
                enforce_detection=False
            )
            return embedding[0]['embedding']
        except Exception as e:
            print(f"Error extrayendo características: {e}")
            return None
    
    def compare_faces(self, features1, features2):
        """
        Compara dos rostros basándose en sus características
        
        Args:
            features1: Características del primer rostro
            features2: Características del segundo rostro
            
        Returns:
            Valor de similitud entre 0.0 y 1.0 (1.0 = idénticos)
        """
        if features1 is None or features2 is None:
            return 0.0
        try:
            # Calcular similitud usando coseno
            distance = np.dot(features1, features2) / (np.linalg.norm(features1) * np.linalg.norm(features2))
            similarity = (distance + 1) / 2
            return float(similarity)
        except:
            return 0.0
    
    def save_face_features(self, person_folder, face_image):
        """
        Guarda un rostro y sus características
        
        Args:
            person_folder: Carpeta de la persona
            face_image: Imagen del rostro
            
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            features = self.extract_face_features(face_image)
            if features is None:
                return False
            
            timestamp = int(time.time() * 1000)
            face_filename = f"{timestamp}.jpg"
            face_path = os.path.join(person_folder, face_filename)
            cv2.imwrite(face_path, face_image)
            
            features_filename = f"{timestamp}.npy"
            features_path = os.path.join(person_folder, features_filename)
            np.save(features_path, features)
            
            print(f"Guardado: {face_filename} y {features_filename}")
            return True
        except Exception as e:
            print(f"Error al guardar características: {e}")
            return False
    
    def register_person(self, person_id, person_name, image, max_faces=50):
        """
        Registra rostros de una persona
        
        Args:
            person_id: ID único de la persona
            person_name: Nombre de la persona
            image: Imagen que contiene rostros
            max_faces: Máximo número de rostros a guardar
            
        Returns:
            Diccionario con información del registro
        """
        try:
            # Crear nombre de carpeta
            folder_name = f"{person_id}{person_name.replace(' ', '')}"
            folder_path = os.path.join(self.face_dir, folder_name)
            
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            # Detectar rostros
            faces = self.detect_faces(image)
            existing_images = len([f for f in os.listdir(folder_path) if f.endswith('.jpg') and not f.startswith('full_')])
            saved_faces = 0
            
            for i, face_info in enumerate(faces):
                if existing_images + saved_faces >= max_faces:
                    break
                
                # Extraer rostro con margen
                x, y, w, h = face_info['x'], face_info['y'], face_info['width'], face_info['height']
                margin = 20
                x_start = max(0, x - margin)
                y_start = max(0, y - margin)
                x_end = min(image.shape[1], x + w + margin)
                y_end = min(image.shape[0], y + h + margin)
                face_image = image[y_start:y_end, x_start:x_end]
                
                if face_image.size > 0:
                    if self.save_face_features(folder_path, face_image):
                        saved_faces += 1
            
            total_images = existing_images + saved_faces
            return {
                'success': True, 
                'message': f'Se guardaron {saved_faces} rostros. Total: {total_images}/{max_faces}',
                'faces_detected': len(faces),
                'faces_saved': saved_faces,
                'total_images': total_images
            }
            
        except Exception as e:
            print(f"Error en el registro facial: {e}")
            return {'success': False, 'error': str(e)}
    
    def identify_person(self, image, similarity_threshold=0.8):
        """
        Identifica una persona comparando su rostro con la base de datos
        
        Args:
            image: Imagen que contiene el rostro a identificar
            similarity_threshold: Umbral mínimo de similitud para considerar una coincidencia
            
        Returns:
            Diccionario con información de identificación
        """
        try:
            # Detectar rostros
            faces = self.detect_faces(image)
            if not faces:
                return {
                    'success': True,
                    'person_identified': None,
                    'similarity': 0.0
                }
            
            # Extraer características del rostro detectado
            x, y, w, h = faces[0]['x'], faces[0]['y'], faces[0]['width'], faces[0]['height']
            margin = 20
            x_start = max(0, x - margin)
            y_start = max(0, y - margin)
            x_end = min(image.shape[1], x + w + margin)
            y_end = min(image.shape[0], y + h + margin)
            face_image = image[y_start:y_end, x_start:x_end]
            
            if face_image.size == 0:
                return {'success': False, 'error': 'Error al extraer el rostro'}
            
            # Extraer características
            features = self.extract_face_features(face_image)
            if features is None:
                return {'success': False, 'error': 'Error al extraer características faciales'}
            
            # Buscar coincidencias
            best_match_id = None
            best_match_name = None
            best_similarity = 0.0
            
            for folder in os.listdir(self.face_dir):
                folder_path = os.path.join(self.face_dir, folder)
                if not os.path.isdir(folder_path):
                    continue
                
                # Extraer ID y nombre del nombre de la carpeta
                person_id = ''.join(filter(str.isdigit, folder.split('_')[0] if '_' in folder else folder))
                person_name = folder[len(person_id):]
                
                for file in os.listdir(folder_path):
                    if not file.endswith('.npy'):
                        continue
                    
                    features_path = os.path.join(folder_path, file)
                    stored_features = np.load(features_path)
                    similarity = self.compare_faces(features, stored_features)
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match_id = person_id
                        best_match_name = person_name
            
            if best_similarity > similarity_threshold:
                return {
                    'success': True,
                    'person_identified': {
                        'id': best_match_id,
                        'name': best_match_name
                    },
                    'similarity': float(best_similarity)
                }
            else:
                return {
                    'success': True,
                    'person_identified': None,
                    'similarity': float(best_similarity)
                }
                
        except Exception as e:
            print(f"Error en la identificación facial: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_person_faces(self, person_id):
        """
        Elimina todos los rostros de una persona
        
        Args:
            person_id: ID de la persona cuyos rostros se eliminarán
            
        Returns:
            Diccionario con resultado de la eliminación
        """
        try:
            print(f"🗑️ Intentando eliminar datos faciales para persona: {person_id}")
            
            # Buscar la carpeta de la persona
            person_folder = None
            for folder in os.listdir(self.face_dir):
                if folder.startswith(str(person_id)):
                    person_folder = os.path.join(self.face_dir, folder)
                    print(f"📁 Carpeta encontrada: {person_folder}")
                    break
            
            if not person_folder:
                print(f"❌ No se encontró la carpeta para la persona {person_id}")
                return {
                    'success': False,
                    'error': 'No se encontró la carpeta de rostros para esta persona'
                }
            
            # Eliminar la carpeta y todo su contenido
            try:
                shutil.rmtree(person_folder)
                print(f"✅ Carpeta eliminada exitosamente: {person_folder}")
            except Exception as e:
                print(f"❌ Error al eliminar carpeta: {e}")
                return {
                    'success': False,
                    'error': f'Error al eliminar carpeta: {str(e)}'
                }
            
            return {
                'success': True,
                'message': 'Datos faciales eliminados correctamente'
            }
            
        except Exception as e:
            print(f"❌ Error al eliminar datos faciales: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_person_info(self, person_id):
        """
        Obtiene información sobre los rostros registrados de una persona
        
        Args:
            person_id: ID de la persona
            
        Returns:
            Diccionario con información de la persona
        """
        try:
            # Buscar la carpeta de la persona
            person_folder = None
            for folder in os.listdir(self.face_dir):
                if folder.startswith(str(person_id)):
                    person_folder = os.path.join(self.face_dir, folder)
                    break
            
            if not person_folder:
                return {
                    'success': False,
                    'error': 'Persona no encontrada'
                }
            
            # Contar archivos
            jpg_files = [f for f in os.listdir(person_folder) if f.endswith('.jpg') and not f.startswith('full_')]
            npy_files = [f for f in os.listdir(person_folder) if f.endswith('.npy')]
            
            return {
                'success': True,
                'person_id': person_id,
                'person_name': folder[len(str(person_id)):],
                'total_faces': len(jpg_files),
                'total_features': len(npy_files),
                'folder_path': person_folder
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_all_persons(self):
        """
        Lista todas las personas registradas
        
        Returns:
            Lista de diccionarios con información de personas
        """
        try:
            persons = []
            for folder in os.listdir(self.face_dir):
                folder_path = os.path.join(self.face_dir, folder)
                if not os.path.isdir(folder_path):
                    continue
                
                # Extraer ID y nombre
                person_id = ''.join(filter(str.isdigit, folder.split('_')[0] if '_' in folder else folder))
                person_name = folder[len(person_id):]
                
                # Contar archivos
                jpg_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg') and not f.startswith('full_')]
                npy_files = [f for f in os.listdir(folder_path) if f.endswith('.npy')]
                
                persons.append({
                    'id': person_id,
                    'name': person_name,
                    'total_faces': len(jpg_files),
                    'total_features': len(npy_files),
                    'folder_path': folder_path
                })
            
            return {
                'success': True,
                'persons': persons,
                'total_persons': len(persons)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_face_count(self):
        """
        Obtiene el número total de rostros en la base de datos
        
        Returns:
            Número total de rostros
        """
        try:
            total_faces = 0
            for folder in os.listdir(self.face_dir):
                folder_path = os.path.join(self.face_dir, folder)
                if os.path.isdir(folder_path):
                    jpg_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg') and not f.startswith('full_')]
                    total_faces += len(jpg_files)
            return total_faces
        except Exception as e:
            print(f"Error contando rostros: {e}")
            return 0
    
    def clear_database(self):
        """
        Elimina toda la base de datos de rostros
        
        Returns:
            Diccionario con resultado de la limpieza
        """
        try:
            print("🗑️ Eliminando toda la base de datos de rostros...")
            if os.path.exists(self.face_dir):
                shutil.rmtree(self.face_dir)
                os.makedirs(self.face_dir)
                print("✅ Base de datos limpiada correctamente")
                return {
                    'success': True,
                    'message': 'Base de datos limpiada correctamente'
                }
            else:
                return {
                    'success': False,
                    'error': 'La base de datos no existe'
                }
        except Exception as e:
            print(f"❌ Error limpiando base de datos: {e}")
            return {
                'success': False,
                'error': str(e)
            }

def capture_from_camera():
    """Captura imagen desde la cámara"""
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara")
        return None
    
    print("📸 Presiona 'ESPACIO' para capturar, 'ESC' para cancelar")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Mostrar frame
        cv2.imshow('Cámara - Presiona ESPACIO para capturar', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            break
        elif key == 32:  # ESPACIO
            print("✅ Foto capturada")
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return frame if 'frame' in locals() else None

def main():
    """Función principal del sistema"""
    print("🎯 SISTEMA DE RECONOCIMIENTO FACIAL AVANZADO")
    print("=" * 60)
    
    # Inicializar sistema
    fr = FacialRecognition()
    
    while True:
        print("\n" + "="*60)
        print("🎯 MENÚ PRINCIPAL")
        print("="*60)
        print("1. Registrar nueva persona (cámara)")
        print("2. Identificar persona (cámara)")
        print("3. Listar personas registradas")
        print("4. Información de persona específica")
        print("5. Eliminar persona")
        print("6. Estadísticas de la base de datos")
        print("7. Limpiar base de datos")
        print("8. Salir")
        print("-"*60)
        
        choice = input("Selecciona una opción: ").strip()
        
        if choice == "1":
            print("\n📝 REGISTRO DE NUEVA PERSONA")
            print("-" * 40)
            person_id = input("ID de la persona: ").strip()
            person_name = input("Nombre de la persona: ").strip()
            
            print("\n📸 Preparando cámara...")
            image = capture_from_camera()
            
            if image is not None:
                result = fr.register_person(person_id, person_name, image)
                if result['success']:
                    print(f"✅ {result['message']}")
                else:
                    print(f"❌ Error: {result['error']}")
            else:
                print("❌ No se capturó ninguna imagen")
        
        elif choice == "2":
            print("\n🔍 IDENTIFICACIÓN DE PERSONA")
            print("-" * 40)
            print("📸 Preparando cámara...")
            
            image = capture_from_camera()
            
            if image is not None:
                result = fr.identify_person(image, similarity_threshold=0.8)
                if result['success']:
                    if result['person_identified']:
                        person = result['person_identified']
                        similarity = result['similarity']
                        print(f"✅ Persona identificada:")
                        print(f"   ID: {person['id']}")
                        print(f"   Nombre: {person['name']}")
                        print(f"   Similitud: {similarity:.2%}")
                    else:
                        print(f"❌ No se identificó a la persona (Similitud: {result['similarity']:.2%})")
                else:
                    print(f"❌ Error: {result['error']}")
            else:
                print("❌ No se capturó ninguna imagen")
        
        elif choice == "3":
            print("\n📋 LISTADO DE PERSONAS REGISTRADAS")
            print("-" * 40)
            result = fr.list_all_persons()
            if result['success']:
                if result['total_persons'] > 0:
                    for person in result['persons']:
                        print(f"👤 ID: {person['id']} | Nombre: {person['name']}")
                        print(f"   Rostros: {person['total_faces']} | Características: {person['total_features']}")
                        print()
                else:
                    print("📝 No hay personas registradas")
            else:
                print(f"❌ Error: {result['error']}")
        
        elif choice == "4":
            print("\nℹ️ INFORMACIÓN DE PERSONA ESPECÍFICA")
            print("-" * 40)
            person_id = input("ID de la persona: ").strip()
            result = fr.get_person_info(person_id)
            if result['success']:
                print(f"👤 ID: {result['person_id']}")
                print(f"   Nombre: {result['person_name']}")
                print(f"   Total rostros: {result['total_faces']}")
                print(f"   Total características: {result['total_features']}")
            else:
                print(f"❌ Error: {result['error']}")
        
        elif choice == "5":
            print("\n🗑️ ELIMINAR PERSONA")
            print("-" * 40)
            person_id = input("ID de la persona a eliminar: ").strip()
            confirm = input(f"¿Estás seguro de eliminar a la persona {person_id}? (s/n): ").strip().lower()
            
            if confirm == 's':
                result = fr.delete_person_faces(person_id)
                if result['success']:
                    print(f"✅ {result['message']}")
                else:
                    print(f"❌ Error: {result['error']}")
            else:
                print("❌ Operación cancelada")
        
        elif choice == "6":
            print("\n📊 ESTADÍSTICAS DE LA BASE DE DATOS")
            print("-" * 40)
            total_faces = fr.get_face_count()
            list_result = fr.list_all_persons()
            
            if list_result['success']:
                print(f"👥 Total de personas: {list_result['total_persons']}")
                print(f"📸 Total de rostros: {total_faces}")
            else:
                print(f"❌ Error obteniendo estadísticas: {list_result['error']}")
        
        elif choice == "7":
            print("\n🧹 LIMPIAR BASE DE DATOS")
            print("-" * 40)
            confirm = input("¿Estás seguro de eliminar TODA la base de datos? (s/n): ").strip().lower()
            
            if confirm == 's':
                result = fr.clear_database()
                if result['success']:
                    print(f"✅ {result['message']}")
                else:
                    print(f"❌ Error: {result['error']}")
            else:
                print("❌ Operación cancelada")
        
        elif choice == "8":
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    main()
