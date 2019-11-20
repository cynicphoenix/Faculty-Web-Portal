from flask import abort, flash, redirect, render_template, url_for
from datetime import date, datetime
from time import gmtime, strftime
from . import admin
from auth.views import get_username, get_isadmin
from admin.forms import AddDepartmentForm, AddPositionForm, AddCCFForm, AddHODForm, AddRouteForm, EditCCFForm, EditHODForm
from database_postgres.database import cursor, conn
from database_mongo.database import db

@admin.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    return render_template('/admin/dashboard.html', title = "Dashboard", username = get_username(), isadmin = get_isadmin())


@admin.route('/departments', methods=['GET', 'POST'])
def list_departments():
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    cursor.execute("SELECT * FROM department WHERE department_id != 'NONE' ORDER BY department_id ASC;")
    departments = cursor.fetchall()
    return render_template('admin/departments/departments.html', departments=departments, title="Departments", username = get_username(), isadmin = get_isadmin())

@admin.route('/departments/add', methods=['GET', 'POST'])
def add_department():
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    form = AddDepartmentForm()
    if form.validate_on_submit():
        cursor.execute("INSERT INTO department(department_id, department_name) VALUES(%s, %s)", (form.department_id.data, form.department_name.data))
        conn.commit()
        flash('You have successfully added a new department!')
        return redirect(url_for('admin.list_departments'))
    return render_template('admin/departments/department.html', action="Add", form=form, title="Add Department", username = get_username(), isadmin = get_isadmin())

@admin.route('/departments/delete/<department_id>', methods=['GET', 'POST'])
def delete_department(department_id):
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    cursor.execute("SELECT * from employee WHERE department_id = %s", (department_id,))
    employees = cursor.fetchone()
    if employees:
        flash("To remove the department, first remove all faculties enrolled in that department.")
        return redirect(url_for('home.error'))
    cursor.execute("DELETE FROM department WHERE department_id = %s", (department_id,))
    conn.commit()
    flash('You have successfully deleted the department!')
    return redirect(url_for('admin.list_departments'))
    return render_template(title="Delete Department")



@admin.route('/positions', methods=['GET', 'POST'])
def list_positions():
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    cursor.execute("SELECT * FROM pos ORDER BY position ASC;")
    positions = cursor.fetchall()
    return render_template('admin/positions/positions.html', positions=positions, title="Positions", username = get_username(), isadmin = get_isadmin())


@admin.route('/positions/add', methods=['GET', 'POST'])
def add_position():
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    form = AddPositionForm()
    if form.validate_on_submit():
        cursor.execute("INSERT INTO pos(position, position_name) VALUES(%s, %s)", (form.position_id.data, form.position_name.data))
        conn.commit()
        flash('You have successfully added a new psoition!')
        return redirect(url_for('admin.list_positions'))
    return render_template('admin/positions/position.html', form = form, action="Add", title="Add Position", username = get_username(), isadmin = get_isadmin())

@admin.route('/positions/delete/<position_id>', methods=['GET', 'POST'])
def delete_position(position_id):
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    conn.commit()
    cursor.execute("UPDATE employee SET role = 'FACULTY' WHERE role = %s", (position_id,))
    cursor.execute("DELETE FROM ccf WHERE position = %s", (position_id,))
    cursor.execute("DELETE FROM pos WHERE position = %s", (position_id,))
    flash('You have successfully deleted the position!')
    return redirect(url_for('admin.list_positions'))
    return render_template(title="Delete Position")



@admin.route('/routes', methods=['GET', 'POST'])
def list_routes():
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    cursor.execute("SELECT * FROM route ORDER BY role")
    routes = cursor.fetchall()
    return render_template('admin/route/route.html', routes = routes, title = "Routes", username = get_username(), isadmin = get_isadmin())

@admin.route('/routes/add', methods=['GET', 'POST'])
def add_route():
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    form = AddRouteForm()
    if form.validate_on_submit():
        cursor.execute("INSERT INTO route(role, start_route, end_route) VALUES(%s, %s, %s)", (form.role.data, form.start_route.data, form.end_route.data))
        conn.commit()
        flash("Route Added Successfully")
        return redirect(url_for('admin.list_routes'))
    return render_template('admin/route/routes.html', title = "Add Route", form = form, username = get_username(), isadmin = get_isadmin())

