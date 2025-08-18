#!/usr/bin/env python
"""
Script para detectar múltiples peticiones al endpoint de recuperación de contraseña
"""

import os
import django
import time
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoproject.settings')
django.setup()

from core.models import PasswordResetToken

def check_multiple_requests():
    """Verificar si hay múltiples tokens creados para el mismo usuario"""
    print("🔍 VERIFICANDO MÚLTIPLES PETICIONES")
    print("=" * 50)
    
    try:
        # Buscar todos los tokens activos
        active_tokens = PasswordResetToken.objects.filter(is_used=False).order_by('-created_at')
        
        print(f"📊 Tokens activos encontrados: {active_tokens.count()}")
        
        if active_tokens.count() > 0:
            print("\n📋 DETALLE DE TOKENS:")
            for i, token in enumerate(active_tokens):
                print(f"   {i+1}. Usuario: {token.user.username}")
                print(f"      Email: {token.user.email}")
                print(f"      Token: {token.token[:20]}...")
                print(f"      Creado: {token.created_at}")
                print(f"      Expira: {token.expires_at}")
                print(f"      Usado: {token.is_used}")
                print()
        
        # Verificar si hay múltiples tokens para el mismo usuario
        from django.db.models import Count
        user_token_counts = PasswordResetToken.objects.filter(
            is_used=False
        ).values('user__username').annotate(
            token_count=Count('id')
        ).filter(token_count__gt=1)
        
        if user_token_counts.exists():
            print("⚠️  PROBLEMA DETECTADO: Múltiples tokens para el mismo usuario")
            for item in user_token_counts:
                username = item['user__username']
                count = item['token_count']
                print(f"   - Usuario {username}: {count} tokens activos")
                
                # Mostrar tokens duplicados
                user_tokens = PasswordResetToken.objects.filter(
                    user__username=username,
                    is_used=False
                ).order_by('-created_at')
                
                for token in user_tokens:
                    print(f"     * Token {token.token[:20]}... creado: {token.created_at}")
        else:
            print("✅ No hay tokens duplicados")
        
        # Limpiar tokens duplicados si los hay
        if user_token_counts.exists():
            print("\n🧹 LIMPIANDO TOKENS DUPLICADOS...")
            for item in user_token_counts:
                username = item['user__username']
                count = item['token_count']
                
                # Mantener solo el token más reciente
                user_tokens = PasswordResetToken.objects.filter(
                    user__username=username,
                    is_used=False
                ).order_by('-created_at')
                
                # Eliminar todos excepto el más reciente
                tokens_to_delete = user_tokens[1:]
                for token in tokens_to_delete:
                    print(f"   Eliminando token {token.token[:20]}... para {username}")
                    token.delete()
                
                print(f"   ✅ Se mantuvieron {count - len(tokens_to_delete)} token(s) para {username}")
        
    except Exception as e:
        print(f"❌ Error verificando tokens: {e}")
        import traceback
        traceback.print_exc()

def monitor_requests():
    """Monitorear peticiones en tiempo real"""
    print("\n🔍 MONITOREANDO PETICIONES EN TIEMPO REAL")
    print("=" * 50)
    print("   Ejecuta este script y luego haz clic en 'ENVIAR INSTRUCCIONES' desde el frontend")
    print("   Presiona Ctrl+C para detener el monitoreo")
    print()
    
    try:
        initial_count = PasswordResetToken.objects.filter(is_used=False).count()
        print(f"📊 Tokens activos iniciales: {initial_count}")
        
        while True:
            time.sleep(1)
            current_count = PasswordResetToken.objects.filter(is_used=False).count()
            
            if current_count != initial_count:
                print(f"🔄 CAMBIO DETECTADO: {initial_count} → {current_count} tokens")
                
                # Mostrar tokens nuevos
                new_tokens = PasswordResetToken.objects.filter(
                    is_used=False
                ).order_by('-created_at')[:current_count - initial_count]
                
                for token in new_tokens:
                    print(f"   📧 Nuevo token para {token.user.username}: {token.token[:20]}...")
                    print(f"      Creado: {token.created_at}")
                
                initial_count = current_count
            
    except KeyboardInterrupt:
        print("\n✅ Monitoreo detenido")

if __name__ == '__main__':
    print("🔍 DIAGNÓSTICO DE MÚLTIPLES PETICIONES")
    print("=" * 60)
    
    # Verificar estado actual
    check_multiple_requests()
    
    # Preguntar si quiere monitorear en tiempo real
    print("\n¿Quieres monitorear las peticiones en tiempo real? (s/n): ", end="")
    response = input().lower().strip()
    
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        monitor_requests()
    else:
        print("✅ Verificación completada")

