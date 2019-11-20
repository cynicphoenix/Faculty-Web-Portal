import datetime
from . import auth
import flask_pymongo
from database_mongo.database import db
from auth.forms import LoginForm, RegistrationForm
from database_postgres.database import cursor, conn
from flask import flash, redirect, render_template, url_for

username = ""
role = ""
isadmin = False

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if isadmin == False:
        flash('Unauthorized Access!')
        return redirect(url_for('user.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        cursor.execute("SELECT department_name FROM department WHERE department_id = %s", (form.department_id.data, )) # Add to postgres database
        department_name = cursor.fetchone()[0]
        cursor.execute("INSERT INTO employee(employee_id, password, first_name, last_name, email_id, department_id, date_of_joining, isadmin) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", (form.username.data, form.password.data, form.first_name.data, form.last_name.data, form.email.data, form.department_id.data, 'now()', form.isadmin.data))
        cursor.execute("INSERT INTO leaves_left(employee_id, total_leaves_left, year) VALUES(%s, %s, %s)", (form.username.data, 30, 2019))
        cursor.execute("INSERT INTO leaves_left(employee_id, total_leaves_left, year) VALUES(%s, %s, %s)", (form.username.data, 30, 2020))
        cursor.execute("INSERT INTO leaves_left(employee_id, total_leaves_left, year) VALUES(%s, %s, %s)", (form.username.data, 30, 2021))
        cursor.execute("INSERT INTO leaves_left(employee_id, total_leaves_left, year) VALUES(%s, %s, %s)", (form.username.data, 30, 2022))
        cursor.execute("INSERT INTO leaves_left(employee_id, total_leaves_left, year) VALUES(%s, %s, %s)", (form.username.data, 30, 2023))
        emp ={ # Add to monodb database
        "_id" : form.username.data, "first_name" : form.first_name.data, "last_name" : form.last_name.data, "email_id" : form.email.data,
        "department_id" : department_name, "no_awards" : 0, "no_publications" : 0, "no_researchs" : 0, "no_projects" : 0, "biography" : "",
        "education" : [], "experience" : [], "research_interests" : [], "projects" : [], "awards" : [], "publications" : [] }
        conn.commit()
        db.employee.insert_one(emp)
        flash('Employee Registered Successfully!')
        return redirect(url_for('admin.dashboard'))
    return render_template('auth/register.html', form=form, title='Register', isadmin = isadmin, username = username, role = role)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cursor.execute("SELECT employee_id FROM employee WHERE employee_id = %s", (form.username.data, ))
        if cursor.fetchone():
            cursor.execute("SELECT password FROM employee WHERE employee_id = %s", (form.username.data, ))
            if cursor.fetchone()[0] == form.password.data:
                global username
                global role
                username = form.username.data
                cursor.execute("SELECT role FROM employee WHERE employee_id = %s", (form.username.data, ))
                role = cursor.fetchone()[0]
                flash('You have successfully been successfully logged in!')
                return redirect(url_for('user.dashboard'))
        flash('Invalid email or password.')
    return render_template('auth/login.html', form=form, title='Login', isadmin = isadmin, username = username, role = role)


@auth.route('/admin/login', methods=['GET', 'POST'])
def adminlogin():
    form = LoginForm()
    if form.validate_on_submit():
        cursor.execute("SELECT employee_id FROM employee WHERE employee_id = %s", (form.username.data, ))
        if cursor.fetchone():
            cursor.execute("SELECT password FROM employee WHERE employee_id = %s", (form.username.data, ))
            if cursor.fetchone()[0] == form.password.data:
                cursor.execute("SELECT isadmin FROM employee WHERE employee_id = %s", (form.username.data, ))
                if(cursor.fetchone()[0] == True) :
                    cursor.execute("SELECT isadmin FROM employee WHERE employee_id = %s", (form.username.data, ))
                    global username
                    global role
                    global isadmin
                    role = cursor.fetchone()[0]
                    isadmin = True
                    username = form.username.data
                    flash('You have successfully been successfully logged in!')
                    return redirect(url_for('admin.dashboard'))
        flash('Invalid credentials!')
    return render_template('auth/login.html', form=form, title='Login', isadmin = isadmin, username = username, role = role)


@auth.route('/logout')
def logout():
    global username
    global isadmin
    global role
    username = ""
    role = ""
    isadmin = False
    flash('You have successfully been logged out!')
    return redirect(url_for('auth.login'))

def get_username():
    return username

def get_isadmin():
    return isadmin

def get_role():
    return role