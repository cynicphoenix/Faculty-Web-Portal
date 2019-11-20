from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, TextField, SelectField, PasswordField
from wtforms.validators import DataRequired
from database_postgres.database import cursor


class AddDepartmentForm(FlaskForm):
    department_id = StringField('Department ID', validators=[DataRequired()])
    department_name = StringField('Department Name', validators=[DataRequired()])
    submit = SubmitField('Save Changes')

    def validate_department_id(self, field):
        cursor.execute("SELECT department_id FROM department WHERE department_id = %s", (field.data,))
        if cursor.fetchone():
            raise ValidationError('Department already exist!')


class AddPositionForm(FlaskForm):
    position_id = StringField('Position ID', validators=[DataRequired()])
    position_name = StringField('Position Name', validators=[DataRequired()])
    submit = SubmitField('Save Changes')

    def validate_position_id(self, field):
        cursor.execute("SELECT position FROM pos WHERE position = %s", (field.data,))
        if cursor.fetchone():
            raise ValidationError('Position already exist!')


class AddRouteForm(FlaskForm):
    role = StringField('Role', validators=[DataRequired()])
    start_route = StringField('From', validators=[DataRequired()])
    end_route = StringField('To', validators=[DataRequired()])
    submit = SubmitField('Add Route')


class AddHODForm(FlaskForm):
    department_id = StringField('Department ID', validators=[DataRequired()]) 
    hod_id = StringField('Employee ID', validators=[DataRequired()])
    submit = SubmitField('Save Changes!')

    def validate_department_id(self, field):
        cursor.execute("SELECT department_id FROM department WHERE department_id = %s", (field.data,))
        if cursor.fetchone() == None:
            raise ValidationError('Department does not exist!')
        
        cursor.execute("SELECT department_id FROM hod WHERE department_id = %s", (field.data,))
        if cursor.fetchone():
            raise ValidationError('HOD already appointed!')

    def validate_hod_id(self, field):
        cursor.execute("SELECT employee_id FROM employee WHERE employee_id = %s", (field.data,))
        if cursor.fetchone() == None:
            raise ValidationError('Employee does not exists!')


class EditHODForm(FlaskForm):
    hod_id = StringField('Employee ID', validators=[DataRequired()])
    submit = SubmitField('Save Changes!')

    def validate_hod_id(self, field):
        cursor.execute("SELECT employee_id FROM employee WHERE employee_id = %s", (field.data,))
        if cursor.fetchone() == None:
            raise ValidationError('Employee does not exists!')

        cursor.execute("SELECT role FROM employee WHERE employee_id = %s", (field.data,))
        if cursor.fetchone()[0] != 'FACULTY':
            raise ValidationError('Employee already holds another position!')


class AddCCFForm(FlaskForm):
    position = StringField('Position ID', validators=[DataRequired()])
    employee_id = StringField('Employee ID', validators=[DataRequired()])
    submit = SubmitField('Add Position')

    def validate_position(self, field):
        cursor.execute("SELECT position FROM pos WHERE position = %s", (field.data,))
        if cursor.fetchone() == None:
            raise ValidationError('Position does not exist!')
        
        cursor.execute("SELECT position FROM ccf WHERE position = %s", (field.data,))
        if cursor.fetchone():
            raise ValidationError('Position already appointed!')

    def validate_employee_id(self, field):
        cursor.execute("SELECT employee_id FROM employee WHERE employee_id = %s", (field.data,))
        if cursor.fetchone() == None :
            raise ValidationError('Employee does not exists!')
    

class EditCCFForm(FlaskForm):
    employee_id = StringField('Employee ID', validators=[DataRequired()])
    submit = SubmitField('Save Changes!')

    def validate_employee_id(self, field):
        cursor.execute("SELECT employee_id FROM employee WHERE employee_id = %s", (field.data,))
        if cursor.fetchone() == None:
            raise ValidationError('Employee does not exists!')

        cursor.execute("SELECT role FROM employee WHERE employee_id = %s", (field.data,))
        if cursor.fetchone()[0] != 'FACULTY':
            raise ValidationError('Employee already holds another position!')