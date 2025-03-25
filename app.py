from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_session import Session
from cryptography.fernet import Fernet
import sqlite3
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.chat.util import Chat, reflections
import threading
import time
import csv
import zipfile
import os
from config import Config

# Initialisation de l'application Flask
app = Flask(__name__)
app.config.from_object(Config)
Session(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Génération de la clé de chiffrement
cipher_suite = Fernet(Config.ENCRYPTION_KEY.encode())

# Création de la base de données
conn = sqlite3.connect(Config.DATABASE_PATH, check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """CREATE TABLE IF NOT EXISTS offres (id INTEGER PRIMARY KEY, title TEXT, company TEXT, location TEXT, encrypted TEXT)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, pin TEXT)""")
conn.commit()


# Fonction de scraping multi-plateformes
def scrape_jobs(keyword):
    jobs = []
    for platform, url_template in Config.JOB_PLATFORMS.items():
        url = url_template.format(keyword=keyword, length=len(keyword) + 7)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        if platform == "glassdoor":
            job_elements = soup.find_all("li", class_="jl")
        elif platform == "indeed":
            job_elements = soup.find_all("div", class_="job_seen_beacon")
        elif platform == "monster":
            job_elements = soup.find_all("section", class_="card-content")
        elif platform == "wttj":
            job_elements = soup.find_all("div", class_="ais-Hits-item")
        else:
            continue

        for job in job_elements:
            title = job.find("h2" if platform in ["indeed", "monster"] else "h3").text.strip()
            company = job.find("span", class_="companyName" if platform == "indeed" else "div").text.strip()
            location = "France"
            encrypted_title = cipher_suite.encrypt(title.encode()).decode()

            cursor.execute("INSERT INTO offres (title, company, location, encrypted) VALUES (?, ?, ?, ?)",
                           (title, company, location, encrypted_title))
            conn.commit()
            jobs.append({"title": title, "company": company, "location": location})

    return jobs


# Route API pour récupérer les offres filtrées
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        pin = request.form["pin"]
        cursor.execute("SELECT * FROM users WHERE username = ? AND pin = ?", (username, pin))
        user = cursor.fetchone()
        if user:
            session["user"] = username
            return redirect(url_for("chat"))
    return render_template("login.html")


@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("chat.html")


@app.route("/offres", methods=["GET"])
def get_offers():
    keyword = request.args.get("keyword", "")
    cursor.execute("SELECT title, company, location FROM offres WHERE title LIKE ?", (f"%{keyword}%",))
    offres = cursor.fetchall()
    return render_template("offres.html", offres=offres)


# Chatbot NLP
pairs = [
    ["bonjour", ["Bonjour ! Comment puis-je vous aider ?"]],
    ["je cherche un emploi", ["Quel type de poste recherchez-vous ?"]],
    ["merci", ["Je vous en prie, bonne chance dans votre recherche !"]]
]
chatbot = Chat(pairs, reflections)


@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.form["message"]
    response = chatbot.respond(user_input)
    return jsonify({"response": response})


# Sauvegarde des conversations
@app.route("/save_chat", methods=["POST"])
def save_chat():
    username = session.get("user", "guest")
    chat_data = request.json.get("chat_data", [])
    pin = request.json.get("pin", "default")

    file_path = f"{username}_chat.csv"
    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["User", "Bot"])
        writer.writerows(chat_data)

    zip_path = f"{username}_chat.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.setpassword(pin.encode())
        zipf.write(file_path)

    os.remove(file_path)
    return jsonify({"message": "Chat sauvegardé avec succès !"})


# Scraping automatique toutes les 30 minutes
def auto_scrape():
    while True:
        scrape_jobs("developer")
        socketio.emit("update", {"message": "Base de données mise à jour"})
        time.sleep(Config.SCRAPING_INTERVAL)


threading.Thread(target=auto_scrape, daemon=True).start()

# Exécution de l'application
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
