# InsuraIQ - Insurance Management Platform

A modern insurance policy management platform built with FastAPI (backend) and React (frontend), designed to help users manage their insurance policies, compare coverage, and get recommendations.

---
**Current Version:** v1.0.0  
See the `VERSION` file for the latest release version.


## 🏗️ Architecture

- **Backend**: FastAPI with SQLAlchemy, PostgreSQL/SQLite
- **Frontend**: React with TypeScript, Vite
- **Deployment**: Docker Compose with Caddy reverse proxy
- **Authentication**: Supabase JWT (configurable)

## 📋 Prerequisites

### For Docker Deployment (Recommended)
- Docker Desktop
- Docker Compose

### For Local Development
- Python 3.11+
- Node.js 20+
- (Optional) PostgreSQL 16+ if not using SQLite

## 🚀 Quick Start

### Option 1: One-Click Startup (Recommended for Local Development)

**Windows Batch Script:**
```cmd
start_all.bat
```

**Windows PowerShell Script (with health checks):**
```powershell
.\start_all.ps1
```

Both scripts will:
- Check for Python and Node.js prerequisites
- Start the FastAPI backend on http://localhost:8000
- Start the React frontend on http://localhost:5173
- Provide status updates and health checks

### Option 2: Docker Deployment

1. **Clone and configure**:
   ```bash
   git clone <repository-url>
   cd InsuraIQ
   cp backend/.env.example .env
   # Edit .env with your Supabase credentials (optional)
   ```

2. **Start the stack**:
   ```bash
   docker compose up --build -d
   ```

3. **Access the application**:
   - Web App: https://localhost (or http://localhost)
   - API Documentation: https://localhost/api/docs
   - API JSON: https://localhost/api/openapi.json

4. **Stop the stack**:
   ```bash
   docker compose down -v
   ```

### Option 3: Manual Local Development (Advanced)

#### Backend Setup

1. **Navigate and setup**:
   ```powershell
   cd backend
   Copy-Item .env.local-example .env
   # Edit .env if needed
   ```

2. **Run the backend**:
   ```powershell
   .\run_local_dev.ps1
   ```

   This script will:
   - Create a Python virtual environment
   - Install dependencies (lightweight set for SQLite)
   - Initialize SQLite database
   - Start Uvicorn server on http://localhost:8000

#### Frontend Setup

In a separate terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend will be available at http://localhost:5173

## 📦 Dependencies

### Backend Dependencies

#### Core Dependencies (requirements.txt)
```
fastapi==0.111.0              # Web framework
uvicorn[standard]==0.30.1     # ASGI server
pydantic==2.8.2               # Data validation
pydantic-settings==2.4.0      # Settings management
SQLAlchemy==2.0.32            # ORM
alembic==1.13.2               # Database migrations
jinja2==3.1.4                 # Template engine
python-multipart==0.0.9       # Form data parsing
httpx==0.27.0                 # HTTP client
python-jose[cryptography]==3.3.0  # JWT handling
```

#### Database Dependencies
```
psycopg2-binary==2.9.9        # PostgreSQL adapter (production)
# SQLite is built into Python (development)
```

#### Optional Dependencies
```
pdfminer.six==20240706        # PDF text extraction
pytesseract==0.3.13           # OCR (requires Tesseract binary)
Pillow==10.4.0                # Image processing
```

#### Local Development (requirements-local.txt)
Lightweight subset excluding:
- `psycopg2-binary` (uses SQLite instead)
- `pytesseract` (OCR disabled for simpler setup)

### Frontend Dependencies

#### Core Dependencies (package.json)
```json
{
  "dependencies": {
    "@supabase/supabase-js": "^2.45.5",  // Auth client
    "react": "^18.3.1",                  // UI framework
    "react-dom": "^18.3.1"              // DOM rendering
  },
  "devDependencies": {
    "@types/react": "^18.3.4",          // TypeScript types
    "@types/react-dom": "^18.3.0",      // TypeScript types
    "@vitejs/plugin-react": "^4.0.0",   // Vite React plugin
    "typescript": "^5.5.4",             // TypeScript compiler
    "vite": "^5.4.1"                    // Build tool
  }
}
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Development mode
LOCAL_DEV=true                                    # Enables auth bypass and SQLite

# Database
SQLALCHEMY_DATABASE_URL=sqlite:///./local_dev.db  # Local SQLite
# SQLALCHEMY_DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db  # Production

# Authentication (optional for local dev)
SUPABASE_URL=https://your-project.supabase.co
API_ISSUER=https://your-project.supabase.co/auth/v1
API_AUDIENCE=                                     # Optional
SUPABASE_JWKS_URL=                               # Optional override

# API Configuration
RATE_LIMIT_PER_MINUTE=240
BASE_PATH=/api

# External Integrations (optional)
INSURER_API_BASE=
INSURER_API_KEY=
```

