from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    redirect,
    session,
    url_for,
    flash,
)
import os

from flask_bootstrap import Bootstrap5
from openai import OpenAI
from dotenv import load_dotenv
from db import db_config, db
from decorators import login_required, redirect_if_logged_in
from models import Message, User, Genre, UserGenre
# from flask_migrate import Migrate

# Configuración de Migraciones


load_dotenv()

client = OpenAI()
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_key")
bootstrap = Bootstrap5(app)
db_config(app)

# migrate = Migrate(app, db)

@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')


@app.route('/')

def index():
    return redirect(url_for('login'))


# #route para las vistas
# @app.route('/')
# def index():
#     return render_template('chat.html')


@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    user_id =session.get("user_id")  # Asumimos que el ID del usuario es 1 (puedes cambiarlo según la lógica de autenticación)
    print("el user_id es", user_id)

    # Obtener géneros del usuario
    user = User.query.get(user_id)
    user_genres = user.get_genres()

    mensajes = Message.get_messages_by_user(user_id)
    if len(mensajes) == 0:
        # Crear un mensaje predeterminado
        message = Message(
            content="Hola! Bienvenido a BuscaPelis, soy SofIA y estoy aquí para ayudarte ¿Que te puedo recomendar?",
            author="assistant",
            user_id=user_id
        )

        db.session.add(message)
        db.session.commit()

    # Crear la lista de preferencias y los intents
    preferences = [
        #{'mensaje': 'Recomiéndame una película que sea muy rara de ver, no conocida pero memorable', 'titulo': 'Sorpréndeme!'}
    ]
    intents = {
        #'Sorpréndeme!': 'Recomiéndame una película que sea muy rara de ver, no conocida pero memorable'
    }

    misgeneros = ""
    for genre in user_genres:
        misgeneros = misgeneros + str(genre.name) + ", "

    preferences.append({
        'mensaje': f'Recomiéndame una película que sea muy rara de ver, no conocida pero memorable, que sea de los generos {misgeneros}', 
        'titulo': 'Sorpréndeme!'
    })

    intents['Sorpréndeme!'] = f'Recomiéndame una película que sea muy rara de ver, no conocida pero memorable, que sea de los generos {misgeneros}'
    intents['Enviar'] = request.form.get('message')


    # Añadir géneros del usuario a las preferencias e intents
    for genre in user_genres:
        genre_name = genre.name
        preferences.append({
            'mensaje': f'Recomiéndame una película de {genre_name}', 
            'titulo': genre_name
        })
        intents[genre_name] = f'Recomiéndame una película de {genre_name}'

    if request.method == 'GET':
        return render_template('chat.html', messages=Message.get_messages_by_user(user_id), preferences=preferences)

    intent = request.form.get('intent')

    # Si el intent coincide con alguno de los géneros o el mensaje predeterminado, tomar su mensaje correspondiente
    if intent in intents:
        user_message = intents[intent]

        # Guardar nuevo mensaje en la BD
        db.session.add(Message(content=user_message, author="user", user_id=user_id))
        db.session.commit()

        texto_base = "Eres un chatbot que recomienda películas, te llamas 'BuscaPelis'. Tu rol es responder recomendaciones de manera breve y concisa. No repitas recomendaciones de películas."
        
        if misgeneros != "":
            texto_base = texto_base  + "Importante! ten en cuenta para las recomendaciones que hagas que mis generos favoritos son: " + misgeneros
        
        messages_for_llm = [{
            "role": "system",
            "content": texto_base,
        }]

        for message in Message.get_messages_by_user(user_id):
            messages_for_llm.append({
                "role": message.author,
                "content": message.content,
            })

        chat_completion = client.chat.completions.create(
            messages=messages_for_llm,
            model="gpt-4o",
            temperature=1.2
        )

        model_recommendation = chat_completion.choices[0].message.content
        db.session.add(Message(content=model_recommendation, author="assistant", user_id=user_id))
        db.session.commit()

        messages = Message.get_messages_by_user(user_id)
        return render_template('chat.html', messages=messages, preferences=preferences)
    

