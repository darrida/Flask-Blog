import os
import click
from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Role, Permission
from flask import abort
from functools import wraps
from flask_login import current_user
  

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)