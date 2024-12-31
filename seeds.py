from app import app
from db import db
from models import Message, User
from datetime import datetime

# Asegúrate de ejecutar esta función al iniciar la aplicación o en una migración.
def create_default_user():
    # Verifica si el usuario ya existe
    default_user = User.query.filter_by(username='admin').first()
    if not default_user:
        default_user = User(username='admin', password='admin123')  # Contraseña por defecto
        db.session.add(default_user)
        db.session.commit()
        print("Usuario por defecto creado.")
    else:
        print("El usuario ya existe.")

with app.app_context():
    db.create_all()  # Crea las tablas en la base de datos
    create_default_user()  # Crear el usuario predeterminado

    # Crear un mensaje predeterminado
    message = Message(
        content="Hola! Bienvenido a BuscaPelis ¿Que te puedo recomendar?",
        author="assistant",
        user_id=1  # Asigna el ID del usuario predeterminado
    )

    db.session.add(message)
    db.session.commit()