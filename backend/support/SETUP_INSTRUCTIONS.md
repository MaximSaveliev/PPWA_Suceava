# Setup Instructions

## Prerequisites

- Python 3.10+
- PostgreSQL 14+
- pip (Python package manager)

---

## Installation Steps

### 1. Clone/Navigate to Project
```bash
cd backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Database Setup

#### Create Database
```sql
CREATE DATABASE image_processing_db;
```

#### Run the SQL Schema
Execute the provided SQL schema to create tables and insert initial data:
```bash
psql -U postgres -d image_processing_db -f schema.sql
```

Or manually connect and execute the SQL provided in the requirements.

### 6. Configure Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` file:
```env
DATABASE_URL=postgresql://postgres:qwerty123@localhost:5432/image_processing_db
SECRET_KEY=generate-a-strong-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
```

**Generate a strong SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 7. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Testing the API

### 1. Register a New User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

Save the `access_token` from the response.

### 3. Get User Info
```bash
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

### 4. Process an Image
```bash
curl -X POST http://localhost:8000/api/v1/images/process \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@/path/to/image.jpg" \
  -F "operation=grayscale" \
  -o output.jpg
```

---

## Project Structure

```
backend/
├── app/
│   ├── config/          # Configuration
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── dal/             # Data Access Layer
│   ├── services/        # Business logic
│   ├── controllers/     # API routes
│   ├── utils/           # Utilities
│   └── main.py          # Entry point
├── support/             # Documentation
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Database Schema

The database includes the following tables:

- **users**: User accounts
- **plans**: Subscription plans (FREE, BASIC, PREMIUM, ENTERPRISE)
- **subscriptions**: User subscriptions
- **image_records**: Image processing history

### Default Plans

| Plan | Operations | Price (cents) |
|------|-----------|---------------|
| FREE | 3 | 0 |
| BASIC | 50 | 999 |
| PREMIUM | 200 | 1999 |
| ENTERPRISE | 999999 | 4999 |

---

## Common Issues

### Database Connection Error
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists

### Import Errors
- Activate virtual environment
- Install all dependencies: `pip install -r requirements.txt`

### Port Already in Use
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

---

## Development Tips

### Enable Auto-reload
The `--reload` flag automatically restarts the server when code changes.

### View Logs
All output is printed to console when running with uvicorn.

### Database Migrations
For schema changes, consider using Alembic:
```bash
pip install alembic
alembic init migrations
```

---

## Production Deployment

1. Set strong `SECRET_KEY` in production
2. Disable `--reload` flag
3. Use a production WSGI server (Gunicorn)
4. Set up HTTPS
5. Configure CORS for your frontend domain
6. Use environment variables for sensitive data
7. Set up database backups

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
