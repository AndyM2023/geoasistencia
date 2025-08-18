#!/usr/bin/env python
"""
Script para identificar y corregir usuarios duplicados
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import User
from django.db.models import Count

def find_duplicate_users():
    """Encontrar usuarios duplicados por email"""
    print("🔍 BUSCANDO USUARIOS DUPLICADOS")
    print("=" * 50)
    
    try:
        # Buscar usuarios duplicados por email
        duplicate_emails = User.objects.values('email').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if duplicate_emails.exists():
            print(f"⚠️  SE ENCONTRARON {duplicate_emails.count()} EMAILS DUPLICADOS:")
            
            for item in duplicate_emails:
                email = item['email']
                count = item['count']
                print(f"\n📧 Email: {email} ({count} usuarios)")
                
                # Mostrar usuarios con este email
                users_with_email = User.objects.filter(email=email).order_by('date_joined')
                
                for i, user in enumerate(users_with_email):
                    print(f"   {i+1}. Usuario: {user.username}")
                    print(f"      ID: {user.id}")
                    print(f"      Fecha de registro: {user.date_joined}")
                    print(f"      Último login: {user.last_login}")
                    print(f"      Activo: {user.is_active}")
                    print(f"      Rol: {user.role}")
                    
                    # Marcar el primero como principal
                    if i == 0:
                        print(f"      ✅ PRINCIPAL (se mantiene)")
                    else:
                        print(f"      ❌ DUPLICADO (se eliminará)")
            
            return duplicate_emails
        else:
            print("✅ No se encontraron usuarios duplicados")
            return None
            
    except Exception as e:
        print(f"❌ Error buscando duplicados: {e}")
        import traceback
        traceback.print_exc()
        return None

def fix_duplicate_users():
    """Corregir usuarios duplicados manteniendo solo el más antiguo"""
    print("\n🔧 CORRIGIENDO USUARIOS DUPLICADOS")
    print("=" * 50)
    
    try:
        duplicate_emails = find_duplicate_users()
        
        if not duplicate_emails:
            print("✅ No hay usuarios duplicados para corregir")
            return
        
        print(f"\n🧹 PROCEDIENDO A LIMPIAR DUPLICADOS...")
        
        for item in duplicate_emails:
            email = item['email']
            count = item['count']
            
            print(f"\n📧 Procesando email: {email}")
            
            # Obtener usuarios con este email ordenados por fecha de registro
            users_with_email = User.objects.filter(email=email).order_by('date_joined')
            
            # Mantener el usuario más antiguo (primero)
            user_to_keep = users_with_email.first()
            users_to_delete = users_with_email[1:]
            
            print(f"   ✅ Manteniendo: {user_to_keep.username} (ID: {user_to_keep.id})")
            print(f"   ❌ Eliminando: {users_to_delete.count()} usuario(s) duplicado(s)")
            
            # Eliminar usuarios duplicados
            for user in users_to_delete:
                print(f"      - Eliminando: {user.username} (ID: {user.id})")
                user.delete()
            
            print(f"   ✅ Email {email} limpiado correctamente")
        
        print(f"\n🎉 LIMPIEZA COMPLETADA")
        
        # Verificar que no queden duplicados
        remaining_duplicates = User.objects.values('email').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if remaining_duplicates.exists():
            print(f"⚠️  Aún quedan {remaining_duplicates.count()} emails duplicados")
        else:
            print("✅ Todos los usuarios duplicados han sido eliminados")
            
    except Exception as e:
        print(f"❌ Error corrigiendo duplicados: {e}")
        import traceback
        traceback.print_exc()

def show_user_summary():
    """Mostrar resumen de usuarios en la base de datos"""
    print("\n📊 RESUMEN DE USUARIOS EN LA BASE DE DATOS")
    print("=" * 50)
    
    try:
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        admin_users = User.objects.filter(role='admin').count()
        
        print(f"👥 Total de usuarios: {total_users}")
        print(f"✅ Usuarios activos: {active_users}")
        print(f"🔐 Usuarios administradores: {admin_users}")
        
        # Mostrar usuarios por email
        print(f"\n📧 USUARIOS POR EMAIL:")
        email_counts = User.objects.values('email').annotate(
            count=Count('id')
        ).order_by('-count')
        
        for item in email_counts:
            email = item['email']
            count = item['count']
            if count > 1:
                print(f"   ⚠️  {email}: {count} usuarios (DUPLICADO)")
            else:
                print(f"   ✅ {email}: {count} usuario")
                
    except Exception as e:
        print(f"❌ Error mostrando resumen: {e}")

if __name__ == '__main__':
    print("🔧 HERRAMIENTA DE LIMPIEZA DE USUARIOS DUPLICADOS")
    print("=" * 60)
    
    # Mostrar estado actual
    show_user_summary()
    
    # Buscar duplicados
    duplicates = find_duplicate_users()
    
    if duplicates:
        print(f"\n¿Quieres corregir los {duplicates.count()} usuarios duplicados? (s/n): ", end="")
        response = input().lower().strip()
        
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            fix_duplicate_users()
            
            # Mostrar estado después de la limpieza
            print("\n" + "=" * 60)
            show_user_summary()
        else:
            print("❌ No se realizaron cambios")
    else:
        print("\n✅ No hay usuarios duplicados para corregir")
    
    print("\n" + "=" * 60)
    print("✅ PROCESO COMPLETADO")
