from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Employee, Attendance, WorkflowRequest, Task, Department, Project
from datetime import datetime
from sqlalchemy import func
from . import main_bp
from ..models import User, Payroll, Resource, Workflow, WorkflowStatus

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Main landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html', title='ERP System')

@main.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with summary of all modules"""
    # Gather basic statistics
    stats = {
        'total_employees': Employee.query.count(),
        'present_today': Attendance.query.filter_by(date=datetime.now().date()).count(),
        'pending_requests': WorkflowRequest.query.filter_by(status='pending').count(),
        'tasks_due': Task.query.filter_by(due_date=datetime.now().date()).count(),
        'total_departments': Department.query.count(),
        'pending_workflows': Workflow.query.filter_by(status=WorkflowStatus.PENDING).count(),
        'low_stock_resources': Resource.query.filter_by(status='Low Stock').count()
    }

    # Get recent notifications
    notifications = current_user.notifications.order_by(Notification.timestamp.desc()).limit(5).all()

    # For admin/manager users, prepare chart data
    dept_performance_data = None
    project_status_data = None
    
    if current_user.role.value in ['admin', 'manager']:
        # Department performance data
        dept_data = db.session.query(
            Department.name,
            func.count(Task.id).label('completed_tasks')
        ).join(Employee).join(Task).filter(
            Task.status == 'completed'
        ).group_by(Department.name).all()

        dept_performance_data = {
            'labels': [d[0] for d in dept_data],
            'datasets': [{
                'label': 'Completed Tasks',
                'data': [d[1] for d in dept_data],
                'backgroundColor': 'rgba(54, 162, 235, 0.5)'
            }]
        }

        # Project status data
        project_stats = db.session.query(
            Project.status,
            func.count(Project.id)
        ).group_by(Project.status).all()

        project_status_data = {
            'labels': [s[0] for s in project_stats],
            'datasets': [{
                'data': [s[1] for s in project_stats],
                'backgroundColor': [
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 206, 86, 0.5)',
                    'rgba(75, 192, 192, 0.5)',
                    'rgba(255, 99, 132, 0.5)'
                ]
            }]
        }

    # Get pending approvals for current user
    pending_approvals = Workflow.query.filter_by(
        assignee_id=current_user.id,
        status=WorkflowStatus.PENDING
    ).all()
    
    # User's own statistics
    user_stats = {}
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if employee:
        user_stats['position'] = employee.position
        user_stats['department'] = employee.department.name if employee.department else 'Unassigned'
        
        # Latest payroll
        latest_payroll = Payroll.query.filter_by(user_id=current_user.id).order_by(
            Payroll.pay_period_end.desc()
        ).first()
        if latest_payroll:
            user_stats['latest_payroll'] = {
                'period': f"{latest_payroll.pay_period_start.strftime('%Y-%m-%d')} to {latest_payroll.pay_period_end.strftime('%Y-%m-%d')}",
                'amount': latest_payroll.net_pay,
                'status': latest_payroll.payment_status
            }
    
    return render_template(
        'main/dashboard.html',
        title='Dashboard',
        stats=stats,
        user_stats=user_stats,
        pending_approvals=pending_approvals,
        notifications=notifications,
        dept_performance_data=dept_performance_data,
        project_status_data=project_status_data
    )