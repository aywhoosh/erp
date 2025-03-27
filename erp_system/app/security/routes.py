from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from . import security_bp
from .. import db
from ..models import User, UserRole
from functools import wraps

def admin_required(f):
    """Decorator to restrict access to admin users only"""
    @wraps(f)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            flash('You need administrator privileges to access this page.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_view

@security_bp.route('/')
@login_required
@admin_required
def index():
    """Security dashboard"""
    users = User.query.all()
    return render_template('security/index.html', users=users, title='Security Dashboard')

@security_bp.route('/users')
@login_required
@admin_required
def users():
    """User management page"""
    users = User.query.all()
    return render_template('security/users.html', users=users, title='User Management')

@security_bp.route('/users/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user details and permissions"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.email = request.form.get('email')
        
        # Only update password if provided
        if request.form.get('password'):
            user.password = generate_password_hash(request.form.get('password'))
        
        # Update role if changed
        new_role = request.form.get('role')
        if new_role and new_role in [role.name for role in UserRole]:
            user.role = UserRole[new_role]
        
        # Update active status
        user.is_active = 'is_active' in request.form
        
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('security.users'))
    
    roles = [(role.name, role.value) for role in UserRole]
    return render_template(
        'security/edit_user.html',
        user=user,
        roles=roles,
        title=f'Edit User - {user.username}'
    )

@security_bp.route('/users/deactivate/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def deactivate_user(user_id):
    """Deactivate a user account"""
    user = User.query.get_or_404(user_id)
    
    # Prevent deactivating own account
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot deactivate your own account'}), 400
    
    user.is_active = False
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'User {user.username} has been deactivated',
        'user_id': user.id
    })

@security_bp.route('/users/activate/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def activate_user(user_id):
    """Activate a user account"""
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'User {user.username} has been activated',
        'user_id': user.id
    })

@security_bp.route('/roles')
@login_required
@admin_required
def roles():
    """Role management page"""
    roles = [(role.name, role.value) for role in UserRole]
    
    # Count users in each role
    role_counts = {}
    for role in UserRole:
        role_counts[role.name] = User.query.filter_by(role=role).count()
    
    return render_template(
        'security/roles.html',
        roles=roles,
        role_counts=role_counts,
        title='Role Management'
    )

@security_bp.route('/logs')
@login_required
@admin_required
def logs():
    """View security logs"""
    # This would typically connect to a logging system
    # For now, we'll just show a placeholder
    return render_template('security/logs.html', title='Security Logs')

@security_bp.route('/audit')
@login_required
@admin_required
def audit():
    """Audit trail for system changes"""
    # This would typically connect to an audit tracking system
    # For now, we'll just show a placeholder
    return render_template('security/audit.html', title='Audit Trail')