# InsuraIQ Project Structure

This document describes the organized structure of the InsuraIQ project after reorganization.

## 📁 Root Directory Structure

```
InsuraIQ/
├── 📁 .github/           # GitHub workflows and templates
├── 📁 .git/              # Git repository data
├── 📁 .vscode/           # VS Code settings
├── 📁 backend/           # Backend API and services
├── 📁 docs/              # Documentation files
├── 📁 examples/          # Example files and configurations
├── 📁 frontend/          # React frontend application
├── 📁 infra/             # Infrastructure configuration
├── 📁 scripts/           # Utility scripts and tools
├── 📁 tests/             # Integration and end-to-end tests
├── .gitignore            # Git ignore rules
├── docker-compose.yml    # Docker composition for services
├── LICENSE               # Project license
├── README.md             # Main project documentation
├── SECURITY.md           # Security policies and guidelines
├── start_all.bat         # Main startup script (Windows)
├── start_all.ps1         # Main startup script (PowerShell)
└── VERSION               # Version information
```

## 📂 Folder Contents

### `/docs` - Documentation
- `CHANGELOG.md` - Version history and changes
- `ENHANCED_PDF_IMPORT_SUMMARY.md` - PDF import feature documentation
- `GENERIC_PARSER_IMPLEMENTATION.md` - Parser implementation details
- `PDF_VIEWER_GUIDE.md` - PDF viewer usage guide
- `README_V2.md` - Alternative README version
- `SECURITY_IMPLEMENTATION.md` - Security implementation details
- `SECURITY_IMPLEMENTATION_COMPLETE.md` - Complete security documentation

### `/tests` - Integration Tests
- `test_comprehensive_parser.py` - Comprehensive parser tests
- `test_enhanced_import.py` - Enhanced import functionality tests
- `test_hebrew_import.py` - Hebrew document import tests
- `test_landa_document.py` - Landa document specific tests
- `test_pdf_endpoint.py` - PDF endpoint API tests
- `test_pdf_upload.py` - PDF upload functionality tests
- `test-policy.txt` - Test policy data

### `/scripts` - Utility Scripts
- `analyze_hebrew_doc.py` - Hebrew document analysis tool
- `check_policies.py` - Policy validation script
- `setup.bat` - Project setup script
- `stop_all.bat` - Service shutdown script
- `test_cleanup.bat` - Test cleanup utility

### `/examples` - Examples and Templates
- `.env.production.example` - Production environment template
- Various PDF examples and sample data

## 🚀 Quick Start

To start the entire application:
```bash
# Windows
start_all.bat

# PowerShell
.\start_all.ps1
```

## 🧪 Running Tests

Integration tests are located in the `/tests` folder:
```bash
cd tests
python test_comprehensive_parser.py
```

## 📖 Documentation

All project documentation is now organized in the `/docs` folder for easy access and maintenance.

## 🛠️ Scripts and Utilities

Utility scripts for development, testing, and maintenance are located in the `/scripts` folder.
