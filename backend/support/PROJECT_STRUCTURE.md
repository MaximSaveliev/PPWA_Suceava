# Project Structure

## FastAPI MVC Architecture

This project follows the **MVC (Model-View-Controller)** pattern with a clear separation of concerns:

```
backend/
├── app/
│   ├── config/              # Configuration & Database
│   │   ├── settings.py      # Application settings
│   │   └── database.py      # Database connection
│   │
│   ├── models/              # SQLAlchemy Models (M)
│   │   ├── user.py
│   │   ├── plan.py
│   │   ├── subscription.py
│   │   └── image_record.py
│   │
│   ├── schemas/             # Pydantic Schemas (V)
│   │   ├── user.py
│   │   ├── plan.py
│   │   ├── subscription.py
│   │   ├── image.py
│   │   └── auth.py
│   │
│   ├── dal/                 # Data Access Layer
│   │   ├── user_dal.py
│   │   ├── plan_dal.py
│   │   ├── subscription_dal.py
│   │   └── image_dal.py
│   │
│   ├── services/            # Business Logic
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── subscription_service.py
│   │   └── image_service.py
│   │
│   ├── controllers/         # API Endpoints (C)
│   │   ├── auth_controller.py
│   │   ├── user_controller.py
│   │   ├── subscription_controller.py
│   │   └── image_controller.py
│   │
│   ├── utils/               # Utilities
│   │   ├── security.py      # JWT & Password hashing
│   │   └── dependencies.py  # FastAPI dependencies
│   │
│   └── main.py              # Application entry point
│
├── support/                 # Documentation
├── requirements.txt
└── .env.example
```

## Flow Architecture

**View → Controller → Service → DAL → DB**

1. **View (Schemas)**: Request/Response validation using Pydantic
2. **Controller**: API endpoints handling HTTP requests
3. **Service**: Business logic and orchestration
4. **DAL**: Database queries and operations
5. **DB**: PostgreSQL database

## Layer Responsibilities

### Models (SQLAlchemy)
- Database table definitions
- Relationships between tables
- Column constraints

### Schemas (Pydantic)
- Request/Response validation
- Data serialization/deserialization
- Type checking

### DAL (Data Access Layer)
- Raw database operations (CRUD)
- Query execution
- Transaction management

### Services
- Business logic
- Data validation beyond schemas
- Orchestration between multiple DALs
- Error handling

### Controllers
- HTTP request handling
- Route definitions
- Authentication/Authorization
- Response formatting

## Key Features

- **Authentication**: JWT-based with OAuth2
- **Authorization**: Role-based (user/admin)
- **Subscription Management**: 4 plans (FREE, BASIC, PREMIUM, ENTERPRISE)
- **Image Processing**: Crop, Grayscale, Sepia, Resize, Rotate, Blur
- **Usage Tracking**: Operations counted per subscription
