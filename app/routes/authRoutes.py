from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.controllers.authController import authenticate

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.list_users'))
    if request.method == 'POST':
        user, message = authenticate(request.form.get('username','').strip(), request.form.get('password',''))
        if user:
            login_user(user)
            flash(message, 'success')
            return redirect(url_for('users.list_users'))
        flash(message, 'danger')
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
