#!/usr/bin/env python3
"""
Debug the case creation 400 errors
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    """Print section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def debug_case_creation():
    """Debug case creation issues"""
    print_section("DEBUG: Case Creation Issues")
    
    # Login first
    login_data = {
        "phone_number": "9073436357",
        "password": "A@123456"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login/email", json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            print("Login successful")
            
            # Test with a unique case number
            import time
            timestamp = int(time.time())
            unique_case_number = f"DEBUG-{timestamp}"
            
            case_data = {
                "case_number": unique_case_number,
                "title": "Debug Test Case",
                "description": "Testing case creation"
            }
            
            print(f"Creating case with unique number: {unique_case_number}")
            print(f"Request data: {json.dumps(case_data, indent=2)}")
            
            response = requests.post(f"{BASE_URL}/cases", json=case_data, headers=headers)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 201:
                print("SUCCESS: Case created successfully")
                return True
            else:
                print("FAILED: Case creation failed")
                return False
        else:
            print(f"Login failed: {login_response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return False

def check_existing_cases():
    """Check what cases already exist"""
    print_section("CHECK: Existing Cases")
    
    login_data = {
        "phone_number": "9073436357",
        "password": "A@123456"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login/email", json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.get(f"{BASE_URL}/cases", headers=headers)
            
            if response.status_code == 200:
                cases = response.json().get("cases", [])
                print(f"Found {len(cases)} existing cases:")
                
                for case in cases:
                    print(f"  - {case.get('case_number')} (Status: {case.get('status')})")
                
                # Check for the test case numbers we tried
                test_numbers = ["VALID-CASE-001", "VALID_CASE_002", "VALIDCASE003"]
                existing_numbers = [case.get('case_number') for case in cases]
                
                print(f"\nChecking for conflicts with test cases:")
                for test_num in test_numbers:
                    if test_num in existing_numbers:
                        print(f"  CONFLICT: '{test_num}' already exists")
                    else:
                        print(f"  OK: '{test_num}' not found")
                
                return True
            else:
                print(f"Failed to get cases: {response.status_code}")
                return False
        else:
            print("Login failed")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return False

def main():
    """Debug case creation issues"""
    print("Debugging Mobile Case Creation Issues...")
    
    # Check existing cases
    check_existing_cases()
    
    # Try creating a unique case
    debug_result = debug_case_creation()
    
    print_section("DEBUG SUMMARY")
    if debug_result:
        print("Case creation works with unique case numbers")
        print("The 400 errors were likely due to duplicate case numbers")
    else:
        print("Case creation still has issues - investigate further")

if __name__ == "__main__":
    main()
