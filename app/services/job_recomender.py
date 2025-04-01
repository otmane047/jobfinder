import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def prepare_data(user, jobs):
    data = []
    education_levels = {'Licence': 1, 'Bachelor': 1, 'Master': 2, 'Doctorat': 3}

    for job in jobs:
        # Gestion robuste des compétences
        user_skills = set(skill.lower() for skill in user['skills'])
        job_skills = set(skill.lower() for skill in job['required_skills'])

        common_skills = user_skills.intersection(job_skills)
        total_skills = len(job['required_skills']) if job['required_skills'] else 1
        skill_match = len(common_skills) / total_skills

        features = {
            'education_diff': education_levels[user['education_level']] - education_levels[job['required_education']],
            'experience_diff': user['experience'] - job['required_experience'],
            'salary_match': 1 if job['salary_range'][0] <= user['desired_salary'] <= job['salary_range'][1] else 0,
            'location_match': 1 if user['location'] == job['location'] else 0,
            'contract_match': 1 if user['contract_type'] == job['contract_type'] else 0,
            'skill_match': skill_match
        }
        data.append(features)

    return pd.DataFrame(data)


def predict(user_profile, jobs):
    df = prepare_data(user_profile, jobs)

    numeric_features = ['education_diff', 'experience_diff', 'skill_match']
    binary_features = ['salary_match', 'location_match', 'contract_match']

    preprocessor = ColumnTransformer([
        ('num', StandardScaler(), numeric_features),
        ('bin', 'passthrough', binary_features)
    ])

    knn = Pipeline([
        ('preprocessor', preprocessor),
        ('knn', NearestNeighbors(n_neighbors=min(5, len(jobs))))
    ]).fit(df)

    user_features = {
        'education_diff': 0,
        'experience_diff': 0,
        'salary_match': 1,
        'location_match': 1,
        'contract_match': 1,
        'skill_match': 1
    }

    user_df = pd.DataFrame([user_features])
    distances, indices = knn.named_steps['knn'].kneighbors(
        knn.named_steps['preprocessor'].transform(user_df)
    )

    return indices[0]  # Retourne les indices des offres recommandées