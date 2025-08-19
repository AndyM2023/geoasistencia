#!/usr/bin/env python3
"""
Script de migración para renombrar carpetas de rostros
de la estructura antigua (ID+nombre) a la nueva (solo ID)

Este script:
1. Busca todas las carpetas en face_recognition/faces/
2. Identifica las que siguen el patrón antiguo (ej: 6joseperez)
3. Las renombra al nuevo patrón (ej: 6)
4. Mantiene un log de la migración
"""

import os
import re
import shutil
import sys
from datetime import datetime

def setup_django():
    """Configurar Django para acceder a los modelos"""
    import django
    import os
    
    # Agregar el directorio del proyecto al path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
    django.setup()

def get_employee_info(employee_id):
    """Obtener información del empleado desde la base de datos"""
    try:
        from core.models import Employee
        employee = Employee.objects.get(employee_id=employee_id)
        return {
            'id': employee.id,
            'employee_id': employee.employee_id,
            'name': f"{employee.user.first_name} {employee.user.last_name}",
            'email': employee.user.email
        }
    except Employee.DoesNotExist:
        return None

def migrate_face_folders():
    """Migrar carpetas de rostros de la estructura antigua a la nueva"""
    
    # Configurar Django
    setup_django()
    
    # Ruta base del sistema facial
    base_dir = os.path.dirname(os.path.abspath(__file__))
    faces_dir = os.path.join(base_dir, 'face_recognition', 'faces')
    
    if not os.path.exists(faces_dir):
        print(f"❌ Directorio de rostros no encontrado: {faces_dir}")
        return
    
    print(f"🔍 Iniciando migración de carpetas de rostros...")
    print(f"📁 Directorio base: {faces_dir}")
    
    # Crear archivo de log
    log_file = f"face_migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    log_path = os.path.join(base_dir, log_file)
    
    with open(log_path, 'w', encoding='utf-8') as log:
        log.write(f"Migración de carpetas de rostros - {datetime.now()}\n")
        log.write(f"Directorio base: {faces_dir}\n")
        log.write("=" * 80 + "\n\n")
        
        # Obtener todas las carpetas
        folders = [f for f in os.listdir(faces_dir) if os.path.isdir(os.path.join(faces_dir, f))]
        
        print(f"📊 Total de carpetas encontradas: {len(folders)}")
        log.write(f"Total de carpetas encontradas: {len(folders)}\n\n")
        
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        for folder in folders:
            try:
                # Verificar si es una carpeta antigua (ID+nombre)
                old_pattern = re.match(r'^(\d+)([a-zA-Z]+)$', folder)
                
                if old_pattern:
                    employee_id = old_pattern.group(1)
                    old_name = old_pattern.group(2)
                    new_folder = employee_id
                    
                    old_path = os.path.join(faces_dir, folder)
                    new_path = os.path.join(faces_dir, new_folder)
                    
                    # Verificar si ya existe la nueva carpeta
                    if os.path.exists(new_path):
                        print(f"⚠️  Ya existe carpeta {new_folder}, saltando {folder}")
                        log.write(f"⚠️  Ya existe carpeta {new_folder}, saltando {folder}\n")
                        skipped_count += 1
                        continue
                    
                    # Obtener información del empleado
                    employee_info = get_employee_info(int(employee_id))
                    
                    if employee_info:
                        print(f"🔄 Migrando: {folder} → {new_folder} ({employee_info['name']})")
                        log.write(f"🔄 Migrando: {folder} → {new_folder} ({employee_info['name']})\n")
                    else:
                        print(f"🔄 Migrando: {folder} → {new_folder} (empleado no encontrado en BD)")
                        log.write(f"🔄 Migrando: {folder} → {new_folder} (empleado no encontrado en BD)\n")
                    
                    # Renombrar carpeta
                    shutil.move(old_path, new_path)
                    
                    print(f"✅ Migración exitosa: {folder} → {new_folder}")
                    log.write(f"✅ Migración exitosa: {folder} → {new_folder}\n")
                    
                    migrated_count += 1
                    
                else:
                    # Verificar si es una carpeta nueva (solo ID)
                    if re.match(r'^\d+$', folder):
                        print(f"✅ Carpeta ya migrada: {folder}")
                        log.write(f"✅ Carpeta ya migrada: {folder}\n")
                        skipped_count += 1
                    else:
                        print(f"⚠️  Carpeta con formato desconocido: {folder}")
                        log.write(f"⚠️  Carpeta con formato desconocido: {folder}\n")
                        skipped_count += 1
                        
            except Exception as e:
                print(f"❌ Error migrando {folder}: {str(e)}")
                log.write(f"❌ Error migrando {folder}: {str(e)}\n")
                error_count += 1
        
        # Resumen final
        print(f"\n🎯 RESUMEN DE MIGRACIÓN:")
        print(f"   ✅ Migradas: {migrated_count}")
        print(f"   ⏭️  Saltadas: {skipped_count}")
        print(f"   ❌ Errores: {error_count}")
        print(f"   📝 Log guardado en: {log_file}")
        
        log.write(f"\n🎯 RESUMEN DE MIGRACIÓN:\n")
        log.write(f"   ✅ Migradas: {migrated_count}\n")
        log.write(f"   ⏭️  Saltadas: {skipped_count}\n")
        log.write(f"   ❌ Errores: {error_count}\n")
        
        if migrated_count > 0:
            print(f"\n🎉 ¡Migración completada exitosamente!")
            print(f"   Las carpetas ahora usan solo el ID del empleado")
            print(f"   No más problemas de sincronización con nombres")
        else:
            print(f"\nℹ️  No se encontraron carpetas para migrar")

if __name__ == "__main__":
    try:
        migrate_face_folders()
    except Exception as e:
        print(f"❌ Error fatal en la migración: {str(e)}")
        sys.exit(1)
