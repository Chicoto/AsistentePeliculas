from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
import os

from flask_bootstrap import Bootstrap5
from openai import OpenAI
from dotenv import load_dotenv
from db import db_config, db
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
def welcome():
    return render_template('welcome.html')

@app.route('/login')
def login():
    return render_template('login.html')  # Aquí deberías crear el formulario de inicio de sesión

@app.route('/register')
def register():
    return render_template('register.html')  # Aquí deberías crear el formulario de registro


@app.route('/')
def index():
    return redirect(url_for('welcome'))


# #route para las vistas
# @app.route('/')
# def index():
#     return render_template('chat.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    user_id = 1  # Asumimos que el ID del usuario es 1 (puedes cambiarlo según la lógica de autenticación)

    # Obtener géneros del usuario
    user = User.query.get(user_id)
    user_genres = user.get_genres()

    mensajes = Message.get_all_messages()
    print(len(mensajes))
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

    print(misgeneros)

    # preferences.append({
    #     'mensaje': request.form.get('message'), 
    #     'titulo': 'Enviar'
    # })
    
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
        return render_template('chat.html', messages=Message.get_all_messages(), preferences=preferences)

    intent = request.form.get('intent')

    # Si el intent coincide con alguno de los géneros o el mensaje predeterminado, tomar su mensaje correspondiente
    if intent in intents:
        user_message = intents[intent]

        # Guardar nuevo mensaje en la BD
        db.session.add(Message(content=user_message, author="user", user_id=user_id))
        db.session.commit()

        messages_for_llm = [{
            "role": "system",
            "content": "Eres un chatbot que recomienda películas, te llamas 'BuscaPelis'. Tu rol es responder recomendaciones de manera breve y concisa. No repitas recomendaciones de películas.",
        }]

        for message in Message.get_all_messages():
            messages_for_llm.append({
                "role": message.author,
                "content": message.content,
            })

        chat_completion = client.chat.completions.create(
            messages=messages_for_llm,
            model="gpt-4o",
            temperature=1.5
        )

        model_recommendation = chat_completion.choices[0].message.content
        db.session.add(Message(content=model_recommendation, author="assistant", user_id=user_id))
        db.session.commit()

        messages = Message.get_all_messages()
        return render_template('chat.html', messages=messages, preferences=preferences)
    

@app.route('/configuration', methods=['GET', 'POST'])
def configurations():
    user = User.query.get(1)  # Usamos user_id = 1 como ejemplo
    all_genres = Genre.query.all()

    # Obtener géneros actuales del usuario
    user_genres = [genre.id for genre in user.genres]  # Lista de géneros que el usuario tiene

    if request.method == 'POST':
        if 'save_password' in request.form:
            # Guardar la nueva contraseña
            password = request.form.get('password')
            if password:
                user.password = password
                db.session.commit()
                flash('Contraseña actualizada correctamente', 'success')

        elif 'save_preferences' in request.form:
            # Guardar las preferencias seleccionadas
            selected_genres = request.form.getlist('preferences')
            selected_genre_ids = [int(genre_id) for genre_id in selected_genres]

            # Eliminar las relaciones existentes en user_genres
            user.genres = []  # Esto eliminará las preferencias actuales del usuario

            # Agregar las nuevas preferencias
            for genre_id in selected_genre_ids:
                genre = Genre.query.get(genre_id)
                user.genres.append(genre)

            db.session.commit()
            flash('Preferencias actualizadas correctamente', 'success')

        return redirect(url_for('configurations'))  # Redirigir para recargar la página con los datos actualizados

    return render_template('configuration.html', user=user, all_genres=all_genres, user_genres=user_genres)

# def chat():

#     # Lista de preferencias
#     preferences = [
#         {'mensaje': 'Recomiéndame una película que sea muy rara de ver, no conocida pero memorable', 'titulo': 'Sorpréndeme!'},
#         {'mensaje': 'Recomiéndame una película de terror', 'titulo': 'Terror'},
#         {'mensaje': 'Recomiéndame una película de acción', 'titulo': 'Acción'},
#         {'mensaje': 'Recomiéndame una película de comedia', 'titulo': 'Comedia'}
#     ]

#     if request.method == 'GET':
#         return render_template('chat.html', messages = Message.get_all_messages(), preferences = preferences)

#     intent = request.form.get('intent')

#     print(intent)
#     intents = {
#         'Sorpréndeme!': 'Recomiéndame una película que sea muy rara de ver, no conocida pero memorable',
#         'Terror': 'Recomiéndame una película de terror',
#         'Acción': 'Recomiéndame una película de acción',
#         'Comedia': 'Recomiéndame una película de comedia',
#         'Enviar': request.form.get('message')
#     }

#     if intent in intents:
#         user_message = intents[intent]

#         # Guardar nuevo mensaje en la BD
#         db.session.add(Message(content=user_message, author="user", user_id = 1))
#         db.session.commit()

#         messages_for_llm = [{
#             "role": "system",
#             "content": "Eres un chatbot que recomienda películas, te llamas 'BuscaPelis'. Tu rol es responder recomendaciones de manera breve y concisa. No repitas recomendaciones.",
#         }]

#         for message in Message.get_all_messages():
#             messages_for_llm.append({
#                 "role": message.author,
#                 "content": message.content,
#             })

#         chat_completion = client.chat.completions.create(
#             messages=messages_for_llm,
#             model="gpt-4o",
#             temperature=1
#         )

#         model_recommendation = chat_completion.choices[0].message.content
#         db.session.add(Message(content=model_recommendation, author="assistant", user_id = 1))
#         db.session.commit()

#         messages = Message.get_all_messages()
#         return render_template('chat.html', messages=messages, preferences=preferences)