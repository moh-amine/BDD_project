# Environment Variables Guide

## Overview

The Exam Scheduling System uses environment variables for database configuration. This ensures:
- ✅ Security (no hardcoded credentials)
- ✅ Flexibility (different configs for local/cloud)
- ✅ Easy deployment (works with Streamlit Cloud)

## Required Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DB_HOST` | Database host | `localhost` | No |
| `DB_PORT` | Database port | `5432` | No |
| `DB_NAME` | Database name | `exam_scheduler` | No |
| `DB_USER` | Database user | `postgres` | No |
| `DB_PASSWORD` | Database password | **None** | **Yes** |

## Local Development

### Method 1: .env File (Recommended)

1. **Create `.env` file** in project root:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env`**:
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=exam_scheduler
   DB_USER=postgres
   DB_PASSWORD=your_password
   ```

3. **Install python-dotenv** (if not installed):
   ```bash
   pip install python-dotenv
   ```

4. **Run application**:
   ```bash
   streamlit run frontend/app.py
   ```

The application automatically loads `.env` if `DB_PASSWORD` is not set in environment.

### Method 2: Environment Variables

**Windows PowerShell:**
```powershell
$env:DB_PASSWORD="your_password"
streamlit run frontend/app.py
```

**Windows CMD:**
```cmd
set DB_PASSWORD=your_password
streamlit run frontend/app.py
```

**Linux/Mac:**
```bash
export DB_PASSWORD=your_password
streamlit run frontend/app.py
```

## Cloud Deployment (Streamlit Cloud)

### Setting Secrets

1. Go to Streamlit Cloud dashboard
2. Select your app
3. Go to **Settings** → **Secrets**
4. Add secrets in TOML format:

```toml
DB_HOST=your-host.neon.tech
DB_PORT=5432
DB_NAME=your-database
DB_USER=your-username
DB_PASSWORD=your-secure-password
```

**Note**: Streamlit Cloud automatically makes secrets available as environment variables.

### No .env File Needed

- ✅ Cloud deployments use environment variables directly
- ✅ No need to create .env file
- ✅ More secure (secrets managed by platform)

## How It Works

### Automatic Loading Priority

1. **First**: Check environment variables (set by system/cloud)
2. **Second**: If `DB_PASSWORD` missing, try loading `.env` file (local dev)
3. **Third**: Raise clear error if still missing

### Code Flow

```python
# 1. Try environment variables
password = os.getenv("DB_PASSWORD")

# 2. If missing, try .env file (local dev only)
if password is None:
    load_dotenv()  # Loads .env if exists
    password = os.getenv("DB_PASSWORD")

# 3. If still missing, raise helpful error
if password is None:
    raise ValueError("DB_PASSWORD required...")
```

## Error Messages

### Missing DB_PASSWORD

If `DB_PASSWORD` is not set, you'll see:

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

### Invalid DB_PORT

```
ValueError: Invalid DB_PORT value: abc. Must be an integer.
```

## Security Best Practices

1. ✅ **Never commit `.env` files** - Already in .gitignore
2. ✅ **Use strong passwords** - Especially for production
3. ✅ **Different passwords** - Local vs production
4. ✅ **Rotate credentials** - Regularly update passwords
5. ✅ **No hardcoded values** - All from environment

## Troubleshooting

### Problem: "DB_PASSWORD environment variable is required"

**Solutions**:
1. Create `.env` file with `DB_PASSWORD=your_password`
2. Set environment variable: `$env:DB_PASSWORD="your_password"`
3. Install python-dotenv: `pip install python-dotenv`

### Problem: .env file not loading

**Check**:
- File is named `.env` (not `.env.txt`)
- File is in project root (same level as `frontend/`)
- Contains `DB_PASSWORD=value` (no quotes)
- `python-dotenv` is installed

### Problem: Connection fails in cloud

**Check**:
- All variables set in Streamlit Cloud Secrets
- Database is accessible from cloud
- Firewall allows connections
- Credentials are correct

## Verification

### Test Local Setup

```python
from backend.database.connection import get_connection

try:
    conn = get_connection()
    print("✅ Connection successful!")
    conn.close()
except ValueError as e:
    print(f"❌ Configuration: {e}")
except Exception as e:
    print(f"❌ Connection: {e}")
```

### Test Environment Variables

```python
import os
print(f"DB_HOST: {os.getenv('DB_HOST', 'NOT SET')}")
print(f"DB_PASSWORD: {'SET' if os.getenv('DB_PASSWORD') else 'NOT SET'}")
```

## Summary

| Scenario | Configuration Method | File Needed |
|----------|---------------------|-------------|
| **Local Dev** | `.env` file | ✅ Yes (optional) |
| **Local Dev** | Environment variables | ❌ No |
| **Cloud** | Streamlit Secrets | ❌ No |
| **Cloud** | Environment variables | ❌ No |

**Key Points**:
- ✅ `.env` is for local convenience only
- ✅ Cloud uses environment variables directly
- ✅ No hardcoded credentials anywhere
- ✅ Clear error messages guide setup
