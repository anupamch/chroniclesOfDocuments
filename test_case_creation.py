#!/usr/bin/env python3
"""
Test case creation API to debug mobile app error
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    """Print section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def print_response(response):
    """Pretty print response"""
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print()

def test_case_creation_endpoint():
    """Test the case creation API endpoint"""
    print_section("TEST: Case Creation API Endpoint")
    
    # Test data similar to mobile app
    case_data = {
        "case_number": "TEST-2024-001",
        "title": "Test Case for Mobile Debug",
        "description": "This is a test case created to debug mobile app issues"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/cases", json=case_data)
        print_response(response)
        
        if response.status_code == 200:
            print("SUCCESS: Case creation works")
            return True
        else:
            print("FAILED: Case creation failed")
            return False
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Connection failed - {e}")
        return False

def test_case_creation_with_auth():
    """Test case creation with authentication"""
    print_section("TEST: Case Creation with Authentication")
    
    # First login to get token
    login_data = {
        "email": "suchitrasengupta.91@gmail.com",
        "password": "A@123456"
    }
    
    try:
        # Login
        login_response = requests.post(f"{BASE_URL}/auth/login/email", json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print(f"Login successful, got token")
            
            # Create case with auth
            headers = {"Authorization": f"Bearer {token}"}
            case_data = {
                "case_number": "AUTH-TEST-001",
                "title": "Authenticated Test Case",
                "description": "Test case with authentication"
            }
            
            case_response = requests.post(f"{BASE_URL}/cases", json=case_data, headers=headers)
            print_response(case_response)
            
            return case_response.status_code == 200
        else:
            print(f"Login failed: {login_response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Auth test failed - {e}")
        return False

def test_backend_health():
    """Test if backend is running"""
    print_section("TEST: Backend Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS: Backend is running")
            return True
        else:
            print("ISSUE: Backend returned unexpected status")
            return False
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Cannot connect to backend - {e}")
        return False

def analyze_mobile_error():
    """Analyze the mobile app error pattern"""
    print_section("ANALYSIS: Mobile Error Pattern")
    
    print("Error Details:")
    print("- Type: AxiosError")
    print("- Context: Create case operation")
    print("- Stack: Network request failure")
    print("\nPossible Causes:")
    print("1. Backend server not running")
    print("2. Network connectivity issues")
    print("3. Authentication token missing/invalid")
    print("4. API endpoint not accessible")
    print("5. CORS or network policy issues")
    print("6. Request payload format issues")
    
    print("\nMobile App Configuration:")
    print("- Uses LOCAL_IP: 192.168.0.221:8000")
    print("- Requires authentication token")
    print("- Makes POST request to /cases endpoint")

def main():
    """Run case creation debugging tests"""
    print("Debugging Mobile Case Creation Error...")
    
    # Test backend connectivity
    backend_ok = test_backend_health()
    
    if not backend_ok:
        print("\nISSUE: Backend server is not accessible")
        print("Please ensure the backend server is running on port 8000")
        return
    
    # Test case creation without auth
    no_auth_test = test_case_creation_endpoint()
    
    # Test case creation with auth
    auth_test = test_case_creation_with_auth()
    
    # Analyze the error
    analyze_mobile_error()
    
    print_section("DEBUGGING SUMMARY")
    print(f"Backend Health: {'OK' if backend_ok else 'FAILED'}")
    print(f"Case Creation (No Auth): {'WORKS' if no_auth_test else 'FAILED'}")
    print(f"Case Creation (With Auth): {'WORKS' if auth_test else 'FAILED'}")
    
    if not auth_test:
        print("\nRECOMMENDATIONS:")
        print("1. Ensure backend server is running")
        print("2. Check mobile app network configuration")
        print("3. Verify authentication token in mobile app")
        print("4. Update LOCAL_IP in mobile/lib/api.ts if needed")
        print("5. Check if user is logged in properly in mobile app")
    else:
        print("\nSUCCESS: Case creation API is working")

if __name__ == "__main__":
    main()
