from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import finance_bp
from .. import db
from ..models import FinancialTransaction, ExpenseClaim, UserRole
from datetime import datetime, timedelta
import calendar

@finance_bp.route('/')
@login_required
def index():
    """Display finance dashboard"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE]:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get recent transactions
    recent_transactions = FinancialTransaction.query.order_by(
        FinancialTransaction.transaction_date.desc()
    ).limit(10).all()
    
    # Get month-to-date totals
    today = datetime.utcnow().date()
    start_of_month = today.replace(day=1)
    
    income_mtd = FinancialTransaction.query.filter(
        FinancialTransaction.transaction_type == 'Income',
        FinancialTransaction.transaction_date >= start_of_month
    ).with_entities(db.func.sum(FinancialTransaction.amount)).scalar() or 0
    
    expenses_mtd = FinancialTransaction.query.filter(
        FinancialTransaction.transaction_type == 'Expense',
        FinancialTransaction.transaction_date >= start_of_month
    ).with_entities(db.func.sum(FinancialTransaction.amount)).scalar() or 0
    
    # Get pending expense claims
    pending_claims = ExpenseClaim.query.filter_by(reimbursed=False).all()
    
    return render_template(
        'finance/index.html',
        transactions=recent_transactions,
        income_mtd=income_mtd,
        expenses_mtd=expenses_mtd,
        pending_claims=pending_claims,
        title='Finance Dashboard'
    )

@finance_bp.route('/transactions')
@login_required
def transactions():
    """Display all financial transactions"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE]:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.dashboard'))
    
    transactions = FinancialTransaction.query.order_by(
        FinancialTransaction.transaction_date.desc()
    ).all()
    
    return render_template(
        'finance/transactions.html',
        transactions=transactions,
        title='Financial Transactions'
    )

@finance_bp.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    """Add a new financial transaction"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE]:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('finance.index'))
    
    if request.method == 'POST':
        transaction = FinancialTransaction(
            transaction_date=datetime.strptime(request.form.get('transaction_date'), '%Y-%m-%d').date(),
            amount=float(request.form.get('amount')),
            transaction_type=request.form.get('transaction_type'),
            category=request.form.get('category'),
            description=request.form.get('description'),
            reference_number=request.form.get('reference_number'),
            created_by_id=current_user.id
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Transaction added successfully', 'success')
        return redirect(url_for('finance.transactions'))
    
    return render_template('finance/add_transaction.html', title='Add Transaction')

@finance_bp.route('/reports')
@login_required
def reports():
    """Financial reports dashboard"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE]:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return render_template('finance/reports.html', title='Financial Reports')

@finance_bp.route('/reports/income-expense', methods=['GET', 'POST'])
@login_required
def income_expense_report():
    """Generate income vs expense report"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE]:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.dashboard'))
    
    today = datetime.utcnow().date()
    
    # Default to current month
    start_date = today.replace(day=1)
    _, last_day = calendar.monthrange(today.year, today.month)
    end_date = today.replace(day=last_day)
    
    if request.method == 'POST':
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
    
    # Get income transactions
    income_transactions = FinancialTransaction.query.filter(
        FinancialTransaction.transaction_type == 'Income',
        FinancialTransaction.transaction_date >= start_date,
        FinancialTransaction.transaction_date <= end_date
    ).order_by(FinancialTransaction.transaction_date).all()
    
    # Get expense transactions
    expense_transactions = FinancialTransaction.query.filter(
        FinancialTransaction.transaction_type == 'Expense',
        FinancialTransaction.transaction_date >= start_date,
        FinancialTransaction.transaction_date <= end_date
    ).order_by(FinancialTransaction.transaction_date).all()
    
    # Calculate totals
    total_income = sum(tx.amount for tx in income_transactions)
    total_expenses = sum(tx.amount for tx in expense_transactions)
    net_profit = total_income - total_expenses
    
    # Group by category for charts
    income_by_category = {}
    for tx in income_transactions:
        if tx.category in income_by_category:
            income_by_category[tx.category] += tx.amount
        else:
            income_by_category[tx.category] = tx.amount
    
    expense_by_category = {}
    for tx in expense_transactions:
        if tx.category in expense_by_category:
            expense_by_category[tx.category] += tx.amount
        else:
            expense_by_category[tx.category] = tx.amount
    
    return render_template(
        'finance/income_expense_report.html',
        start_date=start_date,
        end_date=end_date,
        income_transactions=income_transactions,
        expense_transactions=expense_transactions,
        total_income=total_income,
        total_expenses=total_expenses,
        net_profit=net_profit,
        income_by_category=income_by_category,
        expense_by_category=expense_by_category,
        title='Income vs Expense Report'
    )

@finance_bp.route('/reports/tax-compliance')
@login_required
def tax_compliance():
    """Tax compliance reporting"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE]:
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return render_template('finance/tax_compliance.html', title='Tax Compliance')