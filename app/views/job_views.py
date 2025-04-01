import csv
import os

import pandas as pd
from flask import Blueprint, render_template, request, jsonify

from app.controllers.job_controller import JobController
from app.middleware.session_auth import login_required
from app.services.job_recomender import predict

job_bp = Blueprint('job_bp', __name__)


@job_bp.route("/")
def index():
    return render_template("index.html")


@job_bp.route("/offres", methods=["GET"])
@login_required
def get_offers():
    keyword = request.args.get("keyword", "").lower()
    jobs = JobController.get_jobs(keyword)

    # Convertir en DataFrame
    df = pd.DataFrame(jobs)

    # Vérifier si le DataFrame est vide
    if df.empty:
        return render_template('offres.html', offres=[], recommended_offers=[])

    # Filtrage par mot-clé
    mask = (
            df['Title'].str.lower().str.contains(keyword, na=False) |
            df['Company'].str.lower().str.contains(keyword, na=False) |
            df['Location'].str.lower().str.contains(keyword, na=False)
    )
    filtered_jobs = df[mask]

    # Vérifier à nouveau après filtrage
    if filtered_jobs.empty:
        return render_template('offres.html', offres=[], recommended_offers=[])

    filtered_jobs = filtered_jobs.to_dict('records')

    # Récupérer le profil utilisateur (adaptez selon votre système)
    user_profile = {
        'education_level': 'Master',  # À remplacer par les vraies données
        'experience': 4,
        'desired_salary': 50000,
        'location': 'Paris',
        'contract_type': 'CDI',
        'skills': ['Python', 'Machine Learning', 'Data Analysis']
    }

    # Préparer les données pour la recommandation
    try:
        # Préparer les données des jobs pour la prédiction
        jobs_for_prediction = []
        for job in filtered_jobs:
            jobs_for_prediction.append({
                'required_skills': job.get('Skills', []),
                'required_education': job.get('Education', 'Master'),
                'required_experience': job.get('Experience', 3),
                'salary_range': [job.get('SalaryMin', 30000), job.get('SalaryMax', 70000)],
                'location': job.get('Location', 'Paris'),
                'contract_type': job.get('Employment Type', 'CDI'),
                'title': job.get('Title', ''),
                'company': job.get('Company', ''),
                'job_url': job.get('Job URL', '')
            })

        # Trouver les offres recommandées
        recommended_indices = predict(user_profile, jobs_for_prediction)
        recommended_offers = [filtered_jobs[i] for i in recommended_indices]
    except Exception as e:
        print(f"Erreur dans le système de recommandation: {e}")
        recommended_offers = []

    return render_template('offres.html',
                           offres=filtered_jobs,
                           recommended_offers=recommended_offers,
                           keyword=keyword)
@job_bp.route('/api/offres', methods=['GET'])
def get_offers_api():
    try:
        csv_file = 'linkedin_jobs.csv'

        if not os.path.exists(csv_file):
            return jsonify({'error': 'CSV file not found'}), 404

        jobs = []

        with open(csv_file, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                jobs.append(row)

        return jsonify(jobs)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
