from datetime import datetime

from flask import session, redirect, url_for, flash

from app.services.user_file_service import UserFileService


class AuthController:
    @staticmethod
    def login(username, pin):
        try:
            # Verify user credentials
            if UserFileService.verify_user(username, pin):
                # Set session variables
                session['user'] = username
                session['logged_in'] = True
                session['last_activity'] = datetime.now().isoformat()
                session.permanent = True  # Makes session last for SESSION_LIFETIME

                flash("Login successful!", "success")
                return redirect(url_for('chat_bp.chat'))

            # If user doesn't exist, create them
            if UserFileService.create_user(username, pin):
                session['user'] = username
                session['logged_in'] = True
                session['new_user'] = True  # Flag for first-time users
                session.permanent = True

                flash("Account created successfully!", "success")
                return redirect(url_for('chat_bp.chat'))

        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash("Login failed: " + str(e), "error")

        return redirect(url_for('auth_bp.login'))

    @staticmethod
    def logout():
        session.clear()  # Removes all session data
        return redirect(url_for('auth_bp.login'))
