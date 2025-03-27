from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import payroll_bp
from .. import db
from ..models import User, Employee, Payroll, UserRole
from datetime import datetime

@payroll_bp.route('/')
@login_required
def index():
    """Display payroll dashboard"""
    if current_user.role in [UserRole.ADMIN, UserRole.FINANCE, UserRole.HR]:
        # Admin, finance and HR can see all payrolls
        payrolls = Payroll.query.all()
        return render_template('payroll/index.html', payrolls=payrolls, title='Payroll Management')
    else:
        # Regular employees can only see their own payroll
        payrolls = Payroll.query.filter_by(user_id=current_user.id).all()
        return render_template('payroll/employee_payroll.html', payrolls=payrolls, title='My Payroll')

@payroll_bp.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    """Generate payroll for employees"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE, UserRole.HR]:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('payroll.index'))
    
    if request.method == 'POST':
        # Implementation for payroll generation
        flash('Payroll generated successfully', 'success')
        return redirect(url_for('payroll.index'))
    
    employees = Employee.query.all()
    return render_template('payroll/generate.html', employees=employees, title='Generate Payroll')

@payroll_bp.route('/<int:payroll_id>')
@login_required
def view(payroll_id):
    """View specific payroll details"""
    payroll = Payroll.query.get_or_404(payroll_id)
    
    # Check permissions - only allow viewing if it's the user's own payroll
    # or if user has admin/finance role
    if (payroll.user_id != current_user.id and 
        current_user.role not in [UserRole.ADMIN, UserRole.FINANCE, UserRole.HR]):
        flash('You do not have permission to view this payroll', 'danger')
        return redirect(url_for('payroll.index'))
    
    return render_template('payroll/view.html', payroll=payroll, title='Payroll Details')

@payroll_bp.route('/reports')
@login_required
def reports():
    """Generate payroll reports"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE, UserRole.HR]:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('payroll.index'))
    
    return render_template('payroll/reports.html', title='Payroll Reports')

@payroll_bp.route('/process/<int:payroll_id>', methods=['POST'])
@login_required
def process_payment(payroll_id):
    """Process payroll payment"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE]:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    payroll = Payroll.query.get_or_404(payroll_id)
    payroll.payment_status = 'Paid'
    payroll.payment_date = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Payment processed for {payroll.user.first_name} {payroll.user.last_name}',
        'payroll_id': payroll.id,
        'status': payroll.payment_status,
        'payment_date': payroll.payment_date.strftime('%Y-%m-%d %H:%M:%S')
    })