# ml_model.py
import os
import numpy as np
import joblib
import pandas as pd
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import load_model
from expert_recs import get_expert_recommendation

# Load your trained pipeline and label encoder (adjust paths if needed)
_pipeline_path = os.path.join(os.path.dirname(__file__), 'models', 'tumor_stage','tumor_stage_pipeline.pkl')
_encoder_path  = os.path.join(os.path.dirname(__file__),'models','tumor_stage','stage_label_encoder.pkl')

clf = joblib.load(_pipeline_path)
le  = joblib.load(_encoder_path)



# Assume 'model' is your loaded ML model already initialized somewhere here or imported
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'tumor_type','brain_tumor_classification_model.h5')
model = load_model(MODEL_PATH)
def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def predict_tumor_type_from_image(file_storage, upload_folder):
    """
    file_storage: werkzeug FileStorage object from Flask (uploaded file)
    upload_folder: string path to save the file

    Returns:
      tumor_type (int or string label),
      confidence (float),
      saved file path (str)
    """

    if not allowed_file(file_storage.filename):
        raise ValueError("Invalid file format. Please upload a valid image.")

    # Secure and save the file
    from werkzeug.utils import secure_filename
    filename = secure_filename(file_storage.filename)
    file_path = os.path.join(upload_folder, filename)
    file_storage.save(file_path)

    # Preprocess image
    img = load_img(file_path, target_size=(224, 224))
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Predict
    predictions = model.predict(img_array)
    tumor_type_idx = np.argmax(predictions[0])
    confidence = predictions[0][tumor_type_idx] * 100

    # You may want to map tumor_type_idx to string label here, e.g.
    # tumor_type = CLASS_NAMES[tumor_type_idx]

    return tumor_type_idx, confidence, file_path


def predict_tumor_stage(tumor_type: str, features: dict):
    """
    Predict tumor stage and return expert recommendation.

    Parameters
    ----------
    tumor_type : str
        One of 'glioma', 'meningioma', 'pituitary'.
    features : dict
        Keys must include:
          - total_volume, edema_volume, necrosis_volume,
            enhancing_volume, centroid_x, centroid_y, centroid_z

    Returns
    -------
    stage : str
        e.g. "Stage II"
    recommendation : str
        The clinical text from your expert system.
    """
    # Build a single‐row DataFrame
    df = pd.DataFrame([{
        'tumor_type':      tumor_type,
        'total_volume':     features['total_volume'],
        'edema_volume':     features['edema_volume'],
        'necrosis_volume':  features['necrosis_volume'],
        'enhancing_volume': features['enhancing_volume'],
        'centroid_x':       features['centroid_x'],
        'centroid_y':       features['centroid_y'],
        'centroid_z':       features['centroid_z'],
    }])

    # Predict encoded stage (0–3)
    pred_enc = clf.predict(df)[0]
    # Convert back to "Stage I" … "Stage IV"
    stage = le.inverse_transform([pred_enc])[0]

    # Fetch expert recommendation
    recommendation = get_expert_recommendation(tumor_type, stage)

    return stage, recommendation
