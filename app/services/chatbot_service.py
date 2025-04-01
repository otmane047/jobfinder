import csv
import os
from io import StringIO

from flask import session

from app.services.encryption_service import vigenere_encryption, vigenere_decryption
from config import Config


class CVBot:
    def __init__(self, username: str):
        self.username = username
        self.cv_data = session.get("cv_data", {
            'nom_complet': '', 'age': '', 'niveau_etude': '', 'ecole': '',
            'ville': '', 'experience': '', 'poste_recherche': '', 'salaire': '',
            'type_contrat': '', 'competences': ''
        })
        self.questions = [
            ('nom_complet', "Quel est votre nom complet ?"),
            ('age', "Quel est votre âge ?"),
            ('niveau_etude', "Quel est votre niveau d'étude ?"),
            ('ecole', "Quelle école/université avez-vous fréquentée ?"),
            ('ville', "Dans quelle ville recherchez-vous un emploi ?"),
            ('experience', "Combien d'années d'expérience avez-vous ?"),
            ('poste_recherche', "Quel poste recherchez-vous ?"),
            ('salaire', "Quelles sont vos prétentions salariales ?"),
            ('type_contrat', "Quel type de contrat cherchez-vous ?"),
            ('competences', "Quelles sont vos compétences techniques ?") # Question remains the same
        ]
        self.current_step = session.get("current_step", 0)
        self.cvs_dir = os.path.join(Config.USERS_DIR, "cvs")
        os.makedirs(self.cvs_dir, exist_ok=True)

    def get_welcome_message(self):
        current_field, current_question = self.questions[self.current_step]
        return f"Bonjour {self.username} ! Commençons par créer votre CV. {current_question}"

    def load_state(self, state):
        default_cv_data = {
            'nom_complet': '', 'age': '', 'niveau_etude': '', 'ecole': '',
            'ville': '', 'experience': '', 'poste_recherche': '', 'salaire': '',
            'type_contrat': '', 'competences': ''
        }
        loaded_cv_data = state.get('cv_data', {})
        self.cv_data = {**default_cv_data, **loaded_cv_data}
        self.current_step = state.get('current_step', 0)


    def get_state(self):
        """Retourne l'état courant pour sauvegarde"""
        # No change needed here
        return {
            'cv_data': self.cv_data,
            'current_step': self.current_step
        }

    def process_message(self, message: str) -> str:
        """Traite la réponse de l'utilisateur et passe à la question suivante."""
        if self.current_step >= len(self.questions):
            return self._save_cv()

        current_field, current_question = self.questions[self.current_step]

        # MODIFIED: Removed the special handling for 'competences'.
        # Now it's treated like any other field, assigning the message directly.
        self.cv_data[current_field] = message

        self.current_step += 1

        session["cv_data"] = self.cv_data
        session["current_step"] = self.current_step

        return self._next_question()

    def _next_question(self) -> str:
        """Passe à la question suivante."""
        # No change needed here
        if self.current_step < len(self.questions):
            return self.questions[self.current_step][1]
        return self._save_cv()

    def _save_cv(self) -> str:
        try:
            header_io = StringIO()
            header_writer = csv.writer(header_io, lineterminator='\n')
            headers = list(self.cv_data.keys())  # Ensure consistent order
            header_writer.writerow(headers)
            header_string = header_io.getvalue()
            header_io.close()

            # --- Generate Data Row String ---
            data_io = StringIO()
            # Use quoting=csv.QUOTE_MINIMAL or QUOTE_ALL to handle special chars in data
            data_writer = csv.writer(data_io, lineterminator='\n')
            # Get values in the same order as headers
            data_values = [self.cv_data[h] for h in headers]
            data_writer.writerow(data_values)
            data_string = data_io.getvalue()
            data_io.close()

            # --- Encrypt only the Data Row String ---
            encrypted_data_string = vigenere_encryption(data_string, self.username)

            # --- Save to file ---
            csv_filename = os.path.join(self.cvs_dir, f"cv_{self.username}.csv")
            with open(csv_filename, "w", encoding="utf-8") as f:
                # Write plaintext header
                f.write(header_string)
                # Write encrypted data row
                f.write(encrypted_data_string)  # Already includes its own newline from csv writer

            # Clear session data after saving
            session.pop("cv_data", None)
            session.pop("current_step", None)

            return f"✅ CV sauvegardé (en-tête non chiffré) sous {csv_filename}"
        except Exception as e:
            return f"❌ Erreur lors de la sauvegarde : {str(e)}"

    @classmethod
    def load_cv(cls, username: str):
        try:
            cvs_dir = os.path.join(Config.USERS_DIR, "cvs")
            csv_filename = os.path.join(cvs_dir, f"cv_{username}.csv")

            if not os.path.exists(csv_filename):
                return None

            with open(csv_filename, "r", encoding="utf-8") as f:
                header_line = f.readline()
                if not header_line:
                    raise ValueError("Fichier CV vide ou en-tête manquant.")
                headers = next(csv.reader([header_line]))

                encrypted_data_line = f.readline()
                if not encrypted_data_line:
                    print(f"Warning: Fichier CV {csv_filename} contient seulement l'en-tête.")

                    values = [''] * len(headers)

                else:
                    decrypted_data_line = vigenere_decryption(encrypted_data_line, username)
                    values = next(csv.reader([decrypted_data_line]))

            if len(headers) != len(values):
                raise ValueError(f"Incohérence entre en-tête et données dans {csv_filename}. "
                                 f"En-têtes: {len(headers)}, Valeurs: {len(values)}")

            # Reconstruct CV data
            cv_data = dict(zip(headers, values))

            # Optional: Ensure the 'competences' key exists and defaults to ''
            # (This check might be redundant if headers are guaranteed from save)
            if 'competences' not in cv_data:
                cv_data['competences'] = ''

            return cv_data
        except Exception as e:
            print(f"Error loading CV ({username}): {str(e)}")
            return None