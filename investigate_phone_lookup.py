#!/usr/bin/env python3
"""
Investigate phone number lookup logic and database content
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

def test_flexible_login_endpoint():
    """Test using the flexible login endpoint that auto-detects email vs phone"""
    print_section("TEST: Flexible Login Endpoint")
    
    # Test with phone number
    payload = {
        "identifier": "9073436357",
        "password": "password123"
    }
    
    response = requests.post(f"{API_URL}/auth/login/flexible", json=payload)
    print("Phone login via flexible endpoint:")
    print_response(response)
    
    return response.status_code == 200

def test_phone_specific_endpoint():
    """Test using the phone-specific login endpoint"""
    print_section("TEST: Phone-Specific Login Endpoint")
    
    payload = {
        "phone_number": "9073436357",
        "password": "password123"
    }
    
    response = requests.post(f"{API_URL}/auth/login/phone", json=payload)
    print("Phone login via phone-specific endpoint:")
    print_response(response)
    
    return response.status_code == 200

def test_email_login_for_comparison():
    """Test email login to confirm it works"""
    print_section("TEST: Email Login for Comparison")
    
    # First, we need to find what email is associated with this phone
    # Let's try to create a user to see the error, then try login with different emails
    
    test_emails = [
        "test@example.com",
        "phone@example.com", 
        "user@example.com",
        "admin@example.com"
    ]
    
    for email in test_emails:
        print(f"Testing email: {email}")
        payload = {
            "email": email,
            "password": "password123"
        }
        
        response = requests.post(f"{API_URL}/auth/login/email", json=payload)
        if response.status_code == 200:
            print(f"SUCCESS with email: {email}")
            
            # Get user details to see the phone number
            token_data = response.json()
            access_token = token_data.get("access_token")
            headers = {"Authorization": f"Bearer {access_token}"}
            user_response = requests.get(f"{API_URL}/auth/me", headers=headers)
            
            print("User details:")
            print_response(user_response)
            
            user_data = user_response.json()
            stored_phone = user_data.get("phone_number")
            print(f"Stored phone number: '{stored_phone}'")
            print(f"Type: {type(stored_phone)}")
            
            return user_data
        else:
            print(f"  Failed with status: {response.status_code}")
    
    return None

def create_test_user_with_exact_phone():
    """Create a test user with the exact phone to see the stored format"""
    print_section("CREATE: Test User with Phone 9073436357")
    
    # Try to create user - if it fails, we know the format exists
    payload = {
        "email": "debug907@example.com",
        "password": "password123",
        "full_name": "Debug Phone User",
        "phone_number": "9073436357",
        "role": "customer"
    }
    
    response = requests.post(f"{API_URL}/auth/register", json=payload)
    print("Registration attempt:")
    print_response(response)
    
    if response.status_code == 200:
        print("User created successfully")
        user_data = response.json()
        print(f"Stored phone: '{user_data.get('phone_number')}'")
        return user_data
    else:
        print("User with this phone already exists")
        return None

def test_password_variations():
    """Test with different passwords in case the password is different"""
    print_section("TEST: Different Password Variations")
    
    passwords = [
        "password123",
        "password",
        "123456",
        "admin",
        "test",
        "9073436357"  # Some users use phone as password
    ]
    
    for password in passwords:
        print(f"Testing password: {password}")
        payload = {
            "phone_number": "9073436357",
            "password": password
        }
        
        response = requests.post(f"{API_URL}/auth/login/email", json=payload)
        if response.status_code == 200:
            print(f"SUCCESS with password: {password}")
            return True
        else:
            print(f"  Failed with status: {response.status_code}")
    
    return False

def main():
    """Run comprehensive phone login investigation"""
    print("Investigating phone number login issue...")
    
    # Step 1: Test different endpoints
    flexible_success = test_flexible_login_endpoint()
    phone_success = test_phone_specific_endpoint()
    
    # Step 2: Find associated email
    user_data = test_email_login_for_comparison()
    
    # Step 3: Check stored format
    create_test_user_with_exact_phone()
    
    # Step 4: Test password variations
    password_success = test_password_variations()
    
    print_section("INVESTIGATION SUMMARY")
    print(f"Flexible endpoint success: {flexible_success}")
    print(f"Phone endpoint success: {phone_success}")
    print(f"Password variation success: {password_success}")
    
    if user_data:
        print(f"Found associated user with email: {user_data.get('email')}")
        print(f"Stored phone number: '{user_data.get('phone_number')}'")

if __name__ == "__main__":
    main()
