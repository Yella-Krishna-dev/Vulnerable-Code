# Gold Trading API - Django Version

A Django REST API for buying and selling gold with user authentication and transaction management.

## Features

- **User Authentication**: Register, login, logout, password reset
- **Gold Trading**: Buy and sell gold with simulated pricing
- **Balance Management**: Track cash and gold balances
- **Transaction History**: View all trading transactions
- **Admin Interface**: Django admin for managing users and transactions

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 4. Run the Server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Authentication

#### Register User
```http
POST /api/register/
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "password2": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe"
}
```

#### Login
```http
POST /api/login/
Content-Type: application/json

{
    "username": "john_doe",
    "password": "SecurePass123"
}
```

#### Logout
```http
POST /api/logout/
Authorization: Token your-token-here
```

#### Forgot Password
```http
POST /api/forgot-password/
Content-Type: application/json

{
    "email": "john@example.com"
}
```

#### Reset Password
```http
POST /api/reset-password/
Content-Type: application/json

{
    "reset_token": "uuid-token-here",
    "new_password": "NewSecurePass123"
}
```

#### Change Password
```http
POST /api/change-password/
Authorization: Token your-token-here
Content-Type: application/json

{
    "current_password": "SecurePass123",
    "new_password": "NewSecurePass123"
}
```

### Trading

#### Get Gold Price
```http
GET /api/price/
```

#### Buy Gold
```http
POST /api/buy/
Authorization: Token your-token-here
Content-Type: application/json

{
    "amount": 1.5
}
```

#### Sell Gold
```http
POST /api/sell/
Authorization: Token your-token-here
Content-Type: application/json

{
    "amount": 0.5
}
```

#### Get Balance
```http
GET /api/balance/
Authorization: Token your-token-here
```

#### Get Transaction History
```http
GET /api/transactions/
Authorization: Token your-token-here
```

## Authentication

The API uses Django REST Framework's Token Authentication. After login, include the token in the Authorization header:

```
Authorization: Token your-token-here
```

## Database

The project uses SQLite by default. The database file will be created automatically when you run migrations.

## Admin Interface

Access the Django admin interface at `http://localhost:8000/admin/` to manage:
- Users and their profiles
- Trading transactions
- System settings

## Project Structure

```
gold_trading/
├── gold_trading/          # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── trading/              # Trading app
│   ├── models.py         # Database models
│   ├── views.py          # API views
│   ├── serializers.py    # Data serializers
│   ├── urls.py           # URL patterns
│   └── admin.py          # Admin interface
├── manage.py
├── requirements.txt
└── README.md
```

## Security Notes

- This is a development setup. For production:
  - Change the SECRET_KEY
  - Use environment variables for sensitive settings
  - Set DEBUG=False
  - Configure proper CORS settings
  - Use a production database (PostgreSQL, MySQL)
  - Implement proper email sending for password reset
  - Use HTTPS

## Testing the API

You can test the API using tools like:
- Postman
- curl
- Django REST Framework's browsable API interface

Example curl commands:

```bash
# Register
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"TestPass123","password2":"TestPass123"}'

# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123"}'

# Get gold price
curl http://localhost:8000/api/price/

# Buy gold (replace YOUR_TOKEN with actual token)
curl -X POST http://localhost:8000/api/buy/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount":1.0}'
```