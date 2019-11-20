from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
from database_postgres.database import cursor


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    department_id = StringField('Department', validators=[DataRequired()])
    isadmin = SelectField('Admin Rights', choices = [('False', 'False'), ('True', 'True')])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_department_id(self, field):
       cursor.execute("SELECT department_id FROM department WHERE department_id = %s", (field.data,))
       if (cursor.fetchone() is None):
           raise ValidationError('Department does not exist!')

    def validate_username(self, field):
        cursor.execute("SELECT employee_id FROM employee WHERE employee_id = %s", (field.data,))
        if cursor.fetchone():
            raise ValidationError('Username is already in use!')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')