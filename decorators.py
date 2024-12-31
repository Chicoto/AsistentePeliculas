from flask import session, redirect, url_for, flash
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión para acceder a esta página.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def redirect_if_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" in session:
            return redirect(url_for("welcome"))  # Cambia "dashboard" por la ruta a la que quieras redirigir
        return f(*args, **kwargs)
    return decorated_function
