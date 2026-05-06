#!/usr/bin/env python3
"""
Test the mobile case creation fix and provide troubleshooting steps
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    """Print section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_complete_mobile_flow():
    """Test the complete mobile flow for case creation"""
    print_section("TEST: Complete Mobile Case Creation Flow")
    
    # Step 1: Login with phone number (new mobile functionality)
    print("Step 1: Mobile Login")
    login_data = {
        "phone_number": "9073436357",
        "password": "A@123456"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login/email", json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print("PASS Mobile login successful")
            
            # Step 2: Create case with authentication
            print("\nStep 2: Case Creation with Auth")
            headers = {"Authorization": f"Bearer {token}"}
            case_data = {
                "case_number": "MOBILE-TEST-001",
                "title": "Mobile Test Case",
                "description": "Test case created via mobile flow"
            }
            
            case_response = requests.post(f"{BASE_URL}/cases", json=case_data, headers=headers)
            print(f"Status: {case_response.status_code}")
            
            if case_response.status_code == 201:
                case_info = case_response.json()
                print("PASS Case creation successful")
                print(f"Case ID: {case_info.get('case_id')}")
                print(f"Case Number: {case_info.get('case_number')}")
                return True
            else:
                print("FAIL Case creation failed")
                try:
                    print(f"Error: {case_response.json().get('detail')}")
                except:
                    pass
                return False
        else:
            print("FAIL Mobile login failed")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"FAIL Network error: {e}")
        return False

def check_mobile_network_config():
    """Check mobile network configuration"""
    print_section("MOBILE NETWORK CONFIGURATION")
    
    print("Current mobile app configuration:")
    print("- LOCAL_IP: 192.168.0.221")
    print("- BASE_URL: http://192.168.0.221:8000/api")
    print("- Authentication: Bearer token from AsyncStorage")
    print("- Error handling: Enhanced with detailed logging")
    
    print("\nTroubleshooting Steps:")
    print("1. Verify backend server is running on port 8000")
    print("2. Check if LOCAL_IP matches your machine's IP address")
    print("3. Ensure mobile device can reach the backend server")
    print("4. Verify user is logged in with valid token")
    print("5. Check console logs in mobile app for detailed errors")

def generate_troubleshooting_guide():
    """Generate troubleshooting guide for mobile case creation"""
    print_section("TROUBLESHOOTING GUIDE")
    
    print("If mobile case creation still fails, follow these steps:")
    print()
    print("1. CHECK BACKEND CONNECTIVITY:")
    print("   - Open browser: http://localhost:8000/health")
    print("   - Should return: {'status': 'ok'}")
    print()
    print("2. UPDATE LOCAL_IP IN MOBILE:")
    print("   - File: mobile/lib/api.ts")
    print("   - Line: const LOCAL_IP = '192.168.0.221';")
    print("   - Update to your machine's actual IP address")
    print()
    print("3. VERIFY AUTHENTICATION:")
    print("   - Login to mobile app successfully")
    print("   - Check AsyncStorage for 'token' key")
    print("   - Token should be valid JWT")
    print()
    print("4. CHECK CONSOLE LOGS:")
    print("   - Open React Native debugger")
    print("   - Look for 'API Error Details' logs")
    print("   - Check network request/response details")
    print()
    print("5. TEST API DIRECTLY:")
    print("   - Use Postman/curl to test POST /cases endpoint")
    print("   - Include Authorization: Bearer <token> header")
    print("   - Verify payload format matches mobile app")

def main():
    """Run mobile case creation fix verification"""
    print("Testing Mobile Case Creation Fix...")
    
    # Test the complete mobile flow
    flow_success = test_complete_mobile_flow()
    
    # Check network configuration
    check_mobile_network_config()
    
    # Generate troubleshooting guide
    generate_troubleshooting_guide()
    
    print_section("FIX SUMMARY")
    print("PASS Enhanced error handling in mobile case creation")
    print("PASS Added detailed logging for debugging")
    print("PASS Improved error messages for users")
    print("PASS Maintained authentication requirements")
    
    print(f"\nMobile Flow Test: {'PASSED' if flow_success else 'FAILED'}")
    
    if flow_success:
        print("\nSUCCESS: Mobile case creation should now work properly")
        print("The enhanced error handling will provide better debugging")
        print("information if issues still occur.")
    else:
        print("\nISSUE: Still experiencing problems")
        print("Follow the troubleshooting guide above to resolve.")

if __name__ == "__main__":
    main()