@admin.route('/routes/delete/<role>/<start_route>', methods=['GET', 'POST'])
def delete_route(role, start_route):
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    cursor.execute("DELETE FROM route WHERE role = %s AND start_route  = %s", (role, start_route))
    conn.commit()
    flash('You have successfully deleted the route!')
    return redirect(url_for('admin.list_routes'))
    return render_template(title="Delete Position")



@admin.route('/ccf', methods=['GET', 'POST'])
def list_ccf():
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    cursor.execute("SELECT * FROM ccf ORDER BY position ASC")
    poss = cursor.fetchall()
    return render_template('admin/roles/ccf.html', poss=poss, title='CCF', username = get_username(), isadmin = get_isadmin())

@admin.route('/ccf/add', methods=['GET', 'POST'])
def add_ccf():
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    add_ccf = True
    form = AddCCFForm()
    if form.validate_on_submit():
        cursor.execute("INSERT INTO ccf(position, employee_id, appointed_date) VALUES(%s, %s, %s)", (form.position.data, form.employee_id.data, date.today()))
        cursor.execute("UPDATE employee SET role = %s WHERE employee_id = %s", (form.position.data, form.employee_id.data))
        conn.commit()
        flash('You have successfully added a new position!')
        return redirect(url_for('admin.list_ccf'))
    return render_template('admin/roles/ccfs.html', action="Add", add_ccf = add_ccf, form=form, title="Add CCF", username = get_username(), isadmin = get_isadmin())

@admin.route('/ccf/delete/<position>', methods=['GET', 'POST'])
def delete_ccf(position):
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    cursor.execute("SELECT * FROM ccf WHERE position = %s", (position,))
    data = cursor.fetchone()
    cursor.execute("INSERT INTO ccf_history(employee_id, position, time, start_date, end_date) VALUES(%s, %s, %s, %s, %s)", (data[0], data[1], (datetime.now()).strftime("%H:%M:%S"), data[2], date.today()))
    cursor.execute("DELETE FROM ccf WHERE position = %s", (position,))
    cursor.execute("UPDATE employee SET role = 'FACULTY' WHERE employee_id = %s", (data[0],))
    conn.commit()
    flash('You have successfully deleted the ccf!')
    return redirect(url_for('admin.list_ccf'))
    return render_template(title="Delete CCF")

@admin.route('/ccf/edit/<position>', methods=['GET', 'POST'])
def edit_ccf(position):
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    add_ccf = False
    form = EditCCFForm()
    cursor.execute("SELECT * FROM ccf WHERE position = %s", (position,))
    data = cursor.fetchone()
    if form.validate_on_submit():
        cursor.execute("INSERT INTO ccf_history(employee_id, position, time, start_date, end_date) VALUES(%s, %s, %s, %s, %s)", (data[0], data[1], (datetime.now()).strftime("%H:%M:%S"), data[2], date.today()))
        cursor.execute("UPDATE employee SET role = %s WHERE employee_id = %s", ('FACULTY', data[0]))
        cursor.execute("UPDATE employee SET role = %s WHERE employee_id = %s", (position, form.employee_id.data))
        cursor.execute("UPDATE ccf SET employee_id = %s, appointed_date = %s WHERE position = %s", (form.employee_id.data, date.today(), position))
        conn.commit()
        flash('You have successfully updated the position!')
        return redirect(url_for('admin.list_ccf'))
    return render_template('admin/roles/ccfs.html', action="Edit", add_ccf = add_ccf, form=form, title="Edit CCF", username = get_username(), isadmin = get_isadmin())



@admin.route('/hod', methods=['GET', 'POST'])
def list_hod():
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    cursor.execute("SELECT * FROM hod ORDER BY department_id ASC")
    hods = cursor.fetchall()
    return render_template('admin/roles/hod.html', hods=hods, title='HOD', username = get_username(), isadmin = get_isadmin())

@admin.route('/hod/add', methods=['GET', 'POST'])
def add_hod():
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    add_hod = True
    form = AddHODForm()
    if form.validate_on_submit():
        cursor.execute("SELECT department_id FROM employee WHERE employee_id = %s", (form.hod_id.data,))
        if cursor.fetchone()[0] == form.department_id.data :
            cursor.execute("INSERT INTO hod(department_id, hod_id, appointed_date) VALUES(%s, %s, %s)", (form.department_id.data, form.hod_id.data, date.today()))
            cursor.execute("UPDATE employee SET role = %s WHERE employee_id = %s", ('HOD', form.hod_id.data,))
            conn.commit()
            flash('You have successfully added a new HOD!')
        else :
            flash('Invalid Entry!')
        return redirect(url_for('admin.list_hod'))
    return render_template('admin/roles/hods.html', action="Add", add_hod = add_hod, form=form, title="Add HOD", username = get_username(), isadmin = get_isadmin())

