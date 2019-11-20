from flask_wtf import FlaskForm
from datetime import date
from wtforms import PasswordField, StringField, SubmitField, ValidationError, DateField, SelectField, TextAreaField, TextField, IntegerField
from wtforms.validators import DataRequired, EqualTo
from wtforms.fields.html5 import DateField

class LeaveApplicationForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    leave_type = SelectField('Leave Type', choices = [('Regular', 'Regular'),('Borrowing','Borrow from Next Year')])
    application = TextAreaField('Application', validators=[DataRequired()])
    submit = SubmitField('Apply for Leave!')

class commentFormLower(FlaskForm):
    comment = TextAreaField('Comment')
    submit = SubmitField('Submit!')

class commentFormHigher(FlaskForm):
    comment = TextField('Comment')
    action = SelectField('Action', choices = [('forward','Grant/Forward'),('reject','Reject'),('send_back','Send Back')])
    submit = SubmitField('Submit!')

class EditDetailsForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email_id = StringField('Email ID', validators=[DataRequired()])
    biography = TextAreaField('Biography')
    no_awards = IntegerField('Awards Won')
    no_publications = IntegerField('Total Publications')
    no_researchs = IntegerField('Reseach Output')
    no_projects = IntegerField('Projects Done')
    submit = SubmitField('Save Changes')

class AddDetailsForm(FlaskForm):
    add = TextField('Specification', validators=[DataRequired()])
    submit = SubmitField('Save Changes')