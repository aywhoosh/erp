import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config=None):
    """Factory function to create the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure the app
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_only_for_development'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URI', 'postgresql://postgres:postgres@localhost/erp_system'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Update config if provided
    if config:
        app.config.update(config)
        
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    from .api import api_bp
    from .auth import auth_bp
    from .employee import employee_bp
    from .payroll import payroll_bp
    from .resources import resources_bp
    from .workflow import workflow_bp
    from .finance import finance_bp
    from .security import security_bp
    from .main import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(payroll_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(workflow_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(security_bp)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    return app