@admin.route('/hod/delete/<department_id>', methods=['GET', 'POST'])
def delete_hod(department_id):
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    cursor.execute("SELECT * FROM hod WHERE department_id = %s", (department_id,))
    data = cursor.fetchone()
    cursor.execute("INSERT INTO hod_history(hod_id, department_id, time, start_date, end_date) VALUES(%s, %s, %s, %s, %s)", (data[0], data[1], (datetime.now()).strftime("%H:%M:%S"), data[2], date.today()))
    cursor.execute("DELETE FROM hod WHERE department_id = %s", (department_id,))
    cursor.execute("UPDATE employee SET role = 'FACULTY' WHERE employee_id = %s", (data[0],))
    conn.commit()
    flash('You have successfully deleted the HOD!')
    return redirect(url_for('admin.list_hod'))
    return render_template(title="Delete HOD")

@admin.route('/hod/edit/<department_id>', methods=['GET', 'POST'])
def edit_hod(department_id):
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    add_hod = False
    form = EditHODForm()
    cursor.execute("SELECT * FROM hod WHERE department_id = %s", (department_id,))
    data = cursor.fetchone()
    if form.validate_on_submit():
        cursor.execute("SELECT department_id FROM employee WHERE employee_id = %s", (form.hod_id.data,))
        if cursor.fetchone()[0] == department_id :
            cursor.execute("INSERT INTO hod_history(hod_id, department_id, time, start_date, end_date) VALUES(%s, %s, %s, %s, %s)", (data[0], data[1], (datetime.now()).strftime("%H:%M:%S"), data[2], date.today()))
            cursor.execute("UPDATE employee SET role = %s WHERE employee_id = %s", ('FACULTY', data[0]))
            cursor.execute("UPDATE employee SET role = %s WHERE employee_id = %s", ('HOD', form.hod_id.data))
            cursor.execute("UPDATE hod SET hod_id = %s, appointed_date = %s WHERE department_id = %s", (form.hod_id.data, date.today(), department_id))
            conn.commit()
            flash('You have successfully changed the HOD!')
        else :
            flash('Invalid Entry!')
        return redirect(url_for('admin.list_hod'))
    return render_template('admin/roles/ccfs.html', action="Edit", add_hod = add_hod, form=form, title="Edit HOD", username = get_username(), isadmin = get_isadmin())


@admin.route('/hod/history', methods=['GET', 'POST'])
def history_hod():
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    hod = True
    cursor.execute("SELECT * FROM hod_history ORDER BY department_id ASC, start_date ASC, time ASC")
    history = cursor.fetchall()
    return render_template('admin/history/history.html', hod = hod, history = history, title = "HOD History", username = get_username(), isadmin = get_isadmin())

@admin.route('/ccf/history', methods=['GET', 'POST'])
def history_ccf():
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    hod = False
    cursor.execute("SELECT * FROM ccf_history ORDER BY position ASC, start_date DESC, time ASC")
    history = cursor.fetchall()
    return render_template('admin/history/history.html', hod = hod, history = history, title = "CCF History", username = get_username(), isadmin = get_isadmin())


@admin.route('/employees', methods=['GET', 'POST'])
def employees():
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    cursor.execute("SELECT * FROM employee ORDER BY employee_id ASC ")
    employees = cursor.fetchall()
    cursor.execute("SELECT * FROM department WHERE department_id != 'NONE' ORDER BY department_id ASC")
    departments = cursor.fetchall()
    return render_template('admin/employees.html', employees= employees, departments = departments, title = "Employees", username = get_username(), isadmin = get_isadmin())

@admin.route('/employees/delete/<employee_id>', methods=['GET', 'POST'])
def delete_employee(employee_id):
    if get_isadmin() == False:
        return redirect(url_for('home.error403'))
    cursor.execute("DELETE FROM hod WHERE hod_id = %s", (employee_id,))
    cursor.execute("DELETE FROM ccf WHERE employee_id = %s", (employee_id,))
    cursor.execute("DELETE FROM leaves_left WHERE employee_id = %s", (employee_id,))
    cursor.execute("DELETE FROM employee WHERE employee_id = %s", (employee_id,))
    db.employee.remove( {'_id' : employee_id} )
    conn.commit()
    flash('You have successfully deleted the employee!')
    return redirect(url_for('admin.employees'))
    return render_template(title="Delete Department")