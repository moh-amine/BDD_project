# Cloud Deployment Setup Guide

## Overview

This document describes the changes made to prepare the Exam Scheduling System for cloud deployment on Streamlit Cloud with cloud PostgreSQL (Neon/Supabase).

## Changes Made

### 1. Database Connection (`backend/database/connection.py`)

**Before**: Hardcoded credentials
```python
return psycopg2.connect(
    host="localhost",
    port=5432,
    database="exam_scheduler",
    user="postgres",
    password="1234",
    ...
)
```

**After**: Environment variables
```python
host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "5432")
database = os.getenv("DB_NAME", "exam_scheduler")
user = os.getenv("DB_USER", "postgres")
password = os.getenv("DB_PASSWORD")  # Required, no default
```

**Benefits**:
- ✅ Works both locally and in cloud
- ✅ No hardcoded credentials
- ✅ Secure password handling
- ✅ Easy configuration per environment

### 2. Requirements File (`requirements.txt`)

Created `requirements.txt` with all dependencies:
- `streamlit>=1.28.0` - Web framework
- `psycopg2-binary>=2.9.9` - PostgreSQL adapter
- `bcrypt>=4.0.1` - Password hashing
- `python-dotenv>=1.0.0` - Environment variable loading (optional)

### 3. Git Ignore (`.gitignore`)

Updated to exclude:
- `.env` files (environment variables)
- `__pycache__/` directories
- Streamlit cache
- IDE files
- Temporary files

### 4. Environment Template (`.env.example`)

Created template file showing required environment variables:
- `DB_HOST` - Database host
- `DB_PORT` - Database port
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password (required)

## Local Development Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Create `.env` File

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your local database credentials
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=exam_scheduler
# DB_USER=postgres
# DB_PASSWORD=your_password
```

### Step 3: Load Environment Variables (Optional)

For local development, you can use `python-dotenv` to automatically load `.env`:

```python
# Add to frontend/app.py (optional, for local dev)
from dotenv import load_dotenv
load_dotenv()  # Loads .env file
```

**Note**: Streamlit Cloud automatically loads environment variables, so this is optional.

### Step 4: Run Application

```bash
streamlit run frontend/app.py
```

## Cloud Deployment (Streamlit Cloud)

### Step 1: Prepare Repository

1. Ensure all changes are committed:
   ```bash
   git add .
   git commit -m "Prepare for cloud deployment"
   git push
   ```

2. Verify `.env` is NOT committed:
   ```bash
   git status
   # .env should NOT appear in the list
   ```

### Step 2: Set Environment Variables in Streamlit Cloud

1. Go to your Streamlit Cloud dashboard
2. Select your app
3. Go to "Settings" → "Secrets"
4. Add the following secrets:

```toml
DB_HOST=your-cloud-db-host.neon.tech
DB_PORT=5432
DB_NAME=your-database-name
DB_USER=your-username
DB_PASSWORD=your-secure-password
```

**Note**: Streamlit Cloud uses TOML format in the Secrets section, but the app reads them as environment variables.

### Step 3: Configure App Settings

- **Main file**: `frontend/app.py`
- **Python version**: 3.9+ (recommended: 3.10 or 3.11)
- **Branch**: `main` (or your deployment branch)

### Step 4: Deploy

Streamlit Cloud will:
1. Install dependencies from `requirements.txt`
2. Load environment variables from Secrets
3. Run `streamlit run frontend/app.py`

## Cloud Database Setup (Neon/Supabase)

### Neon PostgreSQL

1. Create account at [neon.tech](https://neon.tech)
2. Create a new project
3. Copy connection string
4. Extract credentials:
   - Host: `xxx.neon.tech`
   - Port: `5432`
   - Database: from connection string
   - User: from connection string
   - Password: from connection string

### Supabase PostgreSQL

1. Create account at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Settings → Database
4. Copy connection string
5. Extract credentials (similar to Neon)

### Database Schema

After setting up the cloud database:

1. Run the schema creation:
   ```bash
   psql -h your-host -U your-user -d your-database -f backend/database/exam_scheduler.sql
   ```

2. Or use the Python script:
   ```bash
   python scripts/create_users_table.py
   python scripts/populate_sample_data.py
   ```

## Verification

### Test Local Connection

```python
from backend.database.connection import get_connection

try:
    conn = get_connection()
    print("✅ Connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### Test Cloud Connection

After deployment, check Streamlit Cloud logs for connection errors.

## Troubleshooting

### Error: "DB_PASSWORD environment variable is required"

**Solution**: Set `DB_PASSWORD` in your environment or `.env` file.

### Error: Connection refused

**Solution**: 
- Check `DB_HOST` is correct
- Verify database is accessible from your network
- Check firewall settings

### Error: Authentication failed

**Solution**:
- Verify `DB_USER` and `DB_PASSWORD` are correct
- Check database user permissions

## Security Notes

1. ✅ **Never commit `.env` files** - They contain sensitive credentials
2. ✅ **Use strong passwords** - Especially for production databases
3. ✅ **Use SSL connections** - For cloud databases (add `sslmode=require` if needed)
4. ✅ **Rotate credentials** - Regularly update database passwords

## Project Structure

```
BDDA_project/
├── backend/
│   ├── database/
│   │   └── connection.py  # ✅ Uses environment variables
│   ├── services/
│   └── optimization/
├── frontend/
│   └── app.py  # ✅ Entry point for Streamlit
├── requirements.txt  # ✅ All dependencies
├── .gitignore  # ✅ Excludes .env and cache
├── .env.example  # ✅ Template for environment variables
└── README.md
```

## Conclusion

The project is now ready for cloud deployment:
- ✅ No hardcoded credentials
- ✅ Environment variable support
- ✅ Requirements file created
- ✅ Git ignore updated
- ✅ Project structure verified

Next steps:
1. Set up cloud PostgreSQL (Neon/Supabase)
2. Configure Streamlit Cloud secrets
3. Deploy and test
