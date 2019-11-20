from flask import render_template
from database_mongo.database import db
from database_postgres.database import cursor
from auth.views import get_username, get_isadmin, get_role
from . import about
    

@about.route('/employees', methods=['GET', 'POST'])
def employees():
    cursor.execute("SELECT * FROM employee ORDER BY employee_id ASC ")
    employees = cursor.fetchall()
    cursor.execute("SELECT * FROM department WHERE department_id != 'NONE' ORDER BY department_id ASC")
    departments = cursor.fetchall()
    return render_template('about/employees.html', title='Employees', employees = employees, departments = departments, username = get_username(), isadmin = get_isadmin(), role = get_role())

@about.route('/about/<user>', methods=['GET', 'POST'])
def about(user):
    emp = db.employee.find_one({"_id" : user})
    first_name = emp['first_name']
    last_name = emp['last_name']
    email_id = emp['email_id']
    department_id = emp['department_id']

    no_awards = emp['no_awards']
    no_publications = emp['no_publications']
    no_researchs = emp['no_researchs']
    no_projects = emp['no_projects']
    biography = emp['biography']
    
    education = emp['education']
    experience = emp['experience']
    research_interests = emp['research_interests']
    projects = emp['projects']
    awards = emp['awards']
    publications = emp['publications']

    return render_template('about/employee.html', first_name = first_name, last_name = last_name, email_id = email_id, department_id = department_id,
                        no_awards = no_awards, no_publications = no_publications, no_researchs = no_researchs, no_projects = no_projects,
                        biography = biography, education = education, experience = experience, research_interests = research_interests,
                        projects = projects, publications = publications, awards = awards, title='About', username = get_username(), isadmin = get_isadmin(), role = get_role())



