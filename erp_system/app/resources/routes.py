from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import resources_bp
from .. import db
from ..models import Resource, ResourceAllocation, UserRole, Employee
from datetime import datetime

@resources_bp.route('/')
@login_required
def index():
    """Display resources dashboard"""
    resources = Resource.query.all()
    return render_template('resources/index.html', resources=resources, title='Resource Management')

@resources_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_resource():
    """Add new resource to inventory"""
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        flash('You do not have permission to add resources', 'danger')
        return redirect(url_for('resources.index'))
    
    if request.method == 'POST':
        resource = Resource(
            name=request.form.get('name'),
            category=request.form.get('category'),
            quantity=int(request.form.get('quantity')),
            status='Available',
            purchase_date=datetime.strptime(request.form.get('purchase_date'), '%Y-%m-%d').date() if request.form.get('purchase_date') else None,
            purchase_cost=float(request.form.get('purchase_cost')) if request.form.get('purchase_cost') else None,
            supplier=request.form.get('supplier'),
            notes=request.form.get('notes')
        )
        
        db.session.add(resource)
        db.session.commit()
        
        # Update status based on quantity
        if resource.quantity <= 0:
            resource.status = 'Out of Stock'
        elif resource.quantity < 5:
            resource.status = 'Low Stock'
        db.session.commit()
        
        flash('Resource added successfully', 'success')
        return redirect(url_for('resources.index'))
    
    return render_template('resources/add.html', title='Add Resource')

@resources_bp.route('/allocate/<int:resource_id>', methods=['GET', 'POST'])
@login_required
def allocate(resource_id):
    """Allocate resource to an employee"""
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        flash('You do not have permission to allocate resources', 'danger')
        return redirect(url_for('resources.index'))
    
    resource = Resource.query.get_or_404(resource_id)
    
    if resource.quantity <= 0:
        flash('Resource is out of stock', 'danger')
        return redirect(url_for('resources.index'))
    
    if request.method == 'POST':
        employee_id = int(request.form.get('employee_id'))
        quantity = int(request.form.get('quantity'))
        
        if quantity > resource.quantity:
            flash(f'Not enough resources available. Only {resource.quantity} in stock.', 'danger')
            return redirect(url_for('resources.allocate', resource_id=resource_id))
        
        allocation = ResourceAllocation(
            resource_id=resource_id,
            employee_id=employee_id,
            allocation_date=datetime.utcnow().date(),
            quantity=quantity,
            status='Allocated',
            notes=request.form.get('notes')
        )
        
        # Update resource quantity
        resource.quantity -= quantity
        
        # Update status based on new quantity
        if resource.quantity <= 0:
            resource.status = 'Out of Stock'
        elif resource.quantity < 5:
            resource.status = 'Low Stock'
        
        db.session.add(allocation)
        db.session.commit()
        
        flash('Resource allocated successfully', 'success')
        return redirect(url_for('resources.index'))
    
    employees = Employee.query.all()
    return render_template(
        'resources/allocate.html', 
        resource=resource, 
        employees=employees,
        title='Allocate Resource'
    )

@resources_bp.route('/return/<int:allocation_id>', methods=['POST'])
@login_required
def return_resource(allocation_id):
    """Process resource return"""
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    allocation = ResourceAllocation.query.get_or_404(allocation_id)
    
    if allocation.status != 'Allocated':
        return jsonify({'success': False, 'message': 'Resource already returned or damaged'}), 400
    
    # Update allocation status
    allocation.status = request.form.get('status', 'Returned')
    allocation.return_date = datetime.utcnow().date()
    
    # If returned in good condition, add back to inventory
    if allocation.status == 'Returned':
        resource = Resource.query.get(allocation.resource_id)
        if resource:
            resource.quantity += allocation.quantity
            
            # Update resource status based on new quantity
            if resource.quantity > 5:
                resource.status = 'Available'
            elif resource.quantity > 0:
                resource.status = 'Low Stock'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Resource return processed successfully',
        'status': allocation.status,
        'return_date': allocation.return_date.strftime('%Y-%m-%d')
    })

@resources_bp.route('/inventory')
@login_required
def inventory():
    """View detailed inventory report"""
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        flash('You do not have permission to view detailed inventory', 'danger')
        return redirect(url_for('resources.index'))
    
    resources = Resource.query.all()
    
    # Calculate statistics
    total_resources = len(resources)
    total_value = sum(r.purchase_cost * r.quantity for r in resources if r.purchase_cost)
    low_stock = sum(1 for r in resources if r.status == 'Low Stock')
    out_of_stock = sum(1 for r in resources if r.status == 'Out of Stock')
    
    return render_template(
        'resources/inventory.html',
        resources=resources,
        stats={
            'total_resources': total_resources,
            'total_value': total_value,
            'low_stock': low_stock,
            'out_of_stock': out_of_stock
        },
        title='Inventory Report'
    )

@resources_bp.route('/allocations')
@login_required
def allocations():
    """View all resource allocations"""
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        flash('You do not have permission to view all allocations', 'danger')
        return redirect(url_for('resources.index'))
    
    allocations = ResourceAllocation.query.all()
    return render_template('resources/allocations.html', allocations=allocations, title='Resource Allocations')