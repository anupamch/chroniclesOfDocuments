# Authentication - Phone Number & Email Login Guide

## Overview

Your backend now supports login with:
- ✅ **Email only** - Traditional email login
- ✅ **Phone number only** - Phone number based login
- ✅ **Flexible identifier** - Auto-detect email or phone number
- ✅ **OAuth2 (Original)** - Standard OAuth2 form data

---

## 🔐 Login Endpoints

### 1. Login with Email
```http
POST /api/auth/login/email
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Response (Success - 200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Response (Error - 401):**
```json
{
  "detail": "Incorrect email or password"
}
```

---

### 2. Login with Phone Number
```http
POST /api/auth/login/phone
Content-Type: application/json

{
  "phone_number": "+1234567890",
  "password": "your_password"
}
```

**Response (Success - 200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Response (Error - 401):**
```json
{
  "detail": "Incorrect phone number or password"
}
```

---

### 3. Login with Email OR Phone (Flexible)
```http
POST /api/auth/login/flexible
Content-Type: application/json

{
  "identifier": "user@example.com",
  "password": "your_password"
}
```

**Or with phone:**
```http
POST /api/auth/login/flexible
Content-Type: application/json

{
  "identifier": "+1234567890",
  "password": "your_password"
}
```

**Response (Success - 200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 4. OAuth2 Standard Login (Original)
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=your_password
```

---

## 📝 Registration

### Register with Email and Phone
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password_123",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "role": "customer"
}
```

**Response (Success - 200):**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "role": "customer",
  "is_active": true,
  "is_deleted": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Note:** Phone number is optional during registration but must be unique if provided.

---

## 🧪 Testing with cURL

### Test Email Login
```bash
curl -X POST "http://localhost:8000/api/auth/login/email" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password"
  }'
```

### Test Phone Login
```bash
curl -X POST "http://localhost:8000/api/auth/login/phone" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "password": "your_password"
  }'
```

### Test Flexible Login (with email)
```bash
curl -X POST "http://localhost:8000/api/auth/login/flexible" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "user@example.com",
    "password": "your_password"
  }'
```

### Test Flexible Login (with phone)
```bash
curl -X POST "http://localhost:8000/api/auth/login/flexible" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "+1234567890",
    "password": "your_password"
  }'
```

---

## 🐍 Testing with Python

### Using Python Requests Library
```python
import requests

# Test email login
response = requests.post(
    "http://localhost:8000/api/auth/login/email",
    json={
        "email": "user@example.com",
        "password": "your_password"
    }
)

if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"Login successful! Token: {token}")
else:
    print(f"Login failed: {response.json()['detail']}")

# Test phone login
response = requests.post(
    "http://localhost:8000/api/auth/login/phone",
    json={
        "phone_number": "+1234567890",
        "password": "your_password"
    }
)

# Test flexible login
response = requests.post(
    "http://localhost:8000/api/auth/login/flexible",
    json={
        "identifier": "user@example.com",  # Or "+1234567890"
        "password": "your_password"
    }
)
```

---

## 🧪 Testing with Postman

### Email Login Request
1. Method: `POST`
2. URL: `http://localhost:8000/api/auth/login/email`
3. Headers: `Content-Type: application/json`
4. Body (JSON):
```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

### Phone Login Request
1. Method: `POST`
2. URL: `http://localhost:8000/api/auth/login/phone`
3. Headers: `Content-Type: application/json`
4. Body (JSON):
```json
{
  "phone_number": "+1234567890",
  "password": "your_password"
}
```

### Flexible Login Request
1. Method: `POST`
2. URL: `http://localhost:8000/api/auth/login/flexible`
3. Headers: `Content-Type: application/json`
4. Body (JSON):
```json
{
  "identifier": "user@example.com",
  "password": "your_password"
}
```

---

## 🔄 Using the Access Token

After login, use the token in subsequent requests:

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Or with Python:
```python
headers = {
    "Authorization": f"Bearer {token}"
}

response = requests.get(
    "http://localhost:8000/api/auth/me",
    headers=headers
)

print(response.json())
```

---

## 💻 Frontend Integration

### React Example
```typescript
// Login with email
async function loginWithEmail(email: string, password: string) {
  const response = await fetch("/api/auth/login/email", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem("token", data.access_token);
    return data;
  } else {
    throw new Error("Login failed");
  }
}

// Login with phone
async function loginWithPhone(phone_number: string, password: string) {
  const response = await fetch("/api/auth/login/phone", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone_number, password })
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem("token", data.access_token);
    return data;
  }
}

// Login with flexible identifier
async function loginFlexible(identifier: string, password: string) {
  const response = await fetch("/api/auth/login/flexible", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ identifier, password })
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem("token", data.access_token);
    return data;
  }
}
```

