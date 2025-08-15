"""
Singleton para el servicio de reconocimiento facial
Se inicializa una sola vez y se reutiliza para todas las consultas
"""

from .face_service import FaceRecognitionService

class FaceServiceSingleton:
    """Singleton para el servicio de reconocimiento facial"""
    
    _instance = None
    _service = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FaceServiceSingleton, cls).__new__(cls)
            # Inicializar el servicio solo una vez
            print("🚀 Inicializando servicio facial singleton...")
            cls._service = FaceRecognitionService()
            print("✅ Servicio facial singleton inicializado")
        return cls._instance
    
    def get_service(self):
        """Obtiene la instancia del servicio facial"""
        return self._service
    
    def get_employee_face_status(self, employee):
        """Obtiene el estado del perfil facial del empleado"""
        return self._service.get_employee_face_status(employee)
    
    def verify_face(self, employee, photo):
        """Verifica un rostro para asistencia"""
        return self._service.verify_face(employee, photo)
    
    def register_face(self, employee, photos_base64):
        """Registra o actualiza rostros de un empleado"""
        result = self._service.register_employee_face(employee, photos_base64)
        # Después del registro/actualización, refrescar el caché del sistema facial
        self.refresh_facial_system()
        return result
    
    def refresh_facial_system(self):
        """Refresca el sistema facial para sincronizar cambios"""
        if self._service and hasattr(self._service, 'facial_system') and self._service.facial_system:
            try:
                print("🔄 Refrescando sistema facial...")
                # El sistema facial se refresca automáticamente al listar personas
                result = self._service.facial_system.list_all_persons()
                if result.get('success'):
                    print(f"✅ Sistema facial refrescado: {result.get('total_persons', 0)} personas")
                else:
                    print(f"⚠️ Error refrescando sistema facial: {result.get('error')}")
            except Exception as e:
                print(f"⚠️ Error en refresh: {e}")

# Instancia global del singleton
face_service_singleton = FaceServiceSingleton()
