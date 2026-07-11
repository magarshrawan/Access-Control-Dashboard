import os
from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv

bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(project_root, '.env'))

    app = Flask(__name__)
    app.config['SECRET_KEY']     = os.environ.get('SECRET_KEY')
    app.config['MYSQL_HOST']     = os.environ.get('MYSQL_HOST')
    app.config['MYSQL_USER']     = os.environ.get('MYSQL_USER')
    app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
    app.config['MYSQL_DATABASE'] = os.environ.get('MYSQL_DATABASE')

    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access the dashboard.'
    login_manager.login_message_category = 'info'

    from app.routes.authRoutes      import auth_bp
    from app.routes.userRoutes      import user_bp
    from app.routes.roleRoutes      import role_bp
    from app.routes.requestRoutes   import request_bp
    from app.routes.auditRoutes     import audit_bp
    from app.routes.dashboardRoutes import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(request_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(dashboard_bp)

    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('dashboard.dashboard'))

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app
