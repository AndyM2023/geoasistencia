import cv2
import os

def capture_photo():
    """Capturar una foto con la cámara"""
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara")
        return None
    
    print("📸 Presiona 'ESPACIO' para capturar, 'ESC' para salir")
    
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
            # Crear directorio temp_photos si no existe
            os.makedirs("temp_photos", exist_ok=True)
            
            # Generar nombre único para la foto
            timestamp = cv2.getTickCount()
            photo_path = f"temp_photos/capture_{timestamp}.jpg"
            
            # Guardar foto
            cv2.imwrite(photo_path, frame)
            print(f"✅ Foto guardada: {photo_path}")
            
            # Preguntar si quiere probarla
            test_choice = input("¿Quieres probar esta foto en el sistema? (s/n): ").strip().lower()
            if test_choice == 's':
                return photo_path
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return None

if __name__ == "__main__":
    print("📷 CAPTURADOR DE FOTOS SIMPLE")
    print("=" * 40)
    
    photo_path = capture_photo()
    
    if photo_path:
        print(f"\n🎯 Foto capturada: {photo_path}")
        print("💡 Ahora puedes usar esta foto para:")
        print("   - Registrar una nueva persona")
        print("   - Probar identificación")
        print("   - Ejecutar: python advanced_face_system.py")
    else:
        print("\n👋 No se capturó ninguna foto")