@app.route('/configuration', methods=['GET', 'POST'])
def configuration():
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    all_genres = Genre.query.all()
    user_genres = [genre.id for genre in user.genres]

    if request.method == 'POST':
        try:
            if 'save_password' in request.form:
                password = request.form.get('password')
                if password:
                    user.password = password
                    db.session.commit()
                    return jsonify({'success': True, 'message': 'Contraseña actualizada correctamente'})
                return jsonify({'success': False, 'message': 'Contraseña no proporcionada'})

            elif 'save_preferences' in request.form:
                selected_genres = request.form.getlist('preferences')
                
                if not selected_genres:
                    return jsonify({'success': False, 'message': 'No se seleccionaron géneros'})
                
                try:
                    selected_genre_ids = [int(genre_id) for genre_id in selected_genres]
                    
                    # Limpiar géneros actuales
                    user.genres = []
                    
                    # Agregar nuevos géneros
                    for genre_id in selected_genre_ids:
                        genre = Genre.query.get(genre_id)
                        if genre:
                            user.genres.append(genre)
                    
                    db.session.commit()
                    return jsonify({'success': True, 'message': 'Preferencias actualizadas correctamente'})
                except ValueError:
                    return jsonify({'success': False, 'message': 'ID de género inválido'})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'success': False, 'message': f'Error al actualizar preferencias: {str(e)}'})

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

    return render_template('configuration.html', user=user, all_genres=all_genres, user_genres=user_genres)

# @app.route('/configuration', methods=['GET', 'POST'])
# def configuration():
#     user_id = session.get("user_id")
#     user = User.query.get(user_id)  # Usamos user_id = 1 como ejemplo
#     all_genres = Genre.query.all()

#     # Obtener géneros actuales del usuario
#     user_genres = [genre.id for genre in user.genres]  # Lista de géneros que el usuario tiene

#     if request.method == 'POST':
#         if 'save_password' in request.form:
#             # Guardar la nueva contraseña
#             password = request.form.get('password')
#             if password:
#                 user.password = password
#                 db.session.commit()
#                 flash('Contraseña actualizada correctamente', 'success')

#         elif 'save_preferences' in request.form:
#             # Guardar las preferencias seleccionadas
#             selected_genres = request.form.getlist('preferences')
#             selected_genre_ids = [int(genre_id) for genre_id in selected_genres]

#             # Eliminar las relaciones existentes en user_genres
#             user.genres = []  # Esto eliminará las preferencias actuales del usuario

#             # Agregar las nuevas preferencias
#             for genre_id in selected_genre_ids:
#                 genre = Genre.query.get(genre_id)
#                 user.genres.append(genre)

#             db.session.commit()
#             flash('Preferencias actualizadas correctamente', 'success')

#         return redirect(url_for('configuration'))  # Redirigir para recargar la página con los datos actualizados

#     return render_template('configuration.html', user=user, all_genres=all_genres, user_genres=user_genres)


