# InsuraIQ - AI-Powered Insurance Policy Analysis Platform

[![Version](https://img.shields.io/badge/version-2.0.1-blue.svg)](#)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![React](https://img.shields.io/badge/react-18.0+-blue.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/fastapi-0.104+-red.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

## 🚀 **Revolutionary AI-Enhanced Insurance Policy Management**

InsuraIQ is a cutting-edge platform that transforms how insurance policies are analyzed, compared, and managed. Powered by **OpenAI GPT-4o-mini** and advanced natural language processing, it extracts **100+ parameters** from complex insurance documents in multiple languages.

---
**Current Version:** v2.0.1 - **Hebrew Document Analysis Enhancement**  
**Security:** ✅ Production-ready with comprehensive security measures  
**AI Integration:** ✅ OpenAI GPT-4o-mini for intelligent document analysis

## 🎯 **Key Features**

### 🧠 **AI-Powered Document Analysis**
- **OpenAI GPT-4o-mini Integration** for semantic understanding of insurance documents
- **Hybrid AI + Regex Engine** with intelligent fallback for maximum reliability
- **100+ Parameter Extraction** across all major insurance types (auto, home, health, life, business)
- **Multi-language Support** with Hebrew RTL text handling and English processing
- **Confidence Scoring** provides extraction quality assessment for user confidence

### 📊 **Advanced Policy Comparison**
- **Side-by-side Parameter Analysis** with detailed comparison tables
- **Coverage Gap Detection** using AI recommendations
- **Financial Analysis** comparing premiums, deductibles, and coverage limits
- **Interactive Comparison Interface** with expandable parameter categories
- **Export Capabilities** for reports and analysis documentation

### 📄 **Intelligent PDF Processing**
- **Multi-method Text Extraction** (PDFMiner → PyPDF2 → OCR fallback)
- **AI-Enhanced Content Understanding** for complex policy document layouts
- **Built-in PDF Viewer** with zoom, navigation, and annotation support
- **Secure File Storage** with user authorization and access controls
- **Batch Processing** for multiple document import and analysis

### 🌐 **Modern User Interface**
- **Responsive React Frontend** with TypeScript for type safety
- **Hebrew RTL Support** for international insurance markets
- **Real-time Progress Indicators** with confidence scores and extraction status
- **Mobile-Optimized Design** for access across all device types
- **Professional Dashboard** with comprehensive policy portfolio management

### 🔒 **Enterprise Security**
- **Environment-based Configuration** with no hardcoded secrets
- **API Key Protection** with secure environment variable management
- **Input Validation** and sanitization for all user inputs
- **File Upload Security** with type validation and size limits
- **Authentication Middleware** for API endpoint protection

## 🏗️ **System Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend│    │   FastAPI Backend│    │   AI Processing │
│   (TypeScript)  │◄──►│    (Python)      │◄──►│   (OpenAI GPT)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PDF Viewer    │    │   SQLite DB      │    │   NLP Engine    │
│   (PDF.js)      │    │   (SQLAlchemy)   │    │   (Regex+AI)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 **Quick Start Guide**

### 📋 **Prerequisites**
- **Python 3.8+** (recommended 3.11+)
- **Node.js 16+** (recommended 18+)
- **OpenAI API Key** (required for AI-enhanced analysis)

### 🔧 **Installation**

#### 1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/InsuraIQ.git
cd InsuraIQ
```

#### 2. **Backend Setup**
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux  
source venv/bin/activate

pip install -r requirements.txt
```

#### 3. **🔒 Secure Environment Configuration**
```bash
# Copy the secure environment template
cp .env.example .env

# ⚠️ IMPORTANT: Edit .env and add your actual API keys
# NEVER commit the .env file to version control!
```

**Required Environment Variables:**
```bash
# .env file (keep this secure!)
OPENAI_API_KEY=your_actual_openai_api_key_here
LOCAL_DEV=true
SQLALCHEMY_DATABASE_URL=sqlite:///./local_dev.db
```

#### 4. **Database Initialization**
```bash
alembic upgrade head
```

#### 5. **Frontend Setup**
```bash
cd ../frontend
npm install
```

#### 6. **🚀 Launch Application**

**Option A: Automated Startup (Recommended)**
```bash
# Windows
start_all.bat

# Or use PowerShell with health checks
.\start_all.ps1
```

**Option B: Manual Startup**
```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --no-use-colors

# Terminal 2: Frontend
cd frontend
npm run dev
```

#### 7. **🌐 Access Application**
- **Frontend Interface**: http://localhost:5173
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **OpenAPI Spec**: http://127.0.0.1:8000/openapi.json

---

## ⚠️ **Important Security Notice**

**🔒 This application handles sensitive financial and personal information. Always:**
- Keep your API keys secure and never commit them to version control
- Use HTTPS in production environments
- Regularly update dependencies for security patches
- Follow the security checklist before deployment
- Monitor for unusual activity and implement logging

---

**🏆 Built with ❤️ for the Insurance Industry**

*Transform your insurance policy management with cutting-edge AI-powered analysis*

**Version 2.0.0** - The AI Revolution in Insurance Technology
