#!/usr/bin/env python3
"""
Test script to debug employee update API
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/employees/21/"

# Test data - minimal update
test_data = {
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "cedula": "1234567890",
    "position": "desarrollador",
    "area": 1,  # Assuming area ID 1 exists
    "photo": None
}

print(f"🔍 Testing employee update API")
print(f"URL: {API_URL}")
print(f"Data: {json.dumps(test_data, indent=2)}")

try:
    # First, get the current employee data
    print("\n📥 Getting current employee data...")
    response = requests.get(API_URL)
    print(f"GET Response Status: {response.status_code}")
    if response.status_code == 200:
        current_data = response.json()
        print(f"Current employee data: {json.dumps(current_data, indent=2)}")
    else:
        print(f"GET Error: {response.text}")
        exit(1)
    
    # Now try to update
    print("\n📤 Attempting update...")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_TOKEN_HERE'  # You'll need to get a valid token
    }
    
    response = requests.put(API_URL, json=test_data, headers=headers)
    print(f"PUT Response Status: {response.status_code}")
    print(f"PUT Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("✅ Update successful!")
        print(f"Response: {response.text}")
    else:
        print(f"❌ Update failed with status {response.status_code}")
        print(f"Response: {response.text}")
        
        # Try to parse error details
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            print("Could not parse error response as JSON")
            
except requests.exceptions.RequestException as e:
    print(f"❌ Request error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
