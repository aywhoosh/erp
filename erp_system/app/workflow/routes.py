from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import workflow_bp
from .. import db
from ..models import (Workflow, WorkflowType, WorkflowStatus, 
                     LeaveRequest, ExpenseClaim, User, Employee)
from datetime import datetime

@workflow_bp.route('/')
@login_required
def index():
    """Display workflow dashboard"""
    # Get workflows requested by the user
    requested_workflows = Workflow.query.filter_by(requester_id=current_user.id).all()
    
    # Get workflows assigned to the user for approval
    assigned_workflows = Workflow.query.filter_by(assignee_id=current_user.id).all()
    
    return render_template(
        'workflow/index.html',
        requested_workflows=requested_workflows,
        assigned_workflows=assigned_workflows,
        title='Workflow Dashboard'
    )

@workflow_bp.route('/leave-request', methods=['GET', 'POST'])
@login_required
def leave_request():
    """Create a new leave request"""
    if request.method == 'POST':
        # Find the employee's manager to assign the request to
        employee = Employee.query.filter_by(user_id=current_user.id).first()
        if not employee:
            flash('Employee record not found', 'danger')
            return redirect(url_for('workflow.index'))
            
        manager_id = None
        if employee.manager:
            manager_id = employee.manager.user_id
        
        # If no manager, assign to HR
        if not manager_id:
            hr_user = User.query.filter_by(role=UserRole.HR).first()
            if hr_user:
                manager_id = hr_user.id
            else:
                # Fallback to admin
                admin_user = User.query.filter_by(role=UserRole.ADMIN).first()
                if admin_user:
                    manager_id = admin_user.id
        
        # Create the leave request workflow
        leave_request = LeaveRequest(
            workflow_type=WorkflowType.LEAVE_REQUEST,
            title=f"Leave Request: {request.form.get('leave_type')}",
            description=request.form.get('reason'),
            requester_id=current_user.id,
            assignee_id=manager_id,
            status=WorkflowStatus.PENDING,
            leave_type=request.form.get('leave_type'),
            start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        )
        
        db.session.add(leave_request)
        db.session.commit()
        
        flash('Leave request submitted successfully', 'success')
        return redirect(url_for('workflow.index'))
    
    return render_template('workflow/leave_request.html', title='Submit Leave Request')

@workflow_bp.route('/expense-claim', methods=['GET', 'POST'])
@login_required
def expense_claim():
    """Create a new expense claim"""
    if request.method == 'POST':
        # Find finance manager or admin to assign the request to
        finance_manager = User.query.filter_by(role=UserRole.FINANCE).first()
        if finance_manager:
            assignee_id = finance_manager.id
        else:
            # Fallback to admin
            admin_user = User.query.filter_by(role=UserRole.ADMIN).first()
            if admin_user:
                assignee_id = admin_user.id
            else:
                assignee_id = None
        
        # Create the expense claim workflow
        expense_claim = ExpenseClaim(
            workflow_type=WorkflowType.EXPENSE_CLAIM,
            title=f"Expense Claim: {request.form.get('category')} - ${request.form.get('amount')}",
            description=request.form.get('description'),
            requester_id=current_user.id,
            assignee_id=assignee_id,
            status=WorkflowStatus.PENDING,
            amount=float(request.form.get('amount')),
            expense_date=datetime.strptime(request.form.get('expense_date'), '%Y-%m-%d').date(),
            category=request.form.get('category')
        )
        
        db.session.add(expense_claim)
        db.session.commit()
        
        flash('Expense claim submitted successfully', 'success')
        return redirect(url_for('workflow.index'))
    
    return render_template('workflow/expense_claim.html', title='Submit Expense Claim')

@workflow_bp.route('/approve/<int:workflow_id>', methods=['POST'])
@login_required
def approve_workflow(workflow_id):
    """Approve a workflow request"""
    workflow = Workflow.query.get_or_404(workflow_id)
    
    # Check permissions
    if workflow.assignee_id != current_user.id:
        return jsonify({'success': False, 'message': 'Not authorized to approve this request'}), 403
    
    workflow.status = WorkflowStatus.APPROVED
    workflow.completed_at = datetime.utcnow()
    db.session.commit()
    
    # If it's an expense claim that was approved, mark it for reimbursement
    if workflow.workflow_type == WorkflowType.EXPENSE_CLAIM:
        expense = ExpenseClaim.query.get(workflow_id)
        if expense:
            expense.reimbursed = True
    
    return jsonify({
        'success': True,
        'message': 'Workflow approved successfully',
        'workflow_id': workflow.id,
        'status': workflow.status.value,
        'completed_at': workflow.completed_at.strftime('%Y-%m-%d %H:%M:%S')
    })

@workflow_bp.route('/reject/<int:workflow_id>', methods=['POST'])
@login_required
def reject_workflow(workflow_id):
    """Reject a workflow request"""
    workflow = Workflow.query.get_or_404(workflow_id)
    
    # Check permissions
    if workflow.assignee_id != current_user.id:
        return jsonify({'success': False, 'message': 'Not authorized to reject this request'}), 403
    
    workflow.status = WorkflowStatus.REJECTED
    workflow.completed_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Workflow rejected',
        'workflow_id': workflow.id,
        'status': workflow.status.value,
        'completed_at': workflow.completed_at.strftime('%Y-%m-%d %H:%M:%S')
    })