@app.route("/login", methods=["GET", "POST"])
def login():
    # Si el usuario ya está autenticado, lo redirigimos al chat o dashboard
    if "user_id" in session:
        return redirect(url_for("welcome"))

    if request.method == "POST":
        # Verifica si es una petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            
            # Busca al usuario en la base de datos
            user = User.query.filter_by(username=username).first()

            # Verifica credenciales
            if user and user.password == password:  # Considera usar verificación de hash
                session["user_id"] = user.id
                return jsonify({
                    "success": True,
                    "redirect": url_for("welcome"),
                    "message": "Inicio de sesión exitoso"
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Nombre de usuario o contraseña incorrectos"
                })
        
        # Si no es AJAX, procesa como antes
        else:
            username = request.form.get("username")
            password = request.form.get("password")
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.password == password:
                session["user_id"] = user.id
                flash("Inicio de sesión exitoso", "success")
                return redirect(url_for("welcome"))
            else:
                flash("Credenciales incorrectas", "danger")
                return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("welcome"))

    if request.method == "POST":
        # Verifica si es una petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            confirm_password = data.get("confirm_password")

            # Validaciones
            if not username or not password:
                return jsonify({
                    "success": False,
                    "message": "Todos los campos son obligatorios"
                })
            
            if password != confirm_password:
                return jsonify({
                    "success": False,
                    "message": "Las contraseñas no coinciden"
                })

            # Verifica usuario existente
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return jsonify({
                    "success": False,
                    "message": "El nombre de usuario ya está en uso"
                })

            # Crear nuevo usuario
            try:
                new_user = User(username=username, password=password)  # Considera hashear la contraseña
                db.session.add(new_user)
                db.session.commit()
                return jsonify({
                    "success": True,
                    "redirect": url_for("login"),
                    "message": "Registro exitoso. Por favor, inicia sesión"
                })
            except Exception as e:
                db.session.rollback()
                return jsonify({
                    "success": False,
                    "message": "Error al crear el usuario. Por favor, intenta nuevamente"
                })
        
        # Si no es AJAX, procesa como antes
        else:
            username = request.form.get("username")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")

            if not username or not password:
                flash("Todos los campos son obligatorios", "danger")
                return redirect(url_for("register"))
            
            if password != confirm_password:
                flash("Las contraseñas no coinciden", "danger")
                return redirect(url_for("register"))

            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash("El nombre de usuario ya está en uso", "danger")
                return redirect(url_for("register"))

            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()

            flash("Registro exitoso. Por favor, inicia sesión", "success")
            return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/check-username")
def check_username():
    username = request.args.get("username")
    if not username:
        return jsonify({"available": False})
    
    existing_user = User.query.filter_by(username=username).first()
    return jsonify({"available": existing_user is None})


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     # Si el usuario ya está autenticado, lo redirigimos al chat o dashboard
#     if "user_id" in session:
#         return redirect(url_for("welcome"))  # O redirige a la página deseada (chat, dashboard, etc.)

#     # Si la solicitud es un POST (enviar formulario)
#     if request.method == "POST":
#         username = request.form.get("username")
#         password = request.form.get("password")

#         # Busca al usuario en la base de datos por su username
#         user = User.query.filter_by(username=username).first()

#         # Verifica que el usuario exista y que la contraseña coincida
#         if user and user.password == password:
#             session["user_id"] = user.id  # Guarda el ID del usuario en la sesión
#             flash("Inicio de sesión exitoso", "success")
#             return redirect(url_for("welcome"))  # Redirige a la página protegida (chat o dashboard)
#         else:
#             flash("Credenciales incorrectas", "danger")
#             return redirect(url_for("login"))  # Redirige nuevamente al login si las credenciales son incorrectas

#     # Si es una solicitud GET, simplemente renderiza la página de login
#     return render_template("login.html")



@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop('_flashes', None) 

    return redirect(url_for("login"))

# @app.route("/register", methods=["GET", "POST"])
# def register():
#     # Si el usuario ya está autenticado, lo redirigimos al dashboard o welcome
#     if "user_id" in session:
#         return redirect(url_for("welcome"))

#     # Si la solicitud es un POST (enviar formulario)
#     if request.method == "POST":
#         username = request.form.get("username")
#         password = request.form.get("password")
#         confirm_password = request.form.get("confirm_password")

#         # Validaciones básicas
#         if not username or not password:
#             flash("Todos los campos son obligatorios", "danger")
#             return redirect(url_for("register"))
#         if password != confirm_password:
#             flash("Las contraseñas no coinciden", "danger")
#             return redirect(url_for("register"))

#         # Verifica si el usuario ya existe
#         existing_user = User.query.filter_by(username=username).first()
#         if existing_user:
#             flash("El nombre de usuario ya está en uso", "danger")
#             return redirect(url_for("register"))

#         # Crear un nuevo usuario y guardar en la base de datos
#         new_user = User(username=username, password=password)  # Considera hashear la contraseña
#         db.session.add(new_user)
#         db.session.commit()

#         flash("Registro exitoso. Por favor, inicia sesión", "success")
#         return redirect(url_for("login"))

#     # Si es una solicitud GET, renderiza la página de registro
#     return render_template("register.html")


def is_authenticated():
    return "user_id" in session

@app.context_processor
def inject_user():
    return {"is_authenticated": is_authenticated}