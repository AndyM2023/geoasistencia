from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        """
        Método que se ejecuta cuando la aplicación está lista.
        Importa las señales para que se registren automáticamente.
        """
        try:
            import core.signals
            print("✅ Señales de core registradas automáticamente")
        except Exception as e:
            print(f"⚠️ Error registrando señales: {e}")
