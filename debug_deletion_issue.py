#!/usr/bin/env python3
"""
Comprehensive debugging for mobile case deletion issues
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    """Print section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def print_response(response):
    """Pretty print response"""
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print()

def test_authentication():
    """Test authentication and token handling"""
    print_section("TEST: Authentication")
    
    login_data = {
        "phone_number": "9073436357",
        "password": "A@123456"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login/email", json=login_data)
        
        print_response(login_response)
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print(f"Token extracted: {token[:50]}..." if token else "No token")
            return token
        else:
            print("Authentication failed")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None

def test_case_access_rights(token):
    """Test if user has access to delete cases"""
    print_section("TEST: Case Access Rights")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get list of cases
    try:
        cases_response = requests.get(f"{BASE_URL}/cases", headers=headers)
        
        if cases_response.status_code == 200:
            cases = cases_response.json().get("cases", [])
            print(f"Found {len(cases)} cases:")
            
            for i, case in enumerate(cases[:3]):  # Test first 3 cases
                case_id = case.get("case_id")
                case_number = case.get("case_number")
                status = case.get("status")
                print(f"\nCase {i+1}: {case_number} ({case_id[:8]}...) - Status: {status}")
                
                # Test access to this specific case
                case_detail_response = requests.get(f"{BASE_URL}/cases/{case_id}", headers=headers)
                print(f"Access check: {case_detail_response.status_code}")
                
                if case_detail_response.status_code == 200:
                    print("PASS User has access to this case")
                    
                    # Test deletion on this case
                    print("Testing deletion...")
                    delete_response = requests.delete(f"{BASE_URL}/cases/{case_id}", headers=headers)
                    print(f"Delete response: {delete_response.status_code}")
                    
                    if delete_response.status_code == 200:
                        print("PASS Deletion successful")
                        return True
                    else:
                        try:
                            error_data = delete_response.json()
                            print(f"FAIL Deletion failed: {error_data}")
                        except:
                            print(f"FAIL Deletion failed: {delete_response.text}")
                else:
                    print("FAIL User does not have access to this case")
        else:
            print(f"Failed to get cases: {cases_response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
    
    return False

def test_delete_with_different_cases(token):
    """Test deletion with different case scenarios"""
    print_section("TEST: Different Deletion Scenarios")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    scenarios = [
        {
            "name": "Delete active case",
            "create_data": {
                "case_number": f"ACTIVE-DELETE-{int(time.time())}",
                "title": "Active Case for Deletion",
                "description": "This case will be deleted while active"
            }
        },
        {
            "name": "Delete case with documents",
            "create_data": {
                "case_number": f"DOC-DELETE-{int(time.time())}",
                "title": "Case with Documents",
                "description": "This case will have documents before deletion"
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        
        try:
            # Create case
            create_response = requests.post(f"{BASE_URL}/cases", json=scenario["create_data"], headers=headers)
            
            if create_response.status_code == 201:
                case_info = create_response.json()
                case_id = case_info.get("case_id")
                print(f"Created case: {case_id[:8]}...")
                
                # For the document scenario, we would need to upload documents, but let's skip that for now
                
                # Delete the case
                delete_response = requests.delete(f"{BASE_URL}/cases/{case_id}", headers=headers)
                
                print(f"Delete status: {delete_response.status_code}")
                print(f"Delete response: {delete_response.text}")
                
                if delete_response.status_code == 200:
                    print("PASS Success")
                else:
                    print("FAIL Failed")
            else:
                print(f"Failed to create case: {create_response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Error in scenario: {e}")

def test_raw_delete_request():
    """Test raw delete request to see exact behavior"""
    print_section("TEST: Raw Delete Request")
    
    token = test_authentication()
    if not token:
        print("Cannot proceed without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test case
    case_data = {
        "case_number": f"RAW-TEST-{int(time.time())}",
        "title": "Raw Test Case",
        "description": "Testing raw delete"
    }
    
    try:
        create_response = requests.post(f"{BASE_URL}/cases", json=case_data, headers=headers)
        
        if create_response.status_code == 201:
            case_id = create_response.json().get("case_id")
            print(f"Test case ID: {case_id}")
            
            # Make raw delete request with detailed logging
            print(f"\nMaking DELETE request to: {BASE_URL}/cases/{case_id}")
            print(f"Headers: {headers}")
            
            delete_response = requests.delete(
                f"{BASE_URL}/cases/{case_id}",
                headers=headers,
                timeout=30  # Add timeout
            )
            
            print(f"\nRaw delete response:")
            print(f"Status Code: {delete_response.status_code}")
            print(f"Status Text: {delete_response.reason}")
            print(f"Headers: {dict(delete_response.headers)}")
            print(f"Response Body: {delete_response.text}")
            print(f"Response Time: {delete_response.elapsed}")
            
            # Check if response is properly closed
            print(f"Connection closed: {delete_response.raw.closed}")
            
        else:
            print(f"Failed to create test case: {create_response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Raw request error: {e}")
        print(f"Error type: {type(e)}")

def main():
    """Run comprehensive deletion debugging"""
    print("Comprehensive Mobile Case Deletion Debugging...")
    
    # Test authentication
    token = test_authentication()
    if not token:
        print("Cannot proceed without authentication")
        return
    
    # Test case access rights
    access_test = test_case_access_rights(token)
    
    # Test different scenarios
    test_delete_with_different_cases(token)
    
    # Test raw request
    test_raw_delete_request()
    
    print_section("DEBUGGING SUMMARY")
    print("If deletion still fails, check these items:")
    print("1. Mobile app network configuration (LOCAL_IP)")
    print("2. WebSocket connections interfering with HTTP requests")
    print("3. Mobile app error handling and logging")
    print("4. React Native debugger console for detailed errors")
    print("5. Backend logs for any errors during deletion")

if __name__ == "__main__":
    main()
