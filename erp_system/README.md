# Enterprise Resource Planning (ERP) System

A full-fledged ERP system designed for office management with features for employee management, payroll processing, resource allocation, workflow automation, financial reporting, and security compliance.

## Features

### 1. Employee Management
- User registration and authentication
- Employee profiles and department management
- Attendance tracking
- Performance monitoring and reviews

### 2. Payroll Processing
- Salary calculations with deductions
- Tax management
- Payment processing and history
- Payroll reports

### 3. Resource Allocation
- Office resource tracking
- Inventory management
- Resource allocation to employees
- Inventory reports

### 4. Workflow Automation
- Leave request approvals
- Expense claim processing
- Task assignments
- Approval workflows

### 5. Financial Reporting
- Expense tracking
- Income vs expense reporting
- Balance sheets
- Tax compliance

### 6. Security Compliance
- Role-Based Access Control (RBAC)
- User management
- Audit trails
- Security logs

## Technology Stack

- **Backend**: Python with Flask
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login with JWT support
- **Frontend**: Flask templates with Bootstrap (expandable to React/Vue.js)
- **Deployment**: Docker-ready, compatible with AWS/GCP/Azure

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd erp_system
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   .\venv\Scripts\activate
   
   # On Unix or MacOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the root directory and add the following:
   ```
   SECRET_KEY=your_secret_key_here
   DATABASE_URI=postgresql://postgres:postgres@localhost/erp_system
   ```
   
   Note: Update the DATABASE_URI with your PostgreSQL credentials if different.

5. **Initialize the database**
   ```bash
   # Create the database in PostgreSQL
   createdb erp_system

   # Initialize migrations
   flask db init
   
   # Create and apply migrations
   flask db migrate
   flask db upgrade
   ```

## Running the Application

1. **Start the server**
   ```bash
   python run.py
   ```
   
2. Open your web browser and navigate to `http://localhost:5000`

## Project Structure

- `app/` - Main application package
  - `api/` - API endpoints
  - `auth/` - Authentication related routes and forms
  - `employee/` - Employee management
  - `finance/` - Financial management
  - `payroll/` - Payroll management
  - `resources/` - Resource management
  - `security/` - Security features
  - `workflow/` - Workflow management
  - `templates/` - HTML templates
  - `static/` - Static files (CSS, JS, images)

## Docker Support

If you prefer using Docker:

1. **Build the Docker image**
   ```bash
   docker build -t erp-system .
   ```

2. **Run the container**
   ```bash
   docker run -p 5000:5000 erp-system
   ```


## Project Structure

```
erp_system/
├── app/                  # Application package
│   ├── api/              # API endpoints
│   ├── auth/             # Authentication
│   ├── employee/         # Employee management
│   ├── finance/          # Financial reporting
│   ├── payroll/          # Payroll processing
│   ├── resources/        # Resource allocation
│   ├── security/         # Security features
│   ├── workflow/         # Workflow automation
│   ├── static/           # Static assets
│   └── templates/        # HTML templates
├── migrations/           # Database migrations
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── run.py                # Application entry point
```

## Development

### Adding New Features

To add a new feature:
1. Create appropriate models in the relevant module
2. Add routes and views
3. Create templates and forms
4. Update the database with migrations:
   ```
   flask db migrate -m "Add feature X"
   flask db upgrade
   ```

### Running Tests

```
pytest
```

## Deployment

### Docker

1. Build the Docker image:
   ```
   docker build -t erp-system .
   ```

2. Run the container:
   ```
   docker run -p 5000:5000 erp-system
   ```

### Production Deployment

For production deployment:
1. Set up a proper database with backups
2. Configure a secure SECRET_KEY
3. Set up HTTPS with a proper certificate
4. Use a production WSGI server (Gunicorn is included in requirements)
5. Configure a reverse proxy (Nginx/Apache)

## License

[License information here]

## Contributors

[List of contributors]