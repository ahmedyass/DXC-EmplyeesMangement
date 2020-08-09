import random
import string

from app            import app
from app.database   import db, Employee, User, Manager, Promotion, Training, Travel, Working
from datetime       import datetime
from config         import *

from flask          import Flask, render_template, request, session, flask
from flask_bcrypt   import Bcrypt
from flask_mail     import Mail, Message
from flask_login    import LoginManager, current_user, login_user, logout_user, login_required, current_app


"""
Message lia hada , don't forget to remove your password from config before uploading the app 

"""

bcrypt      = Bcrypt(app)
mail        = Mail(app)
login       = LoginManager(app)

def todate(d):
    """
    This function is in order to change imported date from HTML to python date object
    """
    dateIwant = d.split('-')
    return datetime(int(dateIwant[0]), int(dateIwant[1]), int(dateIwant[2]))

def get_random_password_string(length):
    """
    this function is in order to create a random password that contains a specific number (length) of caracters 
    """
    password_characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(password_characters) for i in range(length))
    return password

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/index', methods = ['POST', 'GET'])
@login_required
def checking():
    if request.method == 'POST':
        if request.form.get('check') != None:
            if session.get('chechin') == None:
                checkin_date = datetime.today()
                employee_id = current_app.login_manager.id_attribute
                
                checkin = Working(
                    checkin_date, employee_id
                )
                db.session.add(checkin)
                db.session.commit()
                
                flash('you had checked in')

                all_employee_checkings = Working.query.filter_by(employee_id=employee_id)
                this_employee_checking_id = all_employee_checkings[-1].id
                session['chechin'] = this_employee_checking_id

                return render_template('index.html', role=current_user.get_role())
            else:
                checkout_date = datetime.today()
                checking = Working.query.filter_by(id=session.get('chechin'))
                checking.checkout_date = checkout_date
                db.session.commit()

                flash('you had checked out')
                session.pop('chechin', None)

                return render_template('index.html', role=current_user.get_role())

@app.route('/hr')
@login_required
def hr():
    education = ['Life Sciences', 'Other', 'Medical', 'Marketing', 'Technical Degree', 'Human Resources']
    return render_template('index-hr.html', educfields = education)


@app.route('/newEmployee', methods = ['POST', 'GET'])
@login_required
def HRnewEmployee():
    if request.method == 'POST':    
        
        employee = Employee(
            request.form.get('first_name'),                 request.form.get('second_name'),                todate(request.form.get('birthday')), 
            request.form.get('gender'),                     int(request.form.get('education')),             request.form.get('education_field'), 
            request.form.get('marital_status'),             int(request.form.get('companies_number')), 
            todate(request.form.get('employement_date')),   todate(request.form.get('first_employement_date'))
        )
        db.session.add(employee)
        db.session.commit()

        email = request.form.get('email')
        password = get_random_password_string(10)
        pw_hash = bcrypt.generate_password_hash(password, 5)
        
        with mail.connect() as conn:
            msg = Message(
                sender = "monhamada@gmail.com",
                recipients = [email],
                subject = "Your Password"
            )
            msg.html = "<h3>Password</h3><br> <p> hey "+request.form.get('first_name')+"<br> this is your password: "+password+"</p>"

            conn.send(msg)

        """bcrypt.check_password_hash(pw_hash, pw_hash)"""

        all_employee = Employee.query.all()
        this_employee_id = all_employee[-1].id

        user = User(
            email, pw_hash, this_employee_id
        )
        db.session.add(user)
        db.session.commit()

        return "done"

@app.route('/newOperation', methods = ['POST', 'GET'])
def HRnewOperation():
    if request.method == 'GET':
        return render_template("operation.html")
    if request.method == 'POST':
        if request.form.get('id') != None and request.form.get('operation') != None:
            if request.form.get('operation') == 'travel' :
                travel = Travel(
                    todate(request.form.get('date')), 
                    request.form.get('id')
                )
                db.session.add(travel)
                db.session.commit()

                return "Travel done"
            if request.form.get('operation') == 'training' :
                training = Training(
                    todate(request.form.get('date')), 
                    request.form.get('id')
                )
                db.session.add(training)
                db.session.commit()

                return "Training done"

@app.route('/newManager', methods = ['POST', 'GET'])
def HRnewManager():
    if request.method == 'GET':
        return render_template("change_manager.html")
    if request.method == 'POST':
        manager = Manager(
            todate(request.form.get('date')), 
            request.form.get('emp_id'), 
            request.form.get('man_id')
        )
        db.session.add(manager)
        db.session.commit()

        return "Manger done"

@app.route('/newPromotion', methods = ['POST', 'GET'])
def HRnewPromotion():
    if request.method == 'GET':
        return render_template("promote.html")
    if request.method == 'POST':
        promotion = Promotion(
            request.form.get("role"),       request.form.get("departement"),    todate(request.form.get("date")), 
            request.form.get("salary"),     request.form.get("level"),          request.form.get("standard_hours"), 
            request.form.get("employee_id")
        )
        db.session.add(promotion)
        db.session.commit()
        
        return "Manger done"

@app.route('/newProject', methods = ['POST', 'GET'])
def MnewProject():
    if request.method == 'GET':
        return render_template('project.html')
    if request.method == 'POST':
        
        manager_id = 0 #current user if he's a manager
        description = ''
        periode = 0
        starting_date = datetime.today()
        
        project = Project(
            manager_id,
            description,
            periode,
            starting_date
        )
        db.session.add(project)
        db.session.commit()
        
        return "rating done"

@app.route('/newProjectRating', methods = ['POST', 'GET'])
def MnewProjectRating():
    if request.method == 'GET':
        return render_template('rate_project.html')
    if request.method == 'POST':
        
        manager_id = 0 #current user if he's a manager
        employee_id = 0 #selected employee
        project_id = 0 #selected projects created by the manager
        performance_rating = 5
        
        rate = Project_Rating(
            manager_id,
            employee_id,
            project_id,
            performance_rating
        )
        db.session.add(rate)
        db.session.commit()
        
        return "rating done"