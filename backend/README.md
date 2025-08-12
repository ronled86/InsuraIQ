# Backend Development Guide

## 🏗️ Architecture

The backend is built with:
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Python ORM
- **Alembic**: Database migration tool
- **Pydantic**: Data validation and settings
- **PostgreSQL/SQLite**: Database options
- **Supabase**: Authentication provider (optional)

## 📁 Project Structure

```
backend/
├── app/
│   ├── core/                    # Core configuration
│   │   ├── auth_security.py     # JWT authentication
│   │   ├── middleware.py        # Rate limiting, CORS
│   │   └── settings.py          # Environment configuration
│   ├── routers/                 # API endpoints
│   │   ├── policies.py          # Policy CRUD operations
│   │   ├── portfolio.py         # Portfolio analytics
│   │   └── quotes.py            # Advisory and comparison
│   ├── services/                # Business logic
│   │   ├── compare.py           # Policy comparison
│   │   ├── insurer_api.py       # External API integration
│   │   ├── nlp.py               # CSV parsing utilities
│   │   ├── pdf_import.py        # PDF text extraction
│   │   ├── pricing_model.py     # Pricing calculations
│   │   └── recommendations.py   # Advisory logic
│   ├── database.py              # Database configuration
│   ├── main.py                  # FastAPI application
│   ├── models.py                # SQLAlchemy models
│   └── schemas.py               # Pydantic schemas
├── alembic/                     # Database migrations
├── scripts/                     # Utility scripts
├── requirements.txt             # Production dependencies
├── requirements-local.txt       # Development dependencies
├── run_local_dev.ps1           # Local development script
├── .env.example                # Environment template
└── .env.local-example          # Local development template
```

## 🚀 Setup and Installation

### Quick Start (Recommended)

```powershell
cd backend
Copy-Item .env.local-example .env
.\run_local_dev.ps1
```

### Manual Setup

1. **Create virtual environment**:
   ```powershell
   python -m venv .venv
   . .venv/Scripts/Activate.ps1
   ```

2. **Install dependencies**:
   ```powershell
   # For local development (SQLite, no OCR)
   pip install -r requirements-local.txt
   
   # OR for full features (PostgreSQL, OCR)
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```powershell
   Copy-Item .env.example .env
   # Edit .env with your settings
   ```

4. **Initialize database**:
   ```powershell
   # For SQLite (automatic with LOCAL_DEV=true)
   python -c "from app.database import Base, engine; from app import models; Base.metadata.create_all(bind=engine)"
   
   # For PostgreSQL (with running database)
   alembic upgrade head
   ```

5. **Start development server**:
   ```powershell
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 📊 Database Models

### Policy Model
```python
class Policy(Base):
    __tablename__ = "policies"
    
    id: int                    # Primary key
    user_id: str              # User identifier
    owner_name: str           # Policy owner
    insurer: str              # Insurance company
    product_type: str         # Type of insurance
    policy_number: str        # Unique policy number
    start_date: str           # Coverage start
    end_date: str             # Coverage end
    premium_monthly: float    # Monthly premium
    deductible: float         # Deductible amount
    coverage_limit: float     # Maximum coverage
    notes: str                # Additional notes
    active: bool              # Active status
    updated_at: datetime      # Last modification
```

### CompareHistory Model
```python
class CompareHistory(Base):
    __tablename__ = "compare_history"
    
    id: int                   # Primary key
    user_id: str             # User identifier
    policy_ids_csv: str      # Comma-separated policy IDs
    result_json: str         # Comparison results
    created_at: datetime     # Creation timestamp
```

## 🔧 Configuration

### Environment Variables

#### Required for Production
```bash
SQLALCHEMY_DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db
SUPABASE_URL=https://your-project.supabase.co
API_ISSUER=https://your-project.supabase.co/auth/v1
```

#### Optional Configuration
```bash
API_AUDIENCE=                        # JWT audience validation
SUPABASE_JWKS_URL=                   # Custom JWKS endpoint
RATE_LIMIT_PER_MINUTE=240           # Rate limiting
BASE_PATH=/api                       # API mount path
INSURER_API_BASE=                    # External API base URL
INSURER_API_KEY=                     # External API key
```

#### Development Mode
```bash
LOCAL_DEV=true                       # Enables development features
SQLALCHEMY_DATABASE_URL=sqlite:///./local_dev.db  # Local database
```

### Development vs Production

