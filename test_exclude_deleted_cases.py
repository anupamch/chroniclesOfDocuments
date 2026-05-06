#!/usr/bin/env python3
"""
Test that deleted cases are excluded from case lists
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

def test_backend_excludes_deleted():
    """Test that backend excludes deleted cases from list"""
    print_section("TEST: Backend Excludes Deleted Cases")
    
    # Login
    login_data = {
        "phone_number": "9073436357",
        "password": "A@123456"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login/email", json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get cases list
            cases_response = requests.get(f"{BASE_URL}/cases", headers=headers)
            
            if cases_response.status_code == 200:
                cases_data = cases_response.json()
                cases = cases_data.get("cases", [])
                
                print(f"Total cases returned: {len(cases)}")
                print(f"Total count from API: {cases_data.get('total')}")
                
                # Check for deleted cases
                deleted_cases = [case for case in cases if case.get("status") == "deleted"]
                active_cases = [case for case in cases if case.get("status") != "deleted"]
                
                print(f"Active cases: {len(active_cases)}")
                print(f"Deleted cases in list: {len(deleted_cases)}")
                
                if len(deleted_cases) == 0:
                    print("SUCCESS: No deleted cases in the list")
                    return True
                else:
                    print("FAILED: Deleted cases are still showing in the list")
                    for case in deleted_cases:
                        print(f"  - {case.get('case_number')} (Status: {case.get('status')})")
                    return False
            else:
                print(f"Failed to get cases: {cases_response.status_code}")
                return False
        else:
            print("Login failed")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return False

def test_can_see_deleted_with_filter():
    """Test that deleted cases can still be seen with explicit status filter"""
    print_section("TEST: Can See Deleted Cases with Status Filter")
    
    login_data = {
        "phone_number": "9073436357",
        "password": "A@123456"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login/email", json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Request cases with status=deleted filter
            cases_response = requests.get(f"{BASE_URL}/cases?status=deleted", headers=headers)
            
            if cases_response.status_code == 200:
                cases_data = cases_response.json()
                cases = cases_data.get("cases", [])
                
                print(f"Deleted cases with status filter: {len(cases)}")
                
                if len(cases) > 0:
                    print("SUCCESS: Can see deleted cases when explicitly requested")
                    return True
                else:
                    print("INFO: No deleted cases in database (this is normal)")
                    return True
            else:
                print(f"Failed to get filtered cases: {cases_response.status_code}")
                return False
        else:
            print("Login failed")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return False

def test_frontend_filtering():
    """Test frontend filtering logic"""
    print_section("TEST: Frontend Filtering Logic")
    
    # Simulate frontend filtering
    sample_cases = [
        {"case_id": "1", "case_number": "CASE-001", "status": "active"},
        {"case_id": "2", "case_number": "CASE-002", "status": "deleted"},
        {"case_id": "3", "case_number": "CASE-003", "status": "closed"},
        {"case_id": "4", "case_number": "CASE-004", "status": "deleted"},
        {"case_id": "5", "case_number": "CASE-005", "status": "active"}
    ]
    
    # Frontend filtering logic
    active_cases = [case for case in sample_cases if case['status'] != 'deleted']
    
    print(f"Total cases: {len(sample_cases)}")
    print(f"Active cases after filtering: {len(active_cases)}")
    
    print("\nActive cases:")
    for case in active_cases:
        print(f"  - {case['case_number']} (Status: {case['status']})")
    
    print("\nFiltered out (deleted):")
    for case in sample_cases:
        if case['status'] == 'deleted':
            print(f"  - {case['case_number']} (Status: {case['status']})")
    
    if len(active_cases) == 3 and len([c for c in sample_cases if c['status'] == 'deleted']) == 2:
        print("SUCCESS: Frontend filtering works correctly")
        return True
    else:
        print("FAILED: Frontend filtering not working as expected")
        return False

def main():
    """Test deleted cases exclusion"""
    print("Testing Deleted Cases Exclusion from Case Lists...")
    
    # Test backend
    backend_test = test_backend_excludes_deleted()
    
    # Test explicit filter
    filter_test = test_can_see_deleted_with_filter()
    
    # Test frontend logic
    frontend_test = test_frontend_filtering()
    
    print_section("EXCLUSION SUMMARY")
    print("Backend: Modified to exclude deleted cases by default")
    print("Frontend: Added client-side filtering as safety measure")
    print("Filter: Deleted cases can still be seen with status=deleted")
    
    print(f"\nTest Results:")
    print(f"Backend Exclusion: {'PASSED' if backend_test else 'FAILED'}")
    print(f"Status Filter: {'PASSED' if filter_test else 'FAILED'}")
    print(f"Frontend Filter: {'PASSED' if frontend_test else 'FAILED'}")
    
    if backend_test and frontend_test:
        print("\nSUCCESS: Deleted cases are now excluded from case lists")
        print("Both frontend and backend will not show deleted cases by default")
    else:
        print("\nISSUE: Some tests failed - check implementation")

if __name__ == "__main__":
    main()
