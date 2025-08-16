"""
Singleton para el servicio de reconocimiento facial
Se inicializa una sola vez y se reutiliza para todas las consultas
"""

from .face_service import FaceRecognitionService
import os
import sys

class FaceServiceSingleton:
    """Singleton para el servicio de reconocimiento facial"""
    
    _instance = None
    _service = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FaceServiceSingleton, cls).__new__(cls)
            # Inicializar el servicio solo una vez
            print("🚀 Inicializando servicio facial singleton...")
            cls._service = cls._create_service()
            print("✅ Servicio facial singleton inicializado")
        return cls._instance
    
    @classmethod
    def _create_service(cls):
        """Crear el servicio facial con manejo de errores robusto"""
        try:
            # Verificar que el directorio de reconocimiento facial existe
            face_recognition_dir = os.path.join(os.getcwd(), 'face_recognition')
            if not os.path.exists(face_recognition_dir):
                print(f"❌ Directorio de reconocimiento facial no encontrado: {face_recognition_dir}")
                return None
            
            # Agregar el directorio al path si no está
            if face_recognition_dir not in sys.path:
                sys.path.insert(0, face_recognition_dir)
                print(f"✅ Directorio agregado al path: {face_recognition_dir}")
            
            # Intentar importar el sistema facial
            try:
                from advanced_face_system import FacialRecognition
                print(f"✅ FacialRecognition importado correctamente")
            except ImportError as e:
                print(f"❌ Error importando FacialRecognition: {e}")
                return None
            
            # Crear el servicio
            service = FaceRecognitionService()
            
            # Verificar que el servicio se creó correctamente
            if service and hasattr(service, 'facial_system') and service.facial_system:
                print(f"✅ Servicio facial creado exitosamente")
                return service
            else:
                print(f"❌ Servicio facial no se creó correctamente")
                return None
                
        except Exception as e:
            print(f"❌ Error creando servicio facial: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_service(self):
        """Obtiene la instancia del servicio facial, reinicializa si es necesario"""
        # Verificar si el servicio está disponible
        if not self._service or not hasattr(self._service, 'facial_system') or not self._service.facial_system:
            print("⚠️ Servicio facial no disponible, intentando reinicializar...")
            self._service = self._create_service()
            
            if not self._service or not hasattr(self._service, 'facial_system') or not self._service.facial_system:
                print("❌ No se pudo reinicializar el servicio facial")
                return None
        
        return self._service
    
    def get_employee_face_status(self, employee):
        """Obtiene el estado del perfil facial del empleado"""
        service = self.get_service()
        if not service:
            return {
                'success': False,
                'message': 'Sistema de reconocimiento facial no disponible'
            }
        return service.get_employee_face_status(employee)
    
    def verify_face(self, employee, photo):
        """Verifica un rostro para asistencia"""
        service = self.get_service()
        if not service:
            return {
                'success': False,
                'message': 'Sistema de reconocimiento facial no disponible'
            }
        return service.verify_face(employee, photo)
    
    def register_face(self, employee, photos_base64):
        """Registra o actualiza rostros de un empleado"""
        service = self.get_service()
        if not service:
            return {
                'success': False,
                'message': 'Sistema de reconocimiento facial no disponible'
            }
        
        result = service.register_employee_face(employee, photos_base64)
        # Después del registro/actualización, refrescar el caché del sistema facial
        self.refresh_facial_system()
        return result
    
    def refresh_facial_system(self):
        """Refresca el sistema facial para sincronizar cambios"""
        service = self.get_service()
        if service and hasattr(service, 'facial_system') and service.facial_system:
            try:
                print("🔄 Refrescando sistema facial...")
                # El sistema facial se refresca automáticamente al listar personas
                result = service.facial_system.list_all_persons()
                if result.get('success'):
                    print(f"✅ Sistema facial refrescado: {result.get('total_persons', 0)} personas")
                else:
                    print(f"⚠️ Error refrescando sistema facial: {result.get('error')}")
            except Exception as e:
                print(f"⚠️ Error en refresh: {e}")

# Instancia global del singleton
face_service_singleton = FaceServiceSingleton()
