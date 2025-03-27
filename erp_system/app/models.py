from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager
import enum

class UserRole(enum.Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    EMPLOYEE = 'employee'
    HR = 'hr'
    FINANCE = 'finance'

class User(UserMixin, db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password = db.Column(db.String(256))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    role = db.Column(db.Enum(UserRole), default=UserRole.EMPLOYEE)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee_info = db.relationship('Employee', backref='user', uselist=False)
    payrolls = db.relationship('Payroll', backref='user')
    workflows = db.relationship('Workflow', backref='assigned_to')

    def set_password(self, password):
        """Set password hash"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against stored hash"""
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))

class Department(db.Model):
    """Department model for organizational structure"""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employees = db.relationship('Employee', backref='department')

class Employee(db.Model):
    """Employee model for staff details"""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    position = db.Column(db.String(64))
    hire_date = db.Column(db.Date)
    employment_status = db.Column(db.String(20), default='Active')  # Active, On Leave, Resigned
    salary = db.Column(db.Float)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subordinates = db.relationship('Employee', backref=db.backref('manager', remote_side=[id]))
    attendance_records = db.relationship('Attendance', backref='employee')
    performance_reviews = db.relationship('PerformanceReview', backref='employee')

class Attendance(db.Model):
    """Attendance tracking model"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    date = db.Column(db.Date, default=datetime.utcnow().date)
    check_in = db.Column(db.DateTime, nullable=True)
    check_out = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='Present')  # Present, Absent, Late, Half-day
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PerformanceReview(db.Model):
    """Employee performance evaluation model"""
    __tablename__ = 'performance_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    review_date = db.Column(db.Date, default=datetime.utcnow().date)
    period_start = db.Column(db.Date)
    period_end = db.Column(db.Date)
    rating = db.Column(db.Integer)  # 1-5 scale
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    reviewer = db.relationship('User', backref='reviews_given')

class Payroll(db.Model):
    """Payroll model for salary processing"""
    __tablename__ = 'payrolls'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    pay_period_start = db.Column(db.Date)
    pay_period_end = db.Column(db.Date)
    base_salary = db.Column(db.Float)
    overtime_pay = db.Column(db.Float, default=0)
    bonus = db.Column(db.Float, default=0)
    tax_deduction = db.Column(db.Float, default=0)
    insurance_deduction = db.Column(db.Float, default=0)
    other_deductions = db.Column(db.Float, default=0)
    net_pay = db.Column(db.Float)
    payment_status = db.Column(db.String(20), default='Pending')  # Pending, Paid, Cancelled
    payment_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Resource(db.Model):
    """Office resources and inventory model"""
    __tablename__ = 'resources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    category = db.Column(db.String(64))
    quantity = db.Column(db.Integer)
    status = db.Column(db.String(20), default='Available')  # Available, Low Stock, Out of Stock
    purchase_date = db.Column(db.Date, nullable=True)
    purchase_cost = db.Column(db.Float, nullable=True)
    supplier = db.Column(db.String(64), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    allocations = db.relationship('ResourceAllocation', backref='resource')

class ResourceAllocation(db.Model):
    """Track resource allocations to employees"""
    __tablename__ = 'resource_allocations'
    
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    allocation_date = db.Column(db.Date, default=datetime.utcnow().date)
    return_date = db.Column(db.Date, nullable=True)
    quantity = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='Allocated')  # Allocated, Returned, Damaged
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    employee = db.relationship('Employee', backref='resource_allocations')

class WorkflowType(enum.Enum):
    LEAVE_REQUEST = 'leave_request'
    EXPENSE_CLAIM = 'expense_claim'
    RESOURCE_REQUEST = 'resource_request'
    TRAVEL_REQUEST = 'travel_request'
    OTHER = 'other'

class WorkflowStatus(enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'

class Workflow(db.Model):
    """Workflow for approvals and requests"""
    __tablename__ = 'workflows'
    
    id = db.Column(db.Integer, primary_key=True)
    workflow_type = db.Column(db.Enum(WorkflowType))
    title = db.Column(db.String(128))
    description = db.Column(db.Text)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.Enum(WorkflowStatus), default=WorkflowStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    requester = db.relationship('User', foreign_keys=[requester_id], backref='requested_workflows')
    
    # Polymorphic configuration
    __mapper_args__ = {
        'polymorphic_on': workflow_type,
    }

class LeaveRequest(Workflow):
    """Leave request workflow model"""
    __tablename__ = 'leave_requests'
    
    id = db.Column(db.Integer, db.ForeignKey('workflows.id'), primary_key=True)
    leave_type = db.Column(db.String(20))  # Sick, Vacation, Personal, etc.
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    __mapper_args__ = {
        'polymorphic_identity': WorkflowType.LEAVE_REQUEST,
    }

class ExpenseClaim(Workflow):
    """Expense claim workflow model"""
    __tablename__ = 'expense_claims'
    
    id = db.Column(db.Integer, db.ForeignKey('workflows.id'), primary_key=True)
    amount = db.Column(db.Float)
    expense_date = db.Column(db.Date)
    category = db.Column(db.String(64))
    receipt_path = db.Column(db.String(256), nullable=True)
    reimbursed = db.Column(db.Boolean, default=False)
    
    __mapper_args__ = {
        'polymorphic_identity': WorkflowType.EXPENSE_CLAIM,
    }

class FinancialTransaction(db.Model):
    """Financial transactions model"""
    __tablename__ = 'financial_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_date = db.Column(db.Date, default=datetime.utcnow().date)
    amount = db.Column(db.Float)
    transaction_type = db.Column(db.String(20))  # Income, Expense, Transfer
    category = db.Column(db.String(64))
    description = db.Column(db.Text, nullable=True)
    reference_number = db.Column(db.String(64), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    created_by = db.relationship('User', backref='financial_transactions')