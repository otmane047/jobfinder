import logging

from flask import Blueprint, render_template, session
from flask_socketio import emit, join_room

from app import socketio
from app.middleware.session_auth import login_required
from app.services.chatbot_service import CVBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat_bp', __name__)


@chat_bp.route('/chat')
@login_required
def chat():
    """Route principale du chat"""
    return render_template('chat.html')


@socketio.on('connect')
def handle_connect():
    """Gère la connexion WebSocket"""
    if 'user' not in session:
        emit('error', {'message': "Veuillez vous connecter"})
        return

    username = session['user']
    join_room(username)

    # Initialiser le bot si nécessaire
    if 'cv_bot_state' not in session:
        session['cv_bot_state'] = {
            'cv_data': {},
            'current_step': 0
        }
        bot = CVBot(username)
        emit('bot_message', {
            'response': bot.get_welcome_message(),
            'progress': 0
        })


@socketio.on('user_message')
def handle_user_message(data):
    """Traite les messages des utilisateurs"""
    if 'user' not in session:
        emit('error', {'message': "Non authentifié"})
        return

    username = session['user']
    message = data.get('message', '').strip()

    if not message:
        emit('error', {'message': "Message vide"})
        return

    try:
        # Récupérer l'état actuel
        bot_state = session.get('cv_bot_state', {
            'cv_data': {},
            'current_step': 0
        })

        # Traiter le message
        bot = CVBot(username)
        bot.load_state(bot_state)
        response = bot.process_message(message)

        # Sauvegarder le nouvel état
        new_state = bot.get_state()
        session['cv_bot_state'] = new_state
        session.modified = True

        # Calculer la progression
        filled_fields = sum(1 for v in new_state['cv_data'].values() if v and str(v).strip())
        progress = min(100, int((filled_fields / 10) * 100))  # 10 champs au total

        # Envoyer la réponse
        emit('bot_message', {
            'response': response,
            'progress': progress
        }, room=username)

    except Exception as e:
        logger.error(f"Erreur traitement message: {str(e)}")
        emit('error', {'message': "Erreur de traitement"})


@socketio.on('check_session')
def handle_check_session():
    """Vérifie la session utilisateur"""
    if 'user' not in session:
        emit('error', {'message': "Session expirée"}, callback=lambda: False)
    else:
        emit('session_valid', {'user': session['user']}, callback=lambda: True)