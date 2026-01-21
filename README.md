# Exam Scheduling System

A comprehensive exam scheduling and management system with automatic timetable generation.

## Features

- 🔐 Role-based authentication (Admin, Professeur, Etudiant)
- 📅 Automatic exam scheduling with constraint enforcement
- 🎯 Database-level constraint validation
- 📊 Analytics and reporting
- 👥 Multi-user support

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: PostgreSQL
- **Architecture**: No ORM (raw SQL only)

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BDDA_project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Set up database**
   ```bash
   # Create database schema
   psql -U postgres -d exam_scheduler -f backend/database/exam_scheduler.sql
   
   # Create users table
   python scripts/create_users_table.py
   
   # Populate sample data (optional)
   python scripts/populate_sample_data.py
   ```

5. **Run the application**
   ```bash
   streamlit run frontend/app.py
   ```

## Environment Variables

Required environment variables (set in `.env` file or system environment):

- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 5432)
- `DB_NAME` - Database name (default: exam_scheduler)
- `DB_USER` - Database user (default: postgres)
- `DB_PASSWORD` - Database password (**required**, no default)

## Project Structure

```
BDDA_project/
├── backend/
│   ├── database/          # Database connection and queries
│   ├── services/          # Business logic services
│   └── optimization/      # Automatic scheduling
├── frontend/
│   └── app.py            # Streamlit application
├── scripts/               # Utility scripts
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
└── .env.example          # Environment variables template
```

## Cloud Deployment

See [docs/CLOUD_DEPLOYMENT_SETUP.md](docs/CLOUD_DEPLOYMENT_SETUP.md) for detailed cloud deployment instructions.

## Documentation

- [Automatic Scheduling Guide](docs/AUTOMATIC_SCHEDULING_GUIDE.md)
- [Constraints Implementation](docs/CONSTRAINTS_IMPLEMENTATION.md)
- [Cloud Deployment Setup](docs/CLOUD_DEPLOYMENT_SETUP.md)

## License

Academic project - For educational purposes only.
