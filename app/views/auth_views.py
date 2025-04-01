import io
import os
import tempfile
from datetime import datetime

import pyminizip
from flask import Blueprint, render_template, request, send_file, session

from app.controllers.auth_controller import AuthController
from app.middleware.session_auth import login_required
from config import Config

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        pin = request.form["pin"]
        return AuthController.login(username, pin)
    return render_template("login.html")


@auth_bp.route('/logout')
def logout():
    return AuthController.logout()

@auth_bp.route('/export-page', methods=['GET'])
@login_required
def export_page():
    return render_template('export_data.html')

@auth_bp.route('/export', methods=['POST'])
@login_required
def export_data_pyminizip():
    # Get password from config
    username = session['user']
    password = username + "jobfinder"
    if not password:
        return "Error: Secret key not configured for password.", 500

    if not os.path.exists(Config.USERS_DIR) or not os.path.isdir(Config.USERS_DIR):
        return "Error: USERS_DIR does not exist or is not a directory.", 500

    files_to_zip = []
    relative_paths = []
    for root, _, files in os.walk(Config.USERS_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, Config.USERS_DIR)
            files_to_zip.append(full_path)
            relative_paths.append(relative_path)

    if not files_to_zip:
        return "Error: No files to compress in USERS_DIR.", 500

    # Use a temporary directory to avoid filename collisions
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            zip_filename_tmp = os.path.join(tmpdir, "backup.zip")

            pyminizip.compress_multiple(files_to_zip, relative_paths, zip_filename_tmp, password,
                                        5)  # Compression level 1-9

            # Read the created ZIP file into memory for sending
            with open(zip_filename_tmp, "rb") as f:
                memory_file_content = f.read()

        except Exception as e:
            print(f"Error creating zip file: {e}")
            return "Error creating export file.", 500
        # Temporary directory and its contents are automatically cleaned up here

    # Send the ZIP file content for download
    return send_file(
        io.BytesIO(memory_file_content),  # Send the bytes read from the temp zip
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"user_export_{datetime.now().strftime('%Y%m%d')}.zip"
    )
