import psycopg2
import datetime

conn = psycopg2.connect(host = "127.0.0.1", user = "admin", password= "password", port ="5432", database = "faculty_portal")
cursor = conn.cursor()

# Drop all tables
def delete_table():
    cursor.execute('''  DROP TABLE IF EXISTS department CASCADE;
                        DROP TABLE IF EXISTS employee CASCADE;
                        DROP TABLE IF EXISTS hod CASCADE;
                        DROP TABLE IF EXISTS pos CASCADE;
                        DROP TABLE IF EXISTS ccf CASCADE;
                        DROP TABLE IF EXISTS leaves_left CASCADE;
                        DROP TABLE IF EXISTS leave_application CASCADE;
                        DROP TABLE IF EXISTS leave_requests CASCADE;
                        DROP TABLE IF EXISTS comments CASCADE;
                        DROP TABLE IF EXISTS route CASCADE;
                        DROP TABLE IF EXISTS ccf_history CASCADE;
                        DROP TABLE IF EXISTS hod_history CASCADE;''')

    print('Deleted Table!')
    conn.commit()
    return


def initialize():
    cursor.execute('''CREATE TABLE IF NOT EXISTS department(
                    department_id VARCHAR(50) NOT NULL PRIMARY KEY,
                    department_name VARCHAR(255) NOT NULL
                );''')
    print('Department Table Created!')

    cursor.execute('''CREATE TABLE IF NOT EXISTS employee(
                    employee_id VARCHAR(255) NOT NULL PRIMARY KEY,
                    password VARCHAR(255) NOT NULL,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    email_id VARCHAR(50) NOT NULL,
                    department_id VARCHAR(50) NOT NULL,
                    date_of_joining DATE NOT NULL,
                    role VARCHAR(255) NOT NULL,
                    isAdmin BOOLEAN NOT NULL,
                    FOREIGN KEY(department_id) REFERENCES department(department_id)        
                );''')
    cursor.execute('''ALTER TABLE employee ALTER COLUMN password SET DEFAULT 'iitropar' ''');
    cursor.execute('''ALTER TABLE employee ALTER COLUMN isAdmin SET DEFAULT false''');
    cursor.execute('''ALTER TABLE employee ALTER COLUMN role SET DEFAULT 'FACULTY' ''');

    cursor.execute('''CREATE TABLE IF NOT EXISTS hod(
                    hod_id VARCHAR(255) NOT NULL,
                    department_id VARCHAR(255) NOT NULL,
                    appointed_date DATE NOT NULL,
                    PRIMARY KEY(hod_id, department_id),
                    FOREIGN KEY(department_id) REFERENCES department(department_id), 
                    FOREIGN KEY(hod_id) REFERENCES employee(employee_id)
                );''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS pos(
                        position VARCHAR(50) NOT NULL PRIMARY KEY,
                        position_name VARCHAR(255) NOT NULL
                    );''')

    # position : Dean Faculty Affairs, Dean Associative Faculty Affairs, Director
    cursor.execute('''CREATE TABLE IF NOT EXISTS ccf(
                    employee_id VARCHAR(255) NOT NULL,
                    position VARCHAR(50) NOT NULL,
                    appointed_date DATE NOT NULL,
                    PRIMARY KEY(employee_id, position),
                    FOREIGN KEY(employee_id) REFERENCES employee(employee_id),
                    FOREIGN KEY(position) REFERENCES pos(position)
                );''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS leaves_left(
                    employee_id VARCHAR(255) NOT NULL,
                    total_leaves_left INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    PRIMARY KEY(employee_id, year),
                    FOREIGN KEY(employee_id) REFERENCES employee(employee_id)
                );''')

    # Comment stores every comment along with commit time and commit by
    cursor.execute('''CREATE TABLE IF NOT EXISTS leave_application(
                    leave_id SERIAL NOT NULL PRIMARY KEY,
                    leave_type VARCHAR(50) NOT NULL,
                    employee_id VARCHAR(255) NOT NULL,
                    applied_date DATE NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    status VARCHAR(255) NOT NULL,
                    application TEXT NOT NULL,
                    department_id VARCHAR(255) NOT NULL
                );''')

    # HOD-dashboard : Shortcut to display all leave requests
    cursor.execute('''CREATE TABLE IF NOT EXISTS leave_requests(
                    leave_id SERIAL NOT NULL,
                    role VARCHAR(255) NOT NULL,  
                    department_id VARCHAR(255) NOT NULL,              
                    PRIMARY KEY(leave_id),
                    FOREIGN KEY(leave_id) REFERENCES leave_application(leave_id)
                );''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS comments(
                    comment_id SERIAL NOT NULL,
                    leave_id SERIAL NOT NULL,
                    comment TEXT,
                    comment_by VARCHAR(255) NOT NULL,
                    comment_time VARCHAR(255) NOT NULL,
                    role VARCHAR(255) NOT NULL,
                    department_id VARCHAR(255) NOT NULL,
                    PRIMARY KEY(comment_id)
                );''')

    # Stores history of previous HODs
    cursor.execute('''CREATE TABLE IF NOT EXISTS hod_history(
                    hod_id VARCHAR(255) NOT NULL,
                    department_id VARCHAR(50) NOT NULL,
                    time VARCHAR(20) NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE,                
                    PRIMARY KEY(hod_id, department_id, start_date, time)
                );''')

    # Stores history of previous cross-cutting-faculties
    cursor.execute('''CREATE TABLE IF NOT EXISTS ccf_history(
                    employee_id VARCHAR(255) NOT NULL,
                    position VARCHAR(50) NOT NULL,
                    time VARCHAR(20) NOT NULL, 
                    start_date DATE NOT NULL,
                    end_date DATE,                
                    PRIMARY KEY(employee_id, position, time, start_date)
                );''')

    # Route
    cursor.execute(''' CREATE TABLE IF NOT EXISTS route(
                    role VARCHAR(255) NOT NULL,
                    start_route VARCHAR(255) NOT NULL,
                    end_route VARCHAR(255) NOT NULL,
                    PRIMARY KEY(role, start_route)
                );''')
    print('All tables created')
    conn.commit()
    return