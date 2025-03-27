from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import employee_bp
from .. import db
from ..models import Employee, Department, User, Attendance, PerformanceReview
from datetime import datetime

@employee_bp.route('/')
@login_required
def index():
    """Display list of all employees"""
    employees = Employee.query.all()
    return render_template('employee/index.html', employees=employees, title='Employees')

@employee_bp.route('/<int:employee_id>')
@login_required
def profile(employee_id):
    """Display employee profile"""
    employee = Employee.query.get_or_404(employee_id)
    return render_template('employee/profile.html', employee=employee, title='Employee Profile')

@employee_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Register a new employee"""
    # Implementation for employee registration
    return render_template('employee/register.html', title='Register Employee')

@employee_bp.route('/attendance')
@login_required
def attendance():
    """View attendance records"""
    if current_user.role.name in ['ADMIN', 'HR', 'MANAGER']:
        records = Attendance.query.all()
    else:
        employee = Employee.query.filter_by(user_id=current_user.id).first()
        if not employee:
            flash('Employee record not found', 'danger')
            return redirect(url_for('main.dashboard'))
        records = employee.attendance_records
    
    return render_template('employee/attendance.html', records=records, title='Attendance Records')

@employee_bp.route('/attendance/check-in', methods=['POST'])
@login_required
def check_in():
    """Record check-in time"""
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if not employee:
        return jsonify({'success': False, 'message': 'Employee record not found'})
    
    today = datetime.utcnow().date()
    attendance = Attendance.query.filter_by(
        employee_id=employee.id, 
        date=today
    ).first()
    
    if attendance:
        if attendance.check_in:
            return jsonify({'success': False, 'message': 'Already checked in today'})
    else:
        attendance = Attendance(employee_id=employee.id, date=today)
    
    attendance.check_in = datetime.utcnow()
    attendance.status = 'Present'
    db.session.add(attendance)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Check-in recorded successfully',
        'time': attendance.check_in.strftime('%H:%M:%S')
    })

@employee_bp.route('/attendance/check-out', methods=['POST'])
@login_required
def check_out():
    """Record check-out time"""
    employee = Employee.query.filter_by(user_id=current_user.id).first()
    if not employee:
        return jsonify({'success': False, 'message': 'Employee record not found'})
    
    today = datetime.utcnow().date()
    attendance = Attendance.query.filter_by(
        employee_id=employee.id, 
        date=today
    ).first()
    
    if not attendance or not attendance.check_in:
        return jsonify({'success': False, 'message': 'No check-in record found for today'})
    
    attendance.check_out = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Check-out recorded successfully',
        'time': attendance.check_out.strftime('%H:%M:%S')
    })

@employee_bp.route('/performance')
@login_required
def performance():
    """View performance reviews"""
    if current_user.role.name in ['ADMIN', 'HR', 'MANAGER']:
        reviews = PerformanceReview.query.all()
    else:
        employee = Employee.query.filter_by(user_id=current_user.id).first()
        if not employee:
            flash('Employee record not found', 'danger')
            return redirect(url_for('main.dashboard'))
        reviews = employee.performance_reviews
    
    return render_template('employee/performance.html', reviews=reviews, title='Performance Reviews')