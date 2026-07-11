from flask import Blueprint, render_template
from flask_login import login_required
from app.controllers.dashboardController import get_dashboard_ctrl

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    metrics = get_dashboard_ctrl()
    return render_template('dashboard.html', **metrics)
