# API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## Endpoints

### Authentication

#### Register New User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}

Response: 201 Created
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "role": "user",
  "is_active": true,
  "created_at": "2026-01-13T10:00:00"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=username&password=password123

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### Users

#### Get Current User Info
```http
GET /users/me
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "role": "user",
  "is_active": true,
  "created_at": "2026-01-13T10:00:00",
  "current_plan": "FREE",
  "operations_used": 1,
  "operations_remaining": 2
}
```

#### Update Current User
```http
PUT /users/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newemail@example.com",
  "username": "newusername",
  "password": "newpassword123"
}

Response: 200 OK
```

#### Get All Users (Admin Only)
```http
GET /users/?skip=0&limit=100
Authorization: Bearer <admin_token>

Response: 200 OK
[
  {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "role": "user",
    "is_active": true,
    "created_at": "2026-01-13T10:00:00"
  }
]
```

---

### Subscriptions

#### Get Available Plans
```http
GET /subscriptions/plans

Response: 200 OK
[
  {
    "id": 1,
    "name": "FREE",
    "max_operations": 3,
    "price": 0,
    "description": "Plan implicit la înregistrare",
    "created_at": "2026-01-13T10:00:00"
  },
  {
    "id": 2,
    "name": "BASIC",
    "max_operations": 50,
    "price": 999,
    "description": "Pentru utilizatori ocazionali",
    "created_at": "2026-01-13T10:00:00"
  }
]
```

#### Get Current Subscription
```http
GET /subscriptions/my-subscription
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "user_id": 1,
  "plan_id": 1,
  "operations_used": 1,
  "start_date": "2026-01-13T10:00:00",
  "end_date": null,
  "is_active": true,
  "plan_name": "FREE",
  "max_operations": 3,
  "operations_remaining": 2
}
```

#### Upgrade Subscription
```http
POST /subscriptions/upgrade
Authorization: Bearer <token>
Content-Type: application/json

{
  "plan_id": 2
}

Response: 201 Created
{
  "id": 2,
  "user_id": 1,
  "plan_id": 2,
  "operations_used": 0,
  "start_date": "2026-01-13T11:00:00",
  "end_date": null,
  "is_active": true,
  "plan_name": "BASIC",
  "max_operations": 50,
  "operations_remaining": 50
}
```

---

### Images

#### Process Image
```http
POST /images/process
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <image_file>
operation: grayscale | sepia | crop | resize | rotate | blur

# Optional parameters based on operation:
width: 800        # for resize, crop
height: 600       # for resize, crop
x: 0              # for crop
y: 0              # for crop
angle: 90         # for rotate
blur_radius: 5    # for blur

Response: 200 OK
[Binary image data]
```

#### Get Image Processing History
```http
GET /images/history?skip=0&limit=50
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "user_id": 1,
    "filename": "photo.jpg",
    "operation": "grayscale",
    "original_size": "1920x1080",
    "processed_size": "1920x1080",
    "created_at": "2026-01-13T10:00:00"
  }
]
```

#### Get Processed Image by ID
```http
GET /images/{image_id}
Authorization: Bearer <token>

Response: 200 OK
[Binary image data]
```

---

## Image Operations

### Available Operations

1. **grayscale**: Convert image to black and white
2. **sepia**: Apply sepia tone filter
3. **crop**: Crop image (requires: x, y, width, height)
4. **resize**: Resize image (requires: width, height)
5. **rotate**: Rotate image (requires: angle)
6. **blur**: Apply Gaussian blur (requires: blur_radius)

### Example Usage

```bash
# Grayscale
curl -X POST http://localhost:8000/api/v1/images/process \
  -H "Authorization: Bearer <token>" \
  -F "file=@image.jpg" \
  -F "operation=grayscale" \
  -o output.jpg

# Crop
curl -X POST http://localhost:8000/api/v1/images/process \
  -H "Authorization: Bearer <token>" \
  -F "file=@image.jpg" \
  -F "operation=crop" \
  -F "x=100" \
  -F "y=100" \
  -F "width=500" \
  -F "height=500" \
  -o cropped.jpg

# Resize
curl -X POST http://localhost:8000/api/v1/images/process \
  -H "Authorization: Bearer <token>" \
  -F "file=@image.jpg" \
  -F "operation=resize" \
  -F "width=800" \
  -F "height=600" \
  -o resized.jpg
```

---

## Error Responses

```json
{
  "detail": "Error message description"
}
```

### Common Status Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `204 No Content`: Success with no response body
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions or quota exceeded
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