| Feature | Development | Production |
|---------|-------------|------------|
| Database | SQLite | PostgreSQL |
| Authentication | Bypassed | JWT Required |
| Dependencies | Minimal | Full |
| Migrations | Auto-create | Alembic |
| Logging | File + Console | Structured |

## 🔐 Authentication Flow

### Local Development (`LOCAL_DEV=true`)
1. No authentication required
2. Stub user provided: `{"id": "local-user", "email": "local@example.com"}`
3. All endpoints accessible without tokens

### Production
1. JWT token required in `Authorization: Bearer <token>` header
2. Token validated against Supabase JWKS
3. User information extracted from JWT claims
4. Rate limiting applied per IP

### Authentication Bypass
```python
# In auth_security.py
async def current_user(creds = Depends(bearer)):
    if not creds and settings.LOCAL_DEV:
        return STUB_USER  # Development bypass
    # ... JWT validation logic
```

## 📝 API Development

### Adding New Endpoints

1. **Create router function**:
   ```python
   # In app/routers/your_router.py
   @router.get("/endpoint")
   def your_endpoint(db: Session = Depends(get_db), user = Depends(require_auth)):
       # Your logic here
       return {"result": "data"}
   ```

2. **Add to main application**:
   ```python
   # In app/main.py
   from .routers import your_router
   app.include_router(your_router.router)
   ```

3. **Create Pydantic schemas**:
   ```python
   # In app/schemas.py
   class YourSchema(BaseModel):
       field: str
       number: int
   ```

### Database Operations

```python
# Create
new_item = models.Policy(**data)
db.add(new_item)
db.commit()
db.refresh(new_item)

# Read
items = db.query(models.Policy).filter(models.Policy.user_id == user_id).all()

# Update
item.field = new_value
db.commit()

# Delete
db.delete(item)
db.commit()
```

## 🔄 Database Migrations

### Using Alembic

1. **Generate migration**:
   ```powershell
   alembic revision --autogenerate -m "Add new field"
   ```

2. **Review migration file**:
   ```powershell
   # Check alembic/versions/xxx_add_new_field.py
   ```

3. **Apply migration**:
   ```powershell
   alembic upgrade head
   ```

4. **Rollback if needed**:
   ```powershell
   alembic downgrade -1
   ```

### SQLite Auto-Creation (Development)
```python
# In development mode, tables are auto-created
Base.metadata.create_all(bind=engine)
```

## 🧪 Testing

### Unit Tests (Planned)
```powershell
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Manual Testing
```powershell
# API documentation
curl http://localhost:8000/api/docs

# Health check
curl http://localhost:8000/api/openapi.json

# Test endpoint
curl -X GET http://localhost:8000/api/policies/ \
  -H "Authorization: Bearer your-token"
```

## 🐛 Troubleshooting

### Common Issues

#### Import Errors
```
ModuleNotFoundError: No module named 'app'
```
**Solution**: Ensure you're in the backend directory and virtual environment is activated.

#### Database Connection
```
sqlalchemy.exc.OperationalError
```
**Solution**: 
- Check `SQLALCHEMY_DATABASE_URL` in `.env`
- Ensure PostgreSQL is running (if using)
- For SQLite, check file permissions

#### Authentication Issues
```
HTTPException: 401 Unauthorized
```
**Solution**:
- Set `LOCAL_DEV=true` for development
- Check SUPABASE_URL configuration
- Verify JWT token format

#### Dependency Installation
```
error: Microsoft Visual C++ 14.0 is required
```
**Solution**: Use `requirements-local.txt` or install Visual Studio Build Tools

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check logs:
```powershell
# Development
Get-Content backend-dev.log -Tail 50

# Docker
docker compose logs backend -f
```

## 📈 Performance Considerations

### Database Optimization
- Use database indexes on frequently queried fields
- Implement pagination for large result sets
- Consider connection pooling for high traffic

### Caching
- JWKS responses are cached globally
- Consider Redis for session/query caching

### Rate Limiting
- Current: Simple in-memory IP-based limiting
- Production: Consider Redis-backed distributed limiting

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit secrets to version control
2. **JWT Validation**: Always validate tokens in production
3. **Input Validation**: Use Pydantic schemas for all inputs
4. **SQL Injection**: Use SQLAlchemy ORM, avoid raw queries
5. **CORS**: Configure appropriate origins for production
6. **Rate Limiting**: Implement to prevent abuse

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