#### Docker Environment (.env for docker-compose)
```bash
# Same as backend .env, but typically with PostgreSQL URL:
SQLALCHEMY_DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/insurance
```

## 🏃‍♂️ Development Workflow

### Backend Development

1. **Activate environment**:
   ```powershell
   cd backend
   . .venv/Scripts/Activate.ps1
   ```

2. **Install new dependencies**:
   ```powershell
   pip install package-name
   pip freeze > requirements.txt  # Update requirements
   ```

3. **Database migrations**:
   ```powershell
   # Create migration
   alembic revision --autogenerate -m "description"
   
   # Apply migrations
   alembic upgrade head
   ```

4. **Run tests** (when available):
   ```powershell
   pytest
   ```

### Frontend Development

1. **Install new dependencies**:
   ```bash
   npm install package-name
   ```

2. **Build for production**:
   ```bash
   npm run build
   ```

3. **Type checking**:
   ```bash
   npx tsc --noEmit
   ```

## 🔗 API Endpoints

### Policies
- `GET /api/policies/` - List user policies
- `POST /api/policies/` - Create policy
- `PUT /api/policies/{id}` - Update policy
- `DELETE /api/policies/{id}` - Delete policy
- `POST /api/policies/upload` - Upload CSV
- `POST /api/policies/import/pdf` - Import from PDF

### Advisory
- `POST /api/advisor/compare` - Compare policies
- `GET /api/advisor/recommendations` - Get recommendations
- `GET /api/advisor/compare_history` - View comparison history
- `GET /api/advisor/quotes_demo` - Demo external quotes

### Portfolio
- `GET /api/portfolio/summary` - Portfolio overview
- `GET /api/portfolio/analytics` - Analytics data

## 🐳 Docker Configuration

### Services
- **db**: PostgreSQL 16 with health checks
- **backend**: FastAPI application
- **frontend**: React build artifacts
- **caddy**: Reverse proxy with automatic HTTPS

### Volumes
- `db_data`: PostgreSQL data persistence
- `frontend_build`: Shared static assets between frontend and Caddy

## 🔒 Authentication

### Local Development
- Auth is bypassed when `LOCAL_DEV=true`
- Stub user provided: `{"id": "local-user", "email": "local@example.com"}`

### Production
- JWT validation via Supabase
- JWKS endpoint: `{SUPABASE_URL}/auth/v1/keys`
- Configurable audience and issuer validation

## 🛠️ Troubleshooting

### Common Issues

#### Backend won't start
- **Dependency errors**: Use `requirements-local.txt` for simpler local setup
- **Database errors**: Ensure SQLite file permissions or PostgreSQL connectivity
- **Port conflicts**: Change port in `uvicorn` command

#### Frontend build issues
- **Missing dependencies**: Run `npm install`
- **TypeScript errors**: Check `tsconfig.json` configuration
- **Vite plugin issues**: Ensure `@vitejs/plugin-react` is installed

#### Docker issues
- **Build failures**: Try `docker compose build --no-cache`
- **Port conflicts**: Modify ports in `docker-compose.yml`
- **Volume issues**: Run `docker compose down -v` to reset

### Logs and Debugging

#### Local Development
- Backend logs: Check `backend/backend-dev.log`
- Frontend logs: Check browser console

#### Docker
```bash
# View service logs
docker compose logs backend
docker compose logs frontend
docker compose logs caddy

# Follow logs
docker compose logs -f backend
```


## 📚 Documentation

- [Backend Guide](backend/README.md): Detailed backend development documentation
- [Frontend Guide](frontend/README.md): Frontend development and deployment guide
- [Examples](examples/README.md): Sample policy files for testing import functionality

**API Documentation:** To access interactive API docs:
1. Start the backend server: `cd backend && .\run_local_dev.ps1`
2. Visit `http://localhost:8000/api/docs` in your browser

## 📝 License

See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## 📞 Support

For issues and questions:
1. Check this README
2. Review error logs
3. Check the [API documentation](http://localhost:8000/api/docs) when running
4. Open an issue in the repository
