#!/usr/bin/env python3
"""
Script de prueba para verificar los endpoints del dashboard del empleado
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/app/auth/employee_login/"
EMPLOYEE_INFO_URL = f"{BASE_URL}/app/dashboard/employee_info/"
EMPLOYEE_STATS_URL = f"{BASE_URL}/app/dashboard/employee_stats/"
EMPLOYEE_ATTENDANCES_URL = f"{BASE_URL}/app/dashboard/employee_attendances/"

def test_employee_endpoints():
    """Probar los endpoints del dashboard del empleado"""
    
    print("🧪 Probando endpoints del dashboard del empleado...")
    print("=" * 60)
    
    # 1. Intentar login con un empleado existente
    print("\n1️⃣ Probando login...")
    login_data = {
        "username": "lmendieta",  # Usuario que existe en la base de datos
        "password": "test123"  # Contraseña por defecto
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get('token')
            if token:
                print("   ✅ Login exitoso, token obtenido")
                headers = {'Authorization': f'Bearer {token}'}
            else:
                print("   ❌ No se pudo obtener el token")
                return
        else:
            print(f"   ❌ Error en login: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return
    
    # 2. Probar endpoint employee_info
    print("\n2️⃣ Probando /dashboard/employee_info/...")
    try:
        response = requests.get(EMPLOYEE_INFO_URL, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Datos del empleado obtenidos:")
            print(f"      - Nombre: {data.get('fullName', 'N/A')}")
            print(f"      - ID: {data.get('employeeId', 'N/A')}")
            print(f"      - Cargo: {data.get('position', 'N/A')}")
            print(f"      - Área: {data.get('area', 'N/A')}")
            print(f"      - Fecha contratación: {data.get('hireDate', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 3. Probar endpoint employee_stats
    print("\n3️⃣ Probando /dashboard/employee_stats/...")
    try:
        response = requests.get(EMPLOYEE_STATS_URL, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Estadísticas del empleado obtenidas:")
            print(f"      - Días trabajados: {data.get('totalDays', 'N/A')}")
            print(f"      - Días a tiempo: {data.get('onTimeDays', 'N/A')}")
            print(f"      - Días tarde: {data.get('lateDays', 'N/A')}")
            print(f"      - Tasa asistencia: {data.get('attendanceRate', 'N/A')}%")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 4. Probar endpoint employee_attendances
    print("\n4️⃣ Probando /dashboard/employee_attendances/...")
    try:
        response = requests.get(EMPLOYEE_ATTENDANCES_URL, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            attendances = data.get('attendances', [])
            print(f"   ✅ Historial de asistencias obtenido:")
            print(f"      - Total de asistencias: {len(attendances)}")
            
            if attendances:
                print("      - Últimas 3 asistencias:")
                for i, attendance in enumerate(attendances[:3]):
                    print(f"        {i+1}. {attendance.get('date', 'N/A')} - "
                          f"Entrada: {attendance.get('check_in', 'N/A')} - "
                          f"Salida: {attendance.get('check_out', 'N/A')}")
            else:
                print("      - No hay asistencias registradas")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Prueba completada")

if __name__ == "__main__":
    test_employee_endpoints()
