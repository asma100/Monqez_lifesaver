from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Optional
from flask_wtf import FlaskForm
from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, SelectField, SubmitField
from wtforms.validators import DataRequired


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class VolunteerForm(FlaskForm):
    name = StringField("الاسم (اختياري)")
    phone_number = StringField("رقم الهاتف", validators=[DataRequired()])
    
    available_days = SelectMultipleField(
        "الأيام المتاحة",
        choices=[('Saturday', 'السبت'), ('Sunday', 'الأحد'), ('Monday', 'الاثنين'), 
                 ('Tuesday', 'الثلاثاء'), ('Wednesday', 'الأربعاء'), 
                 ('Thursday', 'الخميس'), ('Friday', 'الجمعة')],
        validators=[DataRequired()]
    )

    available_times = SelectField(
        "الفترة الزمنية المتاحة",
        choices=[
            ("08:00-12:00", "٨ صباحًا - ١٢ ظهرًا"),
            ("12:00-16:00", "١٢ ظهرًا - ٤ مساءً"),
            ("16:00-20:00", "٤ مساءً - ٨ مساءً"),
            ("20:00-00:00", "٨ مساءً - ١٢ منتصف الليل"),
            ("00:00-08:00", "١٢ منتصف الليل - ٨ صباحًا")

        ],
        validators=[DataRequired()]
    )

    specialty = StringField("التخصص")
    submit = SubmitField("حفظ البيانات")

