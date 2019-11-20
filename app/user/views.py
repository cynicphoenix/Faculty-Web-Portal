import datetime
from . import user
from database_mongo.database import db
from auth.views import get_username, get_isadmin, get_role
from database_postgres.database import cursor, conn
from flask import abort, flash, redirect, render_template, url_for
from user.forms import LeaveApplicationForm, EditDetailsForm, commentFormLower, commentFormHigher, AddDetailsForm


@user.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if (get_username() == ""):
        flash ("Please Login!")
        return redirect(url_for('auth.login'))
    return render_template('/user/dashboard.html', title = "Dashboard", username = get_username(), isadmin = get_isadmin(), role = get_role())

@user.route('/application', methods=['GET', 'POST'])
def new_application():
    if (get_username() == ""):
        flash ("Please Login!")
        return redirect(url_for('auth.login'))
    username = get_username()
    # Check if user is trying to gnerate more than one requests
    cursor.execute("SELECT status FROM leave_application WHERE employee_id = %s ORDER BY leave_id DESC", (username,))
    status = cursor.fetchone()
    if status :
        if status[0] != 'Granted' and status[0] != 'Rejected':
            flash("Can't apply For leave as last leave is pending!")
            return redirect(url_for('user.dashboard', username = username, isadmin = get_isadmin()))
    
    form = LeaveApplicationForm()
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        application = form.application.data
        leave_type = form.leave_type.data
        now = datetime.datetime.now()
        curr_year = int(now.year)

        cursor.execute("SELECT total_leaves_left FROM leaves_left WHERE employee_id = %s AND year = %s", (username, curr_year))
        total_leaves_left = cursor.fetchone()[0]

        leaves_demanded = int((end_date - start_date).days) + 1
        if(total_leaves_left - leaves_demanded < -10 and leave_type == "Borrowing"):
            flash ("Invalid Application! You can atmax borrow 10 leaves from upcoming year!")
            return redirect(url_for('home.error'))

        if(total_leaves_left - leaves_demanded < 0 and leave_type == "Regular"):
            flash ("Invalid Application! You can't apply for this much leaves! You can try borrowing leaves!")
            return redirect(url_for('home.error'))
        
        # Check type of Leave 
        if(total_leaves_left - leaves_demanded < 0):
            leave_type = 'Borrowing'
        else:
            leave_type = 'Regular'
        status = 'Waiting'  

        cursor.execute("SELECT end_route FROM route WHERE role = %s AND start_route = %s", (get_role(), get_role()))
        to = cursor.fetchone()

        if to is None:
            flash("Route is not defined for you! Please contact admin!")
            return redirect(url_for('home.error'))
        cursor.execute("SELECT department_id FROM employee WHERE employee_id = %s", (username,))
        department_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO leave_application(employee_id, applied_date, leave_type, start_date, end_date, status, application, department_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", (username, 'now()', leave_type, start_date, end_date, status, application, department_id))
        cursor.execute("SELECT leave_id FROM leave_application WHERE employee_id = %s ORDER BY leave_id DESC", (username,))
        leave_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO leave_requests(role, leave_id, department_id) VALUES(%s, %s, %s)", (to[0], leave_id, department_id))
        conn.commit()
        flash ("Application Sent!")
        return redirect(url_for('user.dashboard', username = username))
    return render_template('user/leaves/new_application.html', form=form, title="New Application" , username = username, isadmin = get_isadmin(), role = get_role())



@user.route('/myapplications', methods=['GET', 'POST'])
def my_applications():
    if (get_username() == ""):
        flash ("Please Login!")
        return redirect(url_for('auth.login'))
    username = get_username()
    cursor.execute("SELECT * FROM leave_application WHERE employee_id = %s ORDER BY leave_id DESC", (username,))
    leaves = cursor.fetchall()
    cursor.execute("SELECT * FROM comments ORDER BY leave_id DESC")
    comments = cursor.fetchall()
    cursor.execute("SELECT * FROM leaves_left WHERE employee_id = %s ORDER BY year ASC", (username,))
    leaves_left = cursor.fetchall()
    return render_template('user/leaves/my_applications.html', leaves = leaves, comments = comments, leaves_left = leaves_left, title="My Application" , username = username, isadmin = get_isadmin(), role = get_role())


@user.route('/action/<leave_id>', methods=['GET', 'POST'])
def action(leave_id):
    if (get_username() == ""):
        flash ("Please Login!")
        return redirect(url_for('auth.login'))
    username = get_username()
    form = commentFormHigher()
    cursor.execute("SELECT leave_id FROM leave_requests WHERE role = %s AND leave_id = %s", (get_role(), leave_id))
    id = cursor.fetchone()
    if id is None:
        flash ("Error : Unauthorized Access!")
        return redirect(url_for('home.error'))

    if form.validate_on_submit():
        cursor.execute("SELECT * FROM leave_application WHERE leave_id = %s ORDER BY leave_id", (leave_id,))
        leave = cursor.fetchone()
        cursor.execute("SELECT department_id FROM employee WHERE employee_id = %s", (username,))
        department_id = cursor.fetchone()
        comment = form.comment.data
        comment_by = username
        now = datetime.datetime.now()
        curr_year = int(now.year)
        comment_time = str(datetime.datetime.now())
        cursor.execute("INSERT INTO comments(leave_id, comment, comment_time, comment_by, role, department_id) VALUES(%s, %s, %s, %s, %s, %s)", (leave_id, comment, comment_time, comment_by, get_role(), department_id))
        if form.action.data == "send_back" :
            status = "Sent Back"
        elif form.action.data == "reject" :
            status = "Rejected"
        else :
            cursor.execute("Select role FROM employee WHERE employee_id = %s", (leave[2],))
            role = cursor.fetchone()[0]
            start_route = get_role()
            cursor.execute("Select end_route FROM route WHERE role = %s AND start_route = %s", (role, start_route))
            end_route = cursor.fetchone()
            if end_route is None:
                status = "Granted"
                cursor.execute("Select total_leaves_left FROM leaves_left WHERE employee_id = %s AND year = %s", (leave[2], curr_year))
                leaves_left = cursor.fetchone()[0] - int((leave[5]-leave[4]).days) - 1
                if leaves_left < 0:
                    cursor.execute("Select total_leaves_left FROM leaves_left WHERE employee_id = %s AND year = %s", (leave[2], (curr_year+1)))
                    next_leaves_left = cursor.fetchone()[0] - abs(leaves_left)
                    cursor.execute("Update leaves_left SET total_leaves_left = %s WHERE employee_id = %s AND year = %s", (next_leaves_left, leave[2], (curr_year+1)))
                    leaves_left = 0
                cursor.execute("Update leaves_left SET total_leaves_left = %s WHERE employee_id = %s AND year = %s", (leaves_left, leave[2], curr_year))
            else :
                status = "Forwarded"
                cursor.execute("DELETE FROM leave_requests WHERE role = %s AND leave_id = %s", (get_role(), leave_id))
                cursor.execute("SELECT department_id FROM employee WHERE employee_id = %s", (username,))
                department_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO leave_requests(role, leave_id, department_id) VALUES(%s, %s, %s)", (end_route, leave_id, department_id))
        if status != "Forwarded":
            cursor.execute("DELETE FROM leave_requests WHERE role = %s AND leave_id = %s", (get_role(), leave_id))
        cursor.execute("UPDATE leave_Application SET status = %s WHERE leave_id = (%s)", (status, leave[0]))
        conn.commit()
        return redirect(url_for('user.leave_requests', username = username))
    return render_template('user/leaves/action.html', leave_id = leave_id, form = form, title="Action", username = username, isadmin = get_isadmin(), role = get_role())


@user.route('/leave-requests', methods=['GET', 'POST'])
def leave_requests():
    if (get_username() == ""):
        flash ("Please Login!")
        return redirect(url_for('auth.login'))
    username = get_username()
    cursor.execute("SELECT leave_application.leave_id, leave_type, leave_application.employee_id, applied_date, start_date, end_date, status, application, leave_application.department_id FROM leave_application, leave_requests WHERE leave_requests.role = %s and leave_application.leave_id = leave_requests.leave_id", (get_role(),))
    temp_requests = cursor.fetchall()
    requests = []
    if get_role() == 'HOD':
        cursor.execute("SELECT department_id FROM employee WHERE employee_id = %s", (username,))
        department_id = cursor.fetchone()[0]
        for request in temp_requests:
            if department_id == request[8]:
                requests.append(request)
    else :
        requests = temp_requests
    cursor.execute("SELECT * FROM comments ORDER BY leave_id DESC")
    comments = cursor.fetchall()
    return render_template('user/leaves/leave_requests.html', requests = requests, comments = comments, title="Leave Requests", username = username, isadmin = get_isadmin(), role = get_role())

@user.route('/comment', methods = ['GET', 'POST'])
def comment():
    if (get_username() == ""):
        flash ("Please Login!")
        return redirect(url_for('auth.login'))
    username = get_username()
    form = commentFormLower()
    cursor.execute("SELECT * FROM leave_application WHERE employee_id = %s ORDER BY leave_id DESC", (username,))
    leave = cursor.fetchone()
    cursor.execute("SELECT * FROM comments ORDER BY leave_id DESC")
    comments = cursor.fetchall()
    if leave:
        if leave[6] == "Sent Back":
            if form.validate_on_submit():
                comment = form.comment.data
                comment_by = username
                comment_time = str(datetime.datetime.now())
                cursor.execute("UPDATE leave_Application SET status = %s WHERE leave_id = (%s)", ("Waiting", leave[0]))
                cursor.execute("SELECT role FROM comments WHERE leave_id = %s ORDER BY comment_id DESC", (leave[0],))
                end_route = cursor.fetchone()[0]
                cursor.execute("SELECT department_id FROM employee WHERE employee_id = %s", (username,))
                department_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO leave_requests(role, leave_id, department_id) VALUES(%s, %s, %s)", (end_route, leave[0], department_id))
                cursor.execute("INSERT INTO comments(leave_id, comment, comment_time, comment_by, role, department_id) VALUES(%s, %s, %s, %s, %s, %s)", (leave[0], comment, comment_time, comment_by, get_role(), department_id))
                conn.commit()
                flash ('Application Re-sent!')
                return  redirect(url_for('user.dashboard', username = username))
            return render_template('user/leaves/comment.html', form = form, leave = leave, comments = comments, title = "Comment", username = username, isadmin = get_isadmin(), role = get_role())
        flash ('No action required!')
        return  redirect(url_for('user.dashboard', username = username))
    flash ('No action required!')
    return  redirect(url_for('user.dashboard', username = username))
    
@user.route('/profile', methods=['GET', 'POST'])
def profile():
    if (get_username() == ""):
        flash ("Please Login!")
        return redirect(url_for('auth.login'))
    username = get_username()
    emp = db.employee.find_one({"_id" : username})
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

    return render_template('user/profile/profile.html', first_name = first_name, last_name = last_name, email_id = email_id, department_id = department_id,
                        no_awards = no_awards, no_publications = no_publications, no_researchs = no_researchs, no_projects = no_projects,
                        biography = biography, education = education, experience = experience, research_interests = research_interests,
                        projects = projects, publications = publications, awards = awards, title='Dashboard', username = username, isadmin = get_isadmin(), role = get_role())

@user.route('/edit', methods=['GET', 'POST'])
def edit_details():
    if (get_username() == ""):
        flash ("Please Login!")
        return redirect(url_for('auth.login'))
    username = get_username()
    emp = db.employee.find_one({"_id" : username})
    first_name = emp['first_name']
    last_name = emp['last_name']
    email_id = emp['email_id']
    no_awards = emp['no_awards']
    no_publications = emp['no_publications']
    no_researchs = emp['no_researchs']
    no_projects = emp['no_projects']
    biography = emp['biography']

    form = EditDetailsForm(first_name = first_name, last_name = last_name, email_id = email_id, biography = biography,
                    no_awards = no_awards, no_publications = no_publications, no_researchs = no_researchs, no_projects = no_projects)
    if form.validate_on_submit():
        myquery = { "_id": username }
        newvalues = { "$set": { "first_name" : form.first_name.data, "last_name" : form.last_name.data, "email_id" : form.email_id.data,
                        "biography" : form.biography.data, "no_awards" : form.no_awards.data, "no_publications" : form.no_publications.data,
                        "no_researchs" : form.no_researchs.data, "no_projects" : form.no_projects.data} }
        db.employee.update_one(myquery, newvalues)
        cursor.execute("UPDATE employee SET first_name = %s, last_name = %s, email_id = %s WHERE employee_id = (%s)", (form.first_name.data, form.last_name.data, form.email_id.data, username))
        conn.commit()
        return redirect(url_for('user.profile'))
    return render_template('user/profile/edit_basic_details.html', form=form, title="Edit Details" , username = username, isadmin = get_isadmin(), role = get_role())

    
@user.route('/add/project', methods=['GET', 'POST'])
def add_project():
    if (get_username() == ""):
        flash ("Please Login!")
        return redirect(url_for('auth.login'))
    form = AddDetailsForm()
    username = get_username()
    if form.validate_on_submit():
        db.employee.update({"_id" : username},{"$push": {"projects" : form.add.data } })
        return redirect(url_for('user.profile'))
    return render_template('user/profile/add_details.html', form=form, title="Add" , username = username, isadmin = get_isadmin(), role = get_role())

@user.route('/add/research-interest', methods=['GET', 'POST'])
def add_research_interest():
    if (get_username() == ""):
        flash ("Please Login!")
        return redirect(url_for('auth.login'))
    form = AddDetailsForm()
    username = get_username()
    if form.validate_on_submit():
        db.employee.update({"_id" : username},{"$push": {"research_interests" : form.add.data } })
        return redirect(url_for('user.profile'))
    return render_template('user/profile/add_details.html', form=form, title="Add" , username = username, isadmin = get_isadmin(), role = get_role())

@user.route('/add/award', methods=['GET', 'POST'])
def add_award():
    if (get_username() == ""):
        flash ("Please Login!")
        return redirect(url_for('auth.login'))
    form = AddDetailsForm()
    username = get_username()
    if form.validate_on_submit():
        db.employee.update({"_id" : username},{"$push": {"awards" : form.add.data } })
        return redirect(url_for('user.profile'))
    return render_template('user/profile/add_details.html', form=form, title="Add" , username = username, isadmin = get_isadmin(), role = get_role())

@user.route('/add/publication', methods=['GET', 'POST'])
def add_publication():
    if (get_username() == ""):
        flash ("Please Login!")
        return redirect(url_for('auth.login'))
    form = AddDetailsForm()
    username = get_username()
    if form.validate_on_submit():
        db.employee.update({"_id" : username},{"$push": {"publications" : form.add.data } })
        return redirect(url_for('user.profile'))
    return render_template('user/profile/add_details.html', form=form, title="Add" , username = username, isadmin = get_isadmin(), role = get_role())

@user.route('/add/education', methods=['GET', 'POST'])
def add_education():
    if (get_username() == ""):
        flash ("Please Login!")
        return redirect(url_for('auth.login'))
    form = AddDetailsForm()
    username = get_username()
    if form.validate_on_submit():
        db.employee.update({"_id" : username},{"$push": {"education" : form.add.data } })
        return redirect(url_for('user.profile'))
    return render_template('user/profile/add_details.html', form=form, title="Add" , username = username, isadmin = get_isadmin(), role = get_role())

@user.route('/add/experience', methods=['GET', 'POST'])
def add_experience():
    if (get_username() == ""):
        flash ("Please Login!")
        return redirect(url_for('auth.login'))
    form = AddDetailsForm()
    username = get_username()
    if form.validate_on_submit():
        db.employee.update({"_id" : username},{"$push": {"experience" : form.add.data } })
        return redirect(url_for('user.profile'))
    return render_template('user/profile/add_details.html', form=form, title="Add" , username = username, isadmin = get_isadmin(), role = get_role())
    

@user.route('/delete/<id>/<data>', methods=['GET', 'POST'])
def delete(id, data):
    if (get_username() == ""):
        flash ("Please Login!")
        return redirect(url_for('auth.login'))
    username = get_username()
    db.employee.update({ "_id" : username,}, { "$pull" : { id : data} })
    return redirect(url_for('user.profile'))