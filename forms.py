from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import PasswordField, StringField, SubmitField, IntegerField , FloatField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length,NumberRange,Optional

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    age = IntegerField('Age', validators=[DataRequired()])
    sex = SelectField('Sex', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TumorPredictForm(FlaskForm):
    scan = FileField(
        'Tumor Scan Image',
        validators=[
            FileRequired(),
            FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
        ]
    )
    submit = SubmitField('Predict')

class StagePredictForm(FlaskForm):
    tumor_type = SelectField(
        'Tumor Type',
        choices=[
            ('glioma', 'Glioma'),
            ('meningioma', 'Meningioma'),
            ('pituitary', 'Pituitary')
        ],
        validators=[DataRequired(message="Please select a tumor type.")]
    )
    total_volume = FloatField(
        'Total Volume (cm³)',
        validators=[
            DataRequired(message="Please enter the total tumor volume."),
            NumberRange(min=0.0, message="Volume must be non-negative.")
        ]
    )
    edema_volume = FloatField(
        'Edema Volume (cm³)',
        validators=[
            DataRequired(message="Please enter the edema volume."),
            NumberRange(min=0.0, message="Volume must be non-negative.")
        ]
    )
    necrosis_volume = FloatField(
        'Necrosis Volume (cm³)',
        validators=[
            Optional(),
            NumberRange(min=0.0, message="Volume must be non-negative.")
        ]
    )
    enhancing_volume = FloatField(
        'Enhancing Volume (cm³)',
        validators=[
            DataRequired(message="Please enter the enhancing volume."),
            NumberRange(min=0.0, message="Volume must be non-negative.")
        ]
    )
    centroid_x = FloatField(
        'Centroid X (0–1)',
        validators=[
            DataRequired(message="Please provide centroid X coordinate."),
            NumberRange(min=0.0, max=1.0, message="Must be between 0 and 1.")
        ]
    )
    centroid_y = FloatField(
        'Centroid Y (0–1)',
        validators=[
            DataRequired(message="Please provide centroid Y coordinate."),
            NumberRange(min=0.0, max=1.0, message="Must be between 0 and 1.")
        ]
    )
    centroid_z = FloatField(
        'Centroid Z (0–1)',
        validators=[
            DataRequired(message="Please provide centroid Z coordinate."),
            NumberRange(min=0.0, max=1.0, message="Must be between 0 and 1.")
        ]
    )
    submit = SubmitField('Predict Stage')
