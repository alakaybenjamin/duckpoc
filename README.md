# BioMed Search Service

A comprehensive biomedical search service API designed to streamline scientific data discovery and management, with advanced search interaction capabilities.

## Requirements

- Python 3.11 or higher
- PostgreSQL 14 or higher
- pip (Python package installer)

## Local Setup on macOS

### 1. Install PostgreSQL

If you haven't installed PostgreSQL, you can do it via Homebrew:

```bash
brew install postgresql@14
```

Start PostgreSQL service:
```bash
brew services start postgresql@14
```

### 2. Create and Setup Database

1. Create the database:
```bash
createdb biomed_search
```

2. Create database tables using the provided schema:
```bash
psql biomed_search < schema.sql
```

The schema.sql file is in the root directory of the project and contains all the necessary table definitions including:
- users (authentication and user management)
- clinical_study (study information)
- indication (medical indications)
- procedure (medical procedures)
- data_products (study-related data)
- collections (user collections)
- collection_items (items in collections)
- search_history (user search logs)

### 3. Project Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd biomed-search
```

2. Create a `.env` file in the project root:
```bash
# Database configuration
DATABASE_URL=postgresql://localhost/biomed_search

# Session secret (change this to a secure random string)
SESSION_SECRET=your-secret-key-here
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python main.py
```

The application will be available at `http://localhost:5000`

## Key Features

- Advanced search across medical studies, indications, and procedures
- Dynamic data product selection and filtering
- User-driven collection management
- Secure authentication system
- Responsive search interface with intuitive search term management
- Flexible search pill functionality for multi-term queries

## Project Structure

```
.
├── routes/           # API route handlers
├── models/           # Database models
├── static/          # Static files (JS, CSS)
├── templates/       # HTML templates
├── main.py         # Application entry point
├── app.py          # FastAPI app configuration
├── schema.sql      # Database schema DDL statements
└── database.py     # Database configuration
```

## Common Issues & Solutions

### Database Connection Issues

1. **Can't connect to PostgreSQL**
   - Check if PostgreSQL is running: `brew services list`
   - Verify database exists: `psql -l`
   - Ensure DATABASE_URL in .env is correct

2. **Permission Issues**
   - Check PostgreSQL user permissions: `psql -l`
   - If needed, grant permissions: `psql -c "GRANT ALL PRIVILEGES ON DATABASE biomed_search TO your_username;"`

3. **Schema Issues**
   - If tables are missing, rerun schema: `psql biomed_search < schema.sql`
   - Check table creation: `psql biomed_search -c "\dt"`
   - Verify table structure: `psql biomed_search -c "\d+ table_name"`

### Port Already in Use

If port 5000 is already in use:
1. Find the process: `lsof -i :5000`
2. Stop the process: `kill -9 <PID>`

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: `http://localhost:5000/docs`
- Alternative API documentation: `http://localhost:5000/redoc`

## Development Guidelines

1. Follow PEP 8 style guide for Python code
2. Use type hints where possible
3. Keep functions focused and single-purpose
4. Add docstrings for classes and functions
5. Write tests for new features

## Testing

To run tests:
```bash
pytest tests/
```

## Support

For issues and questions, please create an issue in the repository or contact the development team.