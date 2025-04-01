import csv
import os

import pandas as pd
from flask import Blueprint, render_template, request, jsonify

from app.controllers.job_controller import JobController

job_bp = Blueprint('job_bp', __name__)


@job_bp.route("/")
def index():
    return render_template("index.html")


@job_bp.route("/offres", methods=["GET"])
def get_offers():
    keyword = request.args.get("keyword", "").lower()
    jobs = JobController.get_jobs(keyword)
    df = pd.DataFrame(jobs)

    # jobs = pd.read_csv('linkedin_jobs.csv', encoding='utf-8')


    expected_columns = {'Title', 'Company', 'Location', 'Posted Time', 'Job URL', 'Employment Type'}
    available_columns = set(df.columns)

    if not expected_columns.issubset(available_columns):
        return render_template('offres.html', offres=[])

    mask = (
        jobs['Title'].str.lower().str.contains(keyword, na=False) |
        jobs['Company'].str.lower().str.contains(keyword, na=False) |
        jobs['Location'].str.lower().str.contains(keyword, na=False)
    )
    df = jobs[mask]

    df = df[['Title', 'Company', 'Location', 'Posted Time', 'Job URL', 'Employment Type']]
    offres = df.to_dict('records')

    return render_template('offres.html', offres=offres)


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
