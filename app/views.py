import random
import string

from app            import app
from app.database   import db, User, Employee, Manager, Promotion, Training, Training_Emp, Travel, Travel_Emp, Working, Project, Project_Rating
from datetime       import datetime, date
from dateutil       import relativedelta
from config         import *
from werkzeug.urls  import url_parse

from flask          import Flask, render_template, request, redirect, session, flash, url_for, current_app
from flask_bcrypt   import Bcrypt
from flask_mail     import Mail, Message
from flask_login    import LoginManager, current_user, login_user, logout_user, login_required


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

@login.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/', methods = ['POST', 'GET'])
@app.route('/index', methods = ['POST', 'GET'])
@login_required
def index_post():
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':
        if request.form.get('check') != None:
            if session.get('chechin') == None:
                checkin_date = datetime.today()
                employee_id = current_user.id
                
                checkin = Working(
                   checkin_date, checkin_date, employee_id
                )
                db.session.add(checkin)
                db.session.commit()
                
                flash('you had checked in')
                session['chechin'] = current_user.id

                return render_template('index.html')
            else:
                checkout_date = datetime.today()
                checking = Working.query.filter_by(id=session.get('chechin')).first()
                checking.checkout_date = checkout_date
                db.session.commit()

                flash('you had checked out')
                session.pop('chechin', None)

                return render_template('index.html')

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

        all_employee = Employee.query.all()
        this_employee_id = all_employee[-1].id

        user = User(
            email, pw_hash, this_employee_id
        )
        db.session.add(user)
        db.session.commit()

        flash("New employee has been added")

        return redirect(url_for('hr'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login_post():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by( email = request.form.get('email') ).first()
        if user is None :
            flash('Email doesn\'t exist')
            return redirect(url_for('login'))
        elif not bcrypt.check_password_hash(user.password, request.form.get('password')):
            flash('Invalid password')
            return redirect(url_for('login'))
        login_user(user, remember=request.form.get('remember'))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')

    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email address already exists.')
        return redirect(url_for('auth.signup'))
    
    id_emp = 100

    new_user = User(
        email = email, 
        password = bcrypt.generate_password_hash(password, 5), 
        employee_id = id_emp
    )
    
    new_user.role = role

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/manage_users')
@login_required
def manageUsers():
    return render_template('users.html')

'''
*manage_users
*hr
newManager : teams, change manager
newOperation : travel
newOperation : training
projects 
profile : work/life balence, password, RelationshipSatisfaction
'''
def load_travels():
    travels = Travel.query.all()
    dict_travels = []
    for travel in travels:
        travel_employees = Travel_Emp.query.filter_by(travel_id = travel.id).count()
        dict_travels.append(
            {
                'travels': travel,
                'employees_number': travel_employees
            }
        )
    return dict_travels

@app.route('/travels', methods = ['GET', 'POST'])
@login_required
def travels():
    if request.method == 'GET' and request.args.get('delete'):
        travel = Travel.query.filter_by(id = int(request.args.get('delete'))).first()
        db.session.delete(travel)
        db.session.commit()
        flash("The travel has been deleted")
    if request.method == 'POST' and request.form.get('submit'):
        travel = Travel(
            todate(request.form.get('date')),
            int(request.form.get('duration')),
            request.form.get('destination')
        )
        db.session.add(travel)
        db.session.commit()
        flash("New travel has been added")
    return render_template('travels.html', travels = load_travels())

@app.route('/travels/<travel>', methods = ['GET', 'POST'])
@login_required
def travel_employees(travel):
    '''travel_employee = Travel_Emp.query.filter_by(travel_id = )'''

    
    if request.method == 'POST' and request.form.get('employee_id'):
        travelEmp = Travel_Emp(
            int(travel),
            int(request.form.get('employee_id').split(' ')[0])
        )
        db.session.add(travelEmp)
        db.session.commit()
        flash("Employee has been added")
    
    if request.method == 'GET' and request.args.get('delete'):
        travel_emp = Travel_Emp.query.filter_by(id = int(request.args.get('delete'))).first()
        db.session.delete(travel_emp)
        db.session.commit()
        flash("Employee has been deleted")
    
    Travel_details  = db.session.query(Travel_Emp).filter_by(travel_id = travel).all()
    a = []
    for travel in Travel_details:
        a.append(
            {
                'travel': travel,
                'employee': Employee.query.filter_by(id = travel.employee_id).first()
            }
        )
    id_travelers    = [traveler.employee_id for traveler in Travel_details]
    all_emp         = db.session.query(Employee).filter(Employee.id.notin_(id_travelers)).all()

    return render_template('travel_employees.html', travels = a, all = all_emp)

@app.route('/newPromotion', methods = ['POST', 'GET'])
@login_required
def HRnewPromotion():
    if request.method == "POST" and request.form.get("employee_id") :
        return redirect(url_for("newPromotion", to_promote = str(request.form.get("employee_id").split(' ')[0])))
    all_emp = Employee.query.all()
    return render_template("to_promote.html", all = all_emp)

@app.route('/newPromotion/<to_promote>', methods = ['POST', 'GET'])
@login_required
def newPromotion(to_promote):
    if request.method == 'POST':
        promotion = Promotion(
            int(request.form.get("role")),      request.form.get("departement"),    todate(request.form.get("date")), 
            int(request.form.get("salary")),    int(request.form.get("level")),     int(request.form.get("standard_hours")), 
            int(to_promote)
        )
        user = User.query.filter_by(employee_id = to_promote).first()
        user.role = int(request.form.get("privilege"))
        db.session.add(promotion)
        db.session.commit()
        flash("Employee has been promoted")
        
        return redirect(url_for("HRnewPromotion"))
    
    promote = Promotion.query.filter_by(employee_id = int(to_promote)).first()
    Roles = {0: "User", 1: "Manager", 2: "HR", 3: "HR Manager", 4: "Admin"}
    return render_template("promote.html", employee = promote, Roles = Roles)

@app.route('/ML', methods = ['POST', 'GET'])
@login_required
def ml():
    if request.method == 'POST' and request.form.get('employee'):
        return redirect(url_for('ml', to_predict = request.form.get('employee').split(' ')[0]))
    all_emp = Employee.query.all()
    return render_template("ml.html", all = all_emp)

@app.route('/ML/<to_predict>')
@login_required
def predcition(to_predict):
    L = []
    employee = Employee.query.filter_by(id = int(to_predict)).first()
    manager = Manager.query.filter_by(id = int(to_predict)).first()
    promotion = Promotion.query.filter_by(id = int(to_predict)).first()
    promotions = Promotion.query.filter_by(id = int(to_predict)).all()

    employee.gender
    employee.marital_status
    employee.companies_number
    catage = relativedelta.relativedelta(date.today(), employee.birthday).years
    if catage < 35:
        'jeune'
    elif 35 < catege < 45:
        'exp'
    else:
        'Age'
    employee.education
    employee.education_field
    relativedelta.relativedelta(date.today(), employee.first_employement).years
    relativedelta.relativedelta(date.today(), employee.first_employement_date).years
    relativedelta.relativedelta(date.today(), manager.date).years
    promotion.role
    promotion.salary
    promotion.departement
    promotion.level
    promotion.standard_hours
    (promtions[0]/promotions[-1]) - 1
    
    return render_template('prediction.html', result = predict(L))

"""
[
'Age', 'BusinessTravel', *'DailyRate', 'Department',
'DistanceFromHome', 'Education', 'EducationField', 
'EnvironmentSatisfaction', 'Gender', *'HourlyRate',
'JobInvolvement', 'JobLevel', 'JobRole', 'JobSatisfaction',
'MaritalStatus', 'MonthlyIncome', 'MonthlyRate', 'NumCompaniesWorked',
'Over18', 'OverTime', 'PercentSalaryHike', 'PerformanceRating',
'RelationshipSatisfaction', 'StandardHours', 'StockOptionLevel',
'TotalWorkingYears', 'TrainingTimesLastYear', 'WorkLifeBalance',
'YearsAtCompany', 'YearsInCurrentRole', 'YearsSinceLastPromotion',
'YearsWithCurrManager', 'Unnamed: 35', 'Atrrival', 'Cateage'
]
"""
