from flask import jsonify, request
from flask_login import login_required, current_user
from functools import wraps
from . import api_bp
from .. import db
from ..models import (User, UserRole, Employee, Department, Attendance, 
                     PerformanceReview, Payroll, Resource, ResourceAllocation,
                     Workflow, LeaveRequest, ExpenseClaim, FinancialTransaction)

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# User API endpoints
@api_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """Get all users"""
    users = User.query.all()
    return jsonify({
        'users': [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role.value,
                'is_active': user.is_active
            } for user in users
        ]
    })

@api_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """Get specific user"""
    # Only allow users to view themselves unless they're admin/HR
    if user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.HR]:
        return jsonify({'error': 'Permission denied'}), 403
        
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role.value,
        'is_active': user.is_active
    })

# Employee API endpoints
@api_bp.route('/employees', methods=['GET'])
@login_required
def get_employees():
    """Get all employees"""
    employees = Employee.query.all()
    return jsonify({
        'employees': [
            {
                'id': emp.id,
                'user_id': emp.user_id,
                'name': f"{emp.user.first_name} {emp.user.last_name}",
                'department': emp.department.name if emp.department else None,
                'position': emp.position,
                'hire_date': emp.hire_date.strftime('%Y-%m-%d') if emp.hire_date else None,
                'status': emp.employment_status
            } for emp in employees
        ]
    })

@api_bp.route('/employees/<int:employee_id>', methods=['GET'])
@login_required
def get_employee(employee_id):
    """Get specific employee"""
    emp = Employee.query.get_or_404(employee_id)
    
    # Check permissions
    if (current_user.id != emp.user_id and 
        current_user.role not in [UserRole.ADMIN, UserRole.HR, UserRole.MANAGER]):
        return jsonify({'error': 'Permission denied'}), 403
    
    return jsonify({
        'id': emp.id,
        'user_id': emp.user_id,
        'name': f"{emp.user.first_name} {emp.user.last_name}",
        'email': emp.user.email,
        'department': emp.department.name if emp.department else None,
        'position': emp.position,
        'hire_date': emp.hire_date.strftime('%Y-%m-%d') if emp.hire_date else None,
        'status': emp.employment_status,
        'manager': (f"{emp.manager.user.first_name} {emp.manager.user.last_name}" 
                   if emp.manager else None)
    })

# Payroll API endpoints
@api_bp.route('/payroll', methods=['GET'])
@login_required
def get_payroll():
    """Get payroll records"""
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE, UserRole.HR]:
        # Users can only see their own payroll
        payrolls = Payroll.query.filter_by(user_id=current_user.id).all()
    else:
        payrolls = Payroll.query.all()
    
    return jsonify({
        'payrolls': [
            {
                'id': payroll.id,
                'employee': f"{payroll.user.first_name} {payroll.user.last_name}",
                'period': f"{payroll.pay_period_start.strftime('%Y-%m-%d')} to {payroll.pay_period_end.strftime('%Y-%m-%d')}",
                'base_salary': payroll.base_salary,
                'overtime': payroll.overtime_pay,
                'bonus': payroll.bonus,
                'deductions': payroll.tax_deduction + payroll.insurance_deduction + payroll.other_deductions,
                'net_pay': payroll.net_pay,
                'status': payroll.payment_status
            } for payroll in payrolls
        ]
    })

# Resources API endpoints
@api_bp.route('/resources', methods=['GET'])
@login_required
def get_resources():
    """Get all resources"""
    resources = Resource.query.all()
    return jsonify({
        'resources': [
            {
                'id': resource.id,
                'name': resource.name,
                'category': resource.category,
                'quantity': resource.quantity,
                'status': resource.status
            } for resource in resources
        ]
    })

# Workflow API endpoints
@api_bp.route('/workflows', methods=['GET'])
@login_required
def get_workflows():
    """Get workflows"""
    # Users can see workflows they requested or are assigned to them
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.HR]:
        workflows = Workflow.query.filter(
            (Workflow.requester_id == current_user.id) | 
            (Workflow.assignee_id == current_user.id)
        ).all()
    else:
        workflows = Workflow.query.all()
    
    return jsonify({
        'workflows': [
            {
                'id': workflow.id,
                'type': workflow.workflow_type.value,
                'title': workflow.title,
                'requester': f"{workflow.requester.first_name} {workflow.requester.last_name}",
                'assignee': f"{workflow.assigned_to.first_name} {workflow.assigned_to.last_name}" if workflow.assigned_to else None,
                'status': workflow.status.value,
                'created_at': workflow.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for workflow in workflows
        ]
    })

# Financial API endpoints
@api_bp.route('/finance/transactions', methods=['GET'])
@login_required
def get_transactions():
    """Get financial transactions"""
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE]:
        return jsonify({'error': 'Permission denied'}), 403
        
    transactions = FinancialTransaction.query.all()
    return jsonify({
        'transactions': [
            {
                'id': tx.id,
                'date': tx.transaction_date.strftime('%Y-%m-%d'),
                'amount': tx.amount,
                'type': tx.transaction_type,
                'category': tx.category,
                'description': tx.description,
                'reference': tx.reference_number,
                'created_by': f"{tx.created_by.first_name} {tx.created_by.last_name}"
            } for tx in transactions
        ]
    })