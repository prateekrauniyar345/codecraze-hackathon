# ScholarSense Backend

FastAPI backend for ScholarSense - AI-powered application assistant for students.

## Setup

### 1. Install Dependencies

Make sure you're in the backend directory and have activated the virtual environment:

```bash
cd backend
source .venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and update with your values:

```bash
cp .env.example .env
```

Edit `.env` and update:
- `DATABASE_URL`: Your PostgreSQL connection string
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `SECRET_KEY`: A secure random string for JWT tokens

### 3. Setup Database

Create the PostgreSQL database:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE scholarsense;
\q
```

Run the schema to create tables:

```bash
psql -U postgres -d scholarsense -f schema.sql
```

Optional - Load seed data:

```bash
psql -U postgres -d scholarsense -f seed.sql
```

### 4. Run the Server

```bash
python main.py
# or
uvicorn main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── database.py            # Database connection and session
├── requirements.txt       # Python dependencies
├── schema.sql            # PostgreSQL schema
├── seed.sql              # Sample data
├── models/               # SQLAlchemy models
│   ├── user.py
│   ├── document.py
│   ├── profile.py
│   ├── opportunity.py
│   └── material.py
├── schemas/              # Pydantic schemas
│   ├── user.py
│   ├── document.py
│   ├── profile.py
│   ├── opportunity.py
│   └── material.py
├── routers/              # API endpoints
│   ├── auth.py
│   ├── documents.py
│   ├── profiles.py
│   ├── opportunities.py
│   └── materials.py
├── services/             # Business logic
│   └── llm_client.py
├── utils/               # Utility functions
│   ├── auth.py
│   └── file_utils.py
└── storage/
    └── uploads/         # Uploaded files
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

### Documents
- `POST /documents/upload` - Upload resume/CV
- `GET /documents/` - List user's documents
- `GET /documents/{id}` - Get document details
- `GET /documents/{id}/text` - Get extracted text
- `DELETE /documents/{id}` - Delete document

### Profiles
- `POST /profiles/` - Create profile
- `POST /profiles/from-document/{id}` - Create from document
- `GET /profiles/` - List profiles
- `GET /profiles/latest` - Get latest profile
- `GET /profiles/{id}` - Get specific profile
- `PATCH /profiles/{id}` - Update profile
- `DELETE /profiles/{id}` - Delete profile

### Opportunities
- `POST /opportunities/` - Create opportunity
- `POST /opportunities/analyze` - Analyze fit (without saving)
- `POST /opportunities/{id}/analyze` - Analyze and update opportunity
- `GET /opportunities/` - List opportunities (optional status filter)
- `GET /opportunities/{id}` - Get opportunity
- `PATCH /opportunities/{id}` - Update opportunity
- `DELETE /opportunities/{id}` - Delete opportunity

### Materials
- `POST /materials/generate` - Generate application materials
- `GET /materials/opportunity/{id}` - Get materials for opportunity
- `GET /materials/{id}` - Get specific material
- `DELETE /materials/{id}` - Delete material

## Testing

You can test the API using:
1. Swagger UI at http://localhost:8000/docs
2. curl or httpie from command line
3. Postman or similar API testing tools

Example:
```bash
# Register a user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","full_name":"Test User"}'
```