---

## 🎯 Which Endpoint to Use?

| Scenario | Endpoint | Best For |
|----------|----------|----------|
| Email-only app | `/login/email` | Traditional email login |
| Phone-only app | `/login/phone` | SMS/phone-based signup |
| Both supported | `/login/flexible` | Maximum flexibility |
| OAuth2 clients | `/login` | Legacy/standard OAuth2 |

---

## 🔒 Security Best Practices

1. **Always use HTTPS** - Never send credentials over HTTP
2. **Store tokens securely** - Use httpOnly cookies or secure local storage
3. **Token expiration** - Tokens expire based on `access_token_expire_minutes` setting
4. **Refresh tokens** - Consider implementing refresh tokens for extended sessions
5. **Rate limiting** - Add rate limiting to prevent brute force attacks
6. **Password validation** - Enforce strong password requirements during registration

---

## 📊 Database Schema

### Users Collection
```javascript
{
  "_id": ObjectId,
  "user_id": UUID,
  "email": String (unique, required),
  "phone_number": String (unique, optional),
  "full_name": String,
  "hashed_password": String,
  "role": String,
  "is_active": Boolean,
  "is_deleted": Boolean,
  "created_at": DateTime,
  "updated_at": DateTime
}
```

### Recommended Indexes
```javascript
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "phone_number": 1 }, { unique: true, sparse: true });
db.users.createIndex({ "user_id": 1 }, { unique: true });
```

---

## ⚙️ Configuration

### Environment Variables
```env
# Token expiration in minutes
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days
```

### Settings
```python
# From app/core/config.py
access_token_expire_minutes: int = 60 * 24 * 7  # 1 week
```

---

## 🚀 API Reference

### Updated Schemas

#### LoginRequest
```python
{
  "identifier": "user@example.com or +1234567890",  # Email or phone
  "password": "password123"
}
```

#### LoginEmailRequest
```python
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### LoginPhoneRequest
```python
{
  "phone_number": "+1234567890",
  "password": "password123"
}
```

#### Token Response
```python
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 🔧 Implementation Details

### UserService Methods

#### Get by Email
```python
user = await UserService.get_by_email("user@example.com")
```

#### Get by Phone
```python
user = await UserService.get_by_phone("+1234567890")
```

#### Get by Email or Phone
```python
user = await UserService.get_by_email_or_phone("user@example.com or +1234567890")
```

#### Create User (with phone validation)
```python
user = await UserService.create_user(UserCreate(
    email="user@example.com",
    phone_number="+1234567890",
    password="password123",
    full_name="John Doe"
))
```

---

## ✅ Features

✅ Login with email
✅ Login with phone number  
✅ Flexible login (auto-detect email or phone)
✅ Phone number uniqueness validation
✅ Phone number optional during registration
✅ All original OAuth2 functionality preserved
✅ Consistent error messages
✅ Token-based authentication
✅ User session management

---

## 📌 Error Handling

### Common Errors

| Status | Error | Cause | Solution |
|--------|-------|-------|----------|
| 401 | Incorrect email or password | Wrong credentials | Verify email and password |
| 401 | Incorrect phone or password | Wrong credentials | Verify phone and password |
| 400 | User already exists | Duplicate email or phone | Use different email/phone |
| 400 | Inactive user | Account disabled | Contact admin |
| 400 | User not found | No account exists | Create account first |

---

## 🎓 Next Steps

1. **Test locally** - Use the curl/Postman examples above
2. **Implement in frontend** - Use the React example as guide
3. **Add rate limiting** - Prevent brute force attacks
4. **Implement refresh tokens** - For better UX
5. **Add SMS verification** - For phone-based signup
6. **Add email verification** - For email-based signup

---

## 📞 Support

For issues or questions about authentication:
1. Check database indexes are created
2. Verify .env configuration
3. Check MongoDB is running
4. Review error messages in API response
5. Check backend logs for detailed errors

---

## Summary

Your backend now supports flexible authentication with:
- **Email login**: `/api/auth/login/email`
- **Phone login**: `/api/auth/login/phone`
- **Flexible login**: `/api/auth/login/flexible` (auto-detect)
- **Original OAuth2**: `/api/auth/login` (unchanged)

All endpoints return JWT tokens for stateless authentication!
