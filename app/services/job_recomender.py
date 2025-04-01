import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

## 1. Données d'exemple
user_profile = {
    'age': 28,
    'education_level': 'Master',
    'experience': 4,
    'desired_salary': 45000,
    'contract_type': 'CDI',
    'location': 'Paris',
    'skills': ['Python', 'Machine Learning', 'SQL', 'Pandas', 'Analyse de données']
}

jobs = [
    {
        'title': 'Data Scientist Senior',
        'required_education': 'Master',
        'required_experience': 5,
        'salary_range': (40000, 60000),
        'contract_type': 'CDI',
        'location': 'Paris',
        'required_skills': ['Python', 'Machine Learning', 'SQL', 'Big Data']
    },
    {
        'title': 'Data Analyst',
        'required_education': 'Licence',
        'required_experience': 2,
        'salary_range': (30000, 40000),
        'contract_type': 'CDD',
        'location': 'Lyon',
        'required_skills': ['Python', 'SQL', 'Excel', 'Tableau']
    }
]


## 2. Fonction de préparation des données corrigée
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


## 3. Application
df = prepare_data(user_profile, jobs)
print("Features calculées:\n", df.head())

## 4. Pipeline KNN
numeric_features = ['education_diff', 'experience_diff', 'skill_match']
binary_features = ['salary_match', 'location_match', 'contract_match']

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), numeric_features),
    ('bin', 'passthrough', binary_features)
])

knn = Pipeline([
    ('preprocessor', preprocessor),
    ('knn', NearestNeighbors(n_neighbors=1))
]).fit(df)

## 5. Exemple d'utilisation
user_features = {
    'education_diff': 0,  # Master - Master = 0
    'experience_diff': -1,  # 4 - 5 = -1
    'salary_match': 1,
    'location_match': 1,
    'contract_match': 1,
    'skill_match': 0.75  # 3/4 skills matchés
}

user_df = pd.DataFrame([user_features])
distances, indices = knn.named_steps['knn'].kneighbors(
    knn.named_steps['preprocessor'].transform(user_df)
)

print("\nJob le plus similaire:", jobs[indices[0][0]]['title'])