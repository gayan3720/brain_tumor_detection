import os
from datetime import datetime
from io import BytesIO

from flask import Flask, render_template, redirect, url_for, flash, request, send_file, session, send_from_directory, \
    make_response
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import json

from forms import RegistrationForm, LoginForm, TumorPredictForm, StagePredictForm
from ml_model import predict_tumor_type_from_image, predict_tumor_stage
from utils import save_scan_file, UPLOAD_FOLDER
from bson.objectid import ObjectId

from forms     import RegistrationForm, LoginForm, TumorPredictForm, StagePredictForm
from ml_model  import predict_tumor_type_from_image, predict_tumor_stage
from utils     import save_scan_file, UPLOAD_FOLDER


# PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles   import getSampleStyleSheet
from reportlab.platypus     import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib          import colors

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize MongoDB and Login
mongo = PyMongo(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Supported classes
CLASS_NAMES = ['glioma', 'meningioma', 'no-tumor', 'pituitary']

# User model
default_age = 0
class User(UserMixin):
    def __init__(self, user_doc):
        self.id = str(user_doc['_id'])
        self.username = user_doc['username']
        self.email = user_doc['email']
        self.age = user_doc.get('age', default_age)
        self.sex = user_doc.get('sex', '')
        self.password_hash = user_doc['password_hash']

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    user_doc = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    return User(user_doc) if user_doc else None

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_doc = mongo.db.users.find_one({'username': form.username.data})
        if user_doc and check_password_hash(user_doc['password_hash'], form.password.data):
            login_user(User(user_doc))
            return redirect(url_for('tumor_predict'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if mongo.db.users.find_one({'username': form.username.data}):
            flash('Username exists', 'warning')
        else:
            mongo.db.users.insert_one({
                'username': form.username.data,
                'email': form.email.data,
                'password_hash': generate_password_hash(form.password.data),
                'age': form.age.data,
                'sex': form.sex.data
            })
            flash('Registration complete. Login now.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/tumor_predict', methods=['GET', 'POST'])
@login_required
def tumor_predict():
    form = TumorPredictForm()
    prediction = None
    if form.validate_on_submit():
        scan_file = form.scan.data
        try:
            tumor_idx, confidence, saved_path = predict_tumor_type_from_image(scan_file, UPLOAD_FOLDER)
            tumor_idx = int(tumor_idx)
            confidence = float(confidence)
            ttype = CLASS_NAMES[tumor_idx]
            # save history
            mongo.db.patient_history.insert_one({
                'user_id': current_user.id,
                'tumor_type': ttype,
                'confidence': confidence,
                'image_path': saved_path,
                'created_at': datetime.utcnow()
            })
            prediction = {'tumor_type': ttype, 'confidence': confidence}
            session['predicted_tumor_type'] = ttype
            flash(f'{ttype.title()} detected ({confidence:.1f}%)', 'success')
        except Exception:
            flash('Processing error', 'danger')
    return render_template('tumor_predict.html', form=form, prediction=prediction)

@app.route('/stage_predict', methods=['GET','POST'])
@login_required
def stage_predict():
    form = StagePredictForm()
    result = None
    features_json = None

    # Prefill tumor type
    if 'predicted_tumor_type' in session:
        form.tumor_type.data = session['predicted_tumor_type']

    if form.validate_on_submit():
        # 1) Build features dict
        features = {
            'total_volume':     form.total_volume.data,
            'edema_volume':     form.edema_volume.data,
            'necrosis_volume':  form.necrosis_volume.data or 0.0,
            'enhancing_volume': form.enhancing_volume.data,
            'centroid_x':       form.centroid_x.data,
            'centroid_y':       form.centroid_y.data,
            'centroid_z':       form.centroid_z.data
        }

        # 2) Predict stage & rec
        stage, rec = predict_tumor_stage(form.tumor_type.data, features)

        # 3) Compare to previous record
        history = list(mongo.db.stages.find({
            'user_id': current_user.id,
            'tumor_type': form.tumor_type.data
        }).sort('created_at', -1).limit(2))
        if len(history) == 2:
            # history[0] is current we just inserted next, so previous=history[1]
            prev_stage = history[1]['stage']
            order = {'Stage I':1,'Stage II':2,'Stage III':3,'Stage IV':4}
            diff = order[stage] - order.get(prev_stage, order[stage])
            if diff > 0:
                status = "Worsened since last time"
            elif diff < 0:
                status = "Improved since last time"
            else:
                status = "Unchanged since last time"
        else:
            status = "No prior record"

        # 4) Persist this stage
        mongo.db.stages.insert_one({
            'user_id':    current_user.id,
            'tumor_type': form.tumor_type.data,
            'stage':      stage,
            'features':   features,
            'rec':        rec,
            'status':     status,
            'created_at': datetime.utcnow()
        })

        # 5) Prepare result for template + PDF
        result = {
            'stage':    stage,
            'rec':      rec,
            'features': features,
            'status':   status
        }
        features_json = json.dumps(features)

    return render_template(
        'stage_predict.html',
        form=form,
        result=result,
        features_json=features_json
    )


@app.route('/download_stage_report', methods=['POST'])
@login_required
def download_stage_report():
    tumor_type = request.form['tumor_type']
    stage      = request.form['stage']
    features   = json.loads(request.form['features'])
    rec_text   = request.form['rec']
    status     = request.form.get('status', '')

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=60, bottomMargin=40)
    styles = getSampleStyleSheet()
    elems  = []

    # Title
    elems.append(Paragraph("NeuroScan AI — Tumor Stage Report", styles['Title']))
    elems.append(Spacer(1, 12))

    # Metadata
    meta = [
        ['Patient',        current_user.username],
        ['Date',           datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')],
        ['Tumor Type',     tumor_type.title()],
        ['Predicted Stage',stage],
        ['Status Change',  status]
    ]
    table = Table(meta, colWidths=[120, 300], hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
        ('GRID',        (0,0), (-1,-1), 0.5, colors.gray),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
    ]))
    elems.extend([table, Spacer(1, 20)])

    # Features
    feat_rows = [['Feature','Value']] + [
        [k.replace('_',' ').title(), str(v)] for k,v in features.items()
    ]
    ft = Table(feat_rows, colWidths=[200,200], hAlign='LEFT')
    ft.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
        ('GRID',        (0,0), (-1,-1), 0.5, colors.gray),
    ]))
    elems.extend([Paragraph("Volumetric Features", styles['Heading2']), ft, Spacer(1, 20)])

    # Recommendations
    elems.append(Paragraph("Expert Recommendations", styles['Heading2']))
    for line in rec_text.split('\n'):
        elems.extend([Paragraph(line, styles['BodyText']), Spacer(1,4)])

    doc.build(elems)
    buffer.seek(0)

    resp = make_response(buffer.read())
    resp.headers.set('Content-Type','application/pdf')
    resp.headers.set(
        'Content-Disposition',
        'attachment; filename=' + f"{tumor_type}_{stage}_report.pdf"
    )
    return resp


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)