#!/usr/bin/env python3
"""
Create a debug endpoint to check phone number storage format
"""
import requests
import json

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

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

def test_create_user_with_various_formats():
    """Create users with different phone formats to see how they're stored"""
    print_section("TEST: Create Users with Different Phone Formats")
    
    phone_formats = [
        ("9073436357", "plain"),
        ("+9073436357", "with_plus"),
        ("+919073436357", "india_format"),
        (" 9073436357 ", "with_spaces"),
        ("(907) 343-6357", "us_format")
    ]
    
    for phone, description in phone_formats:
        print(f"Testing format: {description} - '{phone}'")
        
        # Try to create user
        payload = {
            "email": f"test_{description}@example.com",
            "password": "password123",
            "full_name": f"Test {description}",
            "phone_number": phone,
            "role": "customer"
        }
        
        response = requests.post(f"{API_URL}/auth/register", json=payload)
        
        if response.status_code == 200:
            user_data = response.json()
            stored_phone = user_data.get('phone_number')
            print(f"  SUCCESS - Stored as: '{stored_phone}'")
            
            # Test login with the stored format
            login_payload = {
                "phone_number": stored_phone,
                "password": "password123"
            }
            login_response = requests.post(f"{API_URL}/auth/login/email", json=login_payload)
            print(f"  Login with stored format: {login_response.status_code}")
            
        else:
            error_detail = response.json().get("detail", "")
            print(f"  FAILED: {error_detail}")
        
        print()

def test_exact_phone_lookup():
    """Test the exact phone number that's causing issues"""
    print_section("TEST: Exact Phone Number Lookup")
    
    # Try to create a user with the exact phone to see the error
    payload = {
        "email": "exact_test@example.com",
        "password": "password123",
        "full_name": "Exact Phone Test",
        "phone_number": "9073436357",
        "role": "customer"
    }
    
    response = requests.post(f"{API_URL}/auth/register", json=payload)
    print("Registration attempt with exact phone:")
    print_response(response)
    
    if response.status_code == 400:
        print("Phone number already exists. The issue is likely:")
        print("1. The password is different than expected")
        print("2. The phone number is stored with different formatting")
        print("3. The user account is inactive or deleted")

def test_list_all_users_to_find_phone():
    """Try to list users to find the one with this phone"""
    print_section("TEST: List Users to Find Phone")
    
    # Try to get all users (this might not work due to auth)
    try:
        # First try to login as admin
        admin_payload = {
            "email": "admin@example.com",
            "password": "admin123"
        }
        
        admin_response = requests.post(f"{API_URL}/auth/login/email", json=admin_payload)
        if admin_response.status_code == 200:
            token = admin_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try to list users (if endpoint exists)
            list_response = requests.get(f"{API_URL}/users", headers=headers)
            print("List users response:")
            print_response(list_response)
        else:
            print("Admin login failed")
    except Exception as e:
        print(f"Error listing users: {e}")

def main():
    """Run phone format debugging"""
    print("Debugging phone number storage and lookup...")
    
    test_create_user_with_various_formats()
    test_exact_phone_lookup()
    test_list_all_users_to_find_phone()
    
    print_section("DEBUGGING CONCLUSION")
    print("If phone login fails but registration says phone exists:")
    print("1. Check the exact format stored in database")
    print("2. Verify the correct password")
    print("3. Check if user is active (not soft-deleted)")
    print("4. Look for leading/trailing spaces or special characters")

if __name__ == "__main__":
    main()
