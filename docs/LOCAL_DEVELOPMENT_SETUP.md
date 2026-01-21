# Local Development Setup Guide

## Quick Start

### Option 1: Using .env File (Recommended for Local Development)

1. **Install python-dotenv** (if not already installed):
   ```bash
   pip install python-dotenv
   ```

2. **Create .env file** in the project root:
   ```bash
   cp .env.example .env
   ```

3. **Edit .env** with your local database credentials:
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=exam_scheduler
   DB_USER=postgres
   DB_PASSWORD=your_local_password
   ```

4. **Run the application**:
   ```bash
   streamlit run frontend/app.py
   ```

The application will automatically load variables from `.env` file if environment variables are not set.

### Option 2: Using Environment Variables

**Windows PowerShell:**
```powershell
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
$env:DB_NAME="exam_scheduler"
$env:DB_USER="postgres"
$env:DB_PASSWORD="your_password"
streamlit run frontend/app.py
```

**Windows CMD:**
```cmd
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=exam_scheduler
set DB_USER=postgres
set DB_PASSWORD=your_password
streamlit run frontend/app.py
```

**Linux/Mac:**
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=exam_scheduler
export DB_USER=postgres
export DB_PASSWORD=your_password
streamlit run frontend/app.py
```

## How It Works

### Automatic .env Loading

The application automatically attempts to load `.env` file if:
- `DB_PASSWORD` is not set in environment variables
- `.env` file exists in project root
- `python-dotenv` is installed

This means:
- ✅ **Local development**: Just create `.env` file and run
- ✅ **Cloud deployment**: Set environment variables directly (no .env needed)
- ✅ **Security**: No credentials hardcoded, .env is gitignored

### Error Messages

If database connection fails, you'll see a clear error message:

```
❌ Database connection error: DB_PASSWORD environment variable is required.

📋 For LOCAL development:
   1. Create a .env file in the project root (see .env.example)
   2. Add: DB_PASSWORD=your_password
   3. Install python-dotenv: pip install python-dotenv

☁️  For CLOUD deployment:
   1. Set DB_PASSWORD in Streamlit Cloud Secrets
   2. Ensure all DB_* variables are configured

⚠️  Security: Never hardcode passwords in source code!
```

## Troubleshooting

### Error: "DB_PASSWORD environment variable is required"

**Solution 1**: Create `.env` file
```bash
# Copy template
cp .env.example .env

# Edit with your credentials
# Add: DB_PASSWORD=your_password
```

**Solution 2**: Set environment variable
```powershell
# Windows PowerShell
$env:DB_PASSWORD="your_password"
```

**Solution 3**: Install python-dotenv
```bash
pip install python-dotenv
```

### Error: "Module 'dotenv' not found"

**Solution**: Install python-dotenv
```bash
pip install python-dotenv
```

Or use environment variables directly (no .env file needed).

### .env File Not Loading

**Check**:
1. `.env` file is in project root (same level as `frontend/`, `backend/`)
2. File is named exactly `.env` (not `.env.txt` or `env`)
3. `python-dotenv` is installed: `pip install python-dotenv`
4. File contains `DB_PASSWORD=your_password` (no quotes needed)

## Security Notes

1. ✅ **`.env` is gitignored** - Never commit `.env` files
2. ✅ **No hardcoded credentials** - All credentials come from environment
3. ✅ **Cloud deployment** - Uses environment variables directly (no .env)
4. ✅ **Local development** - Optional .env file for convenience

## Comparison: Local vs Cloud

| Aspect | Local Development | Cloud Deployment |
|--------|------------------|------------------|
| Configuration | `.env` file (optional) | Environment variables (required) |
| Loading | Automatic if .env exists | From Streamlit Cloud Secrets |
| Security | .env file (gitignored) | Environment variables (secure) |
| Setup | Create .env file | Set secrets in dashboard |

## Best Practices

1. **Use `.env` for local development** - Easy and convenient
2. **Never commit `.env`** - Already in .gitignore
3. **Use different passwords** - Local vs production
4. **Keep `.env.example` updated** - Document required variables
5. **Test without .env** - Ensure environment variables work too

## Example .env File

```env
# Local Development Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=exam_scheduler
DB_USER=postgres
DB_PASSWORD=my_local_password_123

# Notes:
# - This file is for LOCAL development only
# - Never commit this file to version control
# - For cloud deployment, use environment variables
```

## Verification

Test your setup:

```python
# Test connection
from backend.database.connection import get_connection

try:
    conn = get_connection()
    print("✅ Connection successful!")
    conn.close()
except ValueError as e:
    print(f"❌ Configuration error: {e}")
except Exception as e:
    print(f"❌ Connection error: {e}")
```

## Summary

- ✅ **Local**: Use `.env` file (optional, convenient)
- ✅ **Cloud**: Use environment variables (required, secure)
- ✅ **Both**: No hardcoded credentials
- ✅ **Error messages**: Clear and helpful

The application is now easy to use both locally and in the cloud!
