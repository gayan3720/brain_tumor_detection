# Enhanced synthetic data generation
import numpy as np
import pandas as pd


def generate_tumor_data(n_samples=10000, random_state=42):
    np.random.seed(random_state)

    # Tumor characteristics with more diversity
    characteristics = {
        'tumor_type': ['glioma', 'meningioma', 'pituitary', 'metastatic', 'schwannoma'],
        'size': ['very_small', 'small', 'medium', 'large', 'very_large'],
        'location': ['frontal', 'temporal', 'parietal', 'occipital', 'cerebellum', 'brainstem'],
        'edema': [0, 1],
        'necrosis': [0, 1],
        'enhancement': ['none', 'mild', 'moderate', 'strong', 'ring'],
        'shape': ['regular', 'irregular'],
        'margins': ['well_defined', 'poorly_defined'],
        'calcification': [0, 1],
        'cystic_components': [0, 1],
        'hemorrhage': [0, 1],
        'ki67_index': np.linspace(0, 100, 21),  # Proliferation marker
        'mitotic_count': np.arange(0, 21)  # Mitotic figures per HPF
    }

    # Patient characteristics
    patient_chars = {
        'age': np.arange(18, 91),
        'gender': ['male', 'female'],
        'symptoms_duration': np.arange(1, 365),  # Days
        'neurological_deficit': [0, 1],
        'kps_score': np.arange(40, 101, 10)  # Karnofsky Performance Status
    }

    data = []

    for _ in range(n_samples):
        # Tumor characteristics
        tumor_type = np.random.choice(characteristics['tumor_type'])
        size = np.random.choice(characteristics['size'])
        location = np.random.choice(characteristics['location'])
        edema = np.random.choice(characteristics['edema'])
        necrosis = np.random.choice(characteristics['necrosis'])
        enhancement = np.random.choice(characteristics['enhancement'])
        shape = np.random.choice(characteristics['shape'])
        margins = np.random.choice(characteristics['margins'])
        calcification = np.random.choice(characteristics['calcification'])
        cystic_components = np.random.choice(characteristics['cystic_components'])
        hemorrhage = np.random.choice(characteristics['hemorrhage'])
        ki67_index = np.random.choice(characteristics['ki67_index'])
        mitotic_count = np.random.choice(characteristics['mitotic_count'])

        # Patient characteristics
        age = np.random.choice(patient_chars['age'])
        gender = np.random.choice(patient_chars['gender'])
        symptoms_duration = np.random.choice(patient_chars['symptoms_duration'])
        neurological_deficit = np.random.choice(patient_chars['neurological_deficit'])
        kps_score = np.random.choice(patient_chars['kps_score'])

        # Determine stage based on complex rules
        stage = determine_stage(
            tumor_type, size, location, edema, necrosis, enhancement, shape,
            margins, calcification, cystic_components, hemorrhage, ki67_index,
            mitotic_count, age, kps_score
        )

        data.append([
            tumor_type, size, location, edema, necrosis, enhancement, shape,
            margins, calcification, cystic_components, hemorrhage, ki67_index,
            mitotic_count, age, gender, symptoms_duration, neurological_deficit,
            kps_score, stage
        ])

    # Create DataFrame
    columns = [
        'tumor_type', 'size', 'location', 'edema', 'necrosis', 'enhancement', 'shape',
        'margins', 'calcification', 'cystic_components', 'hemorrhage', 'ki67_index',
        'mitotic_count', 'age', 'gender', 'symptoms_duration', 'neurological_deficit',
        'kps_score', 'stage'
    ]

    return pd.DataFrame(data, columns=columns)


def determine_stage(tumor_type, size, location, edema, necrosis, enhancement, shape,
                    margins, calcification, cystic_components, hemorrhage, ki67_index,
                    mitotic_count, age, kps_score):
    """Enhanced staging rules with probabilistic outcomes"""
    # Base score based on tumor type
    base_scores = {
        'glioma': 0, 'meningioma': 0, 'pituitary': 1, 'metastatic': 3, 'schwannoma': 1
    }
    score = base_scores[tumor_type]

    # Size scoring
    size_scores = {
        'very_small': 0, 'small': 1, 'medium': 2, 'large': 3, 'very_large': 4
    }
    score += size_scores[size]

    # Location scoring
    location_scores = {
        'frontal': 0, 'temporal': 0, 'parietal': 1, 'occipital': 1,
        'cerebellum': 2, 'brainstem': 3
    }
    score += location_scores[location]

    # Additional feature scoring
    score += edema * 1.5
    score += necrosis * 2
    score += calcification * 0.5
    score += cystic_components * 1
    score += hemorrhage * 1.5

    # Enhancement scoring
    enhancement_scores = {
        'none': 0, 'mild': 1, 'moderate': 2, 'strong': 3, 'ring': 4
    }
    score += enhancement_scores[enhancement]

    # Shape and margins
    score += 1 if shape == 'irregular' else 0
    score += 1.5 if margins == 'poorly_defined' else 0

    # Biological markers
    score += ki67_index / 20
    score += mitotic_count / 2

    # Age factor
    score += max(0, (age - 50) / 20)

    # Performance status adjustment
    score -= (100 - kps_score) / 50

    # Probabilistic staging with some randomness
    if score < 5:
        stage = 'I'
    elif score < 10:
        stage = 'II'
    elif score < 15:
        stage = 'III'
    else:
        stage = 'IV'

    # Add some randomness to simulate real-world variability
    if np.random.random() < 0.1:  # 10% chance of misclassification
        stages = ['I', 'II', 'III', 'IV']
        stages.remove(stage)
        stage = np.random.choice(stages)

    return stage


# %%
# Generate enhanced dataset
df = generate_tumor_data(n_samples=10000)
df.to_csv('brain_tumor_stages_enhanced.csv', index=False)