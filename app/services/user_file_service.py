import csv
import os
from datetime import datetime
from io import StringIO

from app.services.encryption_service import vigenere_encryption, vigenere_decryption
from config import Config


class UserFileService:
    @staticmethod
    def get_user_path(username):
        Config.ensure_users_dir()
        return os.path.join(Config.USERS_DIR, f"{username}.csv")

    @staticmethod
    def user_exists(username):
        return os.path.exists(UserFileService.get_user_path(username))

    @staticmethod
    def create_user(username, pin):
        if not (pin.isdigit() and len(pin) == 6):
            raise ValueError("PIN must be exactly 6 digits")

        if UserFileService.user_exists(username):
            raise ValueError("Username already exists")

        user_path = UserFileService.get_user_path(username)

        # Create initial CSV data
        data = StringIO()
        writer = csv.writer(data)
        writer.writerow(["username", "pin", "created_at"])
        writer.writerow([username, pin, str(datetime.now())])

        # Encrypt the entire CSV content
        encrypted_data = vigenere_encryption(data.getvalue(), username)

        # Write encrypted data to file
        with open(user_path, 'w', encoding='utf-8') as file:
            file.write(encrypted_data)

        return True

    @staticmethod
    def verify_user(username, pin):
        if not (pin.isdigit() and len(pin) == 6):
            return False

        user_path = UserFileService.get_user_path(username)
        if not os.path.exists(user_path):
            return False

        try:
            # Read and decrypt the file
            with open(user_path, 'r', encoding='utf-8') as file:
                encrypted_data = file.read()
                decrypted_data = vigenere_decryption(encrypted_data, username)

                # Parse the CSV
                reader = csv.DictReader(decrypted_data.splitlines())
                for row in reader:
                    if row['pin'] == pin:
                        return True
            return False
        except Exception:
            return False

    @staticmethod
    def get_user_data(username, pin):
        if not UserFileService.verify_user(username, pin):
            return None

        user_path = UserFileService.get_user_path(username)
        try:
            with open(user_path, 'r', encoding='utf-8') as file:
                encrypted_data = file.read()
                decrypted_data = vigenere_decryption(encrypted_data, username)
                reader = csv.DictReader(decrypted_data.splitlines())
                return list(reader)
        except Exception:
            return None

    @staticmethod
    def save_cv_data(username, pin, cv_data):
        if not UserFileService.verify_user(username, pin):
            return False

        cv_path = os.path.join(Config.USERS_DIR, f"{username}_cv.csv")

        try:
            # Read existing data if file exists
            existing_data = []
            if os.path.exists(cv_path):
                with open(cv_path, 'r', encoding='utf-8') as file:
                    encrypted_data = file.read()
                    decrypted_data = vigenere_decryption(encrypted_data, username)
                    reader = csv.DictReader(decrypted_data.splitlines())
                    existing_data = list(reader)

            # Add new data
            existing_data.append(cv_data)

            # Prepare new CSV data
            data = StringIO()
            writer = csv.DictWriter(data, fieldnames=cv_data.keys())
            writer.writeheader()
            writer.writerows(existing_data)

            # Encrypt and save
            encrypted_data = vigenere_encryption(data.getvalue(),username)
            with open(cv_path, 'w', encoding='utf-8') as file:
                file.write(encrypted_data)

            return True
        except Exception as e:
            print(f"Error saving CV data: {str(e)}")
            return False

    @staticmethod
    def get_cv_data(username, pin):
        if not UserFileService.verify_user(username, pin):
            return None

        cv_path = os.path.join(Config.USERS_DIR, f"{username}_cv.csv")

        if not os.path.exists(cv_path):
            return None

        try:
            with open(cv_path, 'r', encoding='utf-8') as file:
                encrypted_data = file.read()
                decrypted_data = vigenere_decryption(encrypted_data, username)
                reader = csv.DictReader(decrypted_data.splitlines())
                return list(reader)
        except Exception:
            return None