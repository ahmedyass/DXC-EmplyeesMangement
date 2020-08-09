from app                import app
from config             import *
from flask_sqlalchemy   import SQLAlchemy
from flask_login        import UserMixin
from datetime           import date

[
    'Age', 'Attrition', 'BusinessTravel', 'DailyRate', 'Department',
    'DistanceFromHome', 'Education', 'EducationField', 'EmployeeCount',
    'EmployeeNumber', 'EnvironmentSatisfaction', 'Gender', 'HourlyRate',
    'JobInvolvement', 'JobLevel', 'JobRole', 'JobSatisfaction',
    'MaritalStatus', 'MonthlyIncome', 'MonthlyRate', 'NumCompaniesWorked',
    'Over18', 'OverTime', 'PercentSalaryHike', 'PerformanceRating',
    'RelationshipSatisfaction', 'StandardHours', 'StockOptionLevel',
    'TotalWorkingYears', 'TrainingTimesLastYear', 'WorkLifeBalance',
    'YearsAtCompany', 'YearsInCurrentRole', 'YearsSinceLastPromotion',
    'YearsWithCurrManager', 'Unnamed: 35', 'Atrrival', 'Cateage'
]

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id                      = db.Column(db.Integer,     primary_key = True)
    email                   = db.Column(db.String(100), nullable = False, unique = True)
    password                = db.Column(db.String(255))
    role                    = db.Column(db.Integer,     nullable = False, default = 0)
    '''
    0: for user
    1: for manager
    2: for hr
    3: for hr manager 
    4: for admin
    '''

    employee_id     = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable = False, unique = True)
    employee        = db.relationship("Employee", back_populates = "user", uselist = False)
    
    def __init__(self, email, password, employee_id):
        self.email          = email
        self.password       = password
        self.employee_id    = employee_id

    def get_id(self):
        return self.id

    def get_role(self):
        return self.role

class Employee(db.Model):
    __tablename__ = 'employee'

    id                      = db.Column(db.Integer,     primary_key = True)
    first_name              = db.Column(db.String(100), nullable = False)
    second_name             = db.Column(db.String(100), nullable = False)
    birthday                = db.Column(db.DateTime)
    gender                  = db.Column(db.String(10),  nullable = False)
    education               = db.Column(db.Integer,     nullable = False)
    education_field         = db.Column(db.String(20),  nullable = False)
    marital_status          = db.Column(db.String(10),  nullable = False)
    companies_number        = db.Column(db.Integer,     nullable = False)
    employement_date        = db.Column(db.DateTime)
    first_employement_date  = db.Column(db.DateTime)
    attrition               = db.Column(db.Integer,     nullable = False, default = 0)

    user            = db.relationship("User",           back_populates = "employee")
    promotion       = db.relationship("Promotion",      back_populates = "employee")
    training_emp    = db.relationship("Training_Emp",   back_populates = "employee")
    travel_emp      = db.relationship("Travel_Emp",     back_populates = "employee")
    manager         = db.relationship("Manager",        back_populates = "employee",    foreign_keys = 'Manager.manager_id')
    employee_man    = db.relationship("Manager",        back_populates = "employee",    foreign_keys = 'Manager.employee_id')
    working         = db.relationship("Working",        back_populates = "employee")
    project         = db.relationship("Project",        back_populates = "manager")
    project_rating  = db.relationship("Project_Rating", back_populates = "employee")
    
    def __init__(self, first_name, second_name, birthday, gender, education, education_field, marital_status, companies_number, employement_date, first_employement_date):
        self.first_name             = first_name
        self.second_name            = second_name
        self.birthday               = birthday
        self.gender                 = gender
        self.education              = education
        self.education_field        = education_field
        self.marital_status         = marital_status
        self.companies_number       = companies_number
        self.employement_date       = employement_date
        self.first_employement_date = first_employement_date
        
class Manager(db.Model):
    __tablename__ = 'manager'

    id                      = db.Column(db.Integer,     primary_key = True)
    date                    = db.Column(db.DateTime,    default= date.today())

    employee_id     = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable = False)
    manager_id      = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable = False)
    employee        = db.relationship("Employee", foreign_keys=[employee_id], back_populates = "manager")
    manager         = db.relationship("Employee", foreign_keys=[employee_id], back_populates = "manager")

    def __init__(self, date, employee_id, manager_id):
        self.date           = date
        self.employee_id    = employee_id
        self.manager_id     = manager_id

class Promotion(db.Model):
    __tablename__ = 'promotion'

    id                  = db.Column(db.Integer,     primary_key = True)
    role                = db.Column(db.String(100), nullable = False)
    departement         = db.Column(db.String(100), nullable = False)
    date                = db.Column(db.DateTime,    default= date.today())
    salary              = db.Column(db.Integer,     nullable = False)
    level               = db.Column(db.Integer,     nullable = False)
    standard_hours      = db.Column(db.Integer,     nullable = False)

    employee_id     = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable = False)
    employee        = db.relationship("Employee", back_populates = "promotion")
    
    def __init__(self, role, departement, date, salary, level, standard_hours, employee_id):
        self.role           = role
        self.departement    = departement
        self.date           = date
        self.salary         = salary
        self.level          = level
        self.standard_hours = standard_hours
        self.employee_id    = employee_id

class Training(db.Model):
    __tablename__ = 'training'

    id            = db.Column(db.Integer,           primary_key = True)
    date          = db.Column(db.DateTime,          default= date.today())
    field         = db.Column(db.String(100))
    duration      = db.Column(db.Integer)

    training_emp  = db.relationship("Training_Emp", back_populates = "training")

    def __init__(self, date, duration):
        self.date        = date
        self.duration    = duration

class Training_Emp(db.Model):
    __tablename__ = 'training_emp'

    id            = db.Column(db.Integer,        primary_key = True)

    training_id   = db.Column(db.Integer, db.ForeignKey('training.id'), nullable = False)
    training      = db.relationship("Training",  back_populates = "training_emp")

    employee_id   = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable = False)
    employee      = db.relationship("Employee",  back_populates = "training_emp")

    def __init__(self, training_id, employee_id):
        self.training_id    = training_id
        self.employee_id    = employee_id

class Travel(db.Model):
    __tablename__ = 'travel'

    id            = db.Column(db.Integer,         primary_key = True)
    date          = db.Column(db.DateTime,        default= date.today())
    destination   = db.Column(db.String(100))
    duration      = db.Column(db.Integer)

    travel_emp    = db.relationship("Travel_Emp", back_populates = "travel")

    def __init__(self, date, duration, destination):
        self.date        = date
        self.duration    = duration
        self.destination = destination

class Travel_Emp(db.Model):
    __tablename__ = 'travel_emp'

    id            = db.Column(db.Integer,       primary_key = True)

    travel_id     = db.Column(db.Integer, db.ForeignKey('travel.id'), nullable = False)
    travel        = db.relationship("Travel",   back_populates = "travel_emp")

    employee_id   = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable = False)
    employee      = db.relationship("Employee", back_populates = "travel_emp")

    def __init__(self, travel_id, employee_id):
        self.travel_id      = travel_id
        self.employee_id    = employee_id
    
class Working(db.Model):
    __tablename__ = 'working'

    id            = db.Column(db.Integer,       primary_key = True)
    checkin_date  = db.Column(db.DateTime,      nullable = False)
    checkout_date = db.Column(db.DateTime)

    employee_id   = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable = False)
    employee      = db.relationship("Employee", back_populates = "working")

    def __init__(self, checkin_date, checkout_date, employee_id):
        self.checkin_date   = checkin_date
        self.checkout_date  = checkout_date
        self.employee_id    = employee_id

class Project(db.Model):
    __tablename__ = 'project'

    id                      = db.Column(db.Integer,     primary_key = True)
    description             = db.Column(db.String(100), nullable = False)
    period                  = db.Column(db.Integer,     nullable = False)
    starting_date           = db.Column(db.DateTime,    nullable = False)

    manager_id      = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable = False)
    manager         = db.relationship("Employee", back_populates = "project")

    project_rating  = db.relationship("Project_Rating", back_populates = "project")

    def __init__(self, manager_id, description, period, starting_date):
        self.manager_id      = manager_id
        self.description     = description
        self.periode         = periode
        self.starting_date   = starting_date

class Project_Rating(db.Model):
    __tablename__ = 'project_rating'

    id                      = db.Column(db.Integer,     primary_key = True)
    performance_rating      = db.Column(db.Integer,     nullable = False)

    employee_id     = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable = False, unique = True)
    employee        = db.relationship("Employee", back_populates = "project_rating")

    project_id      = db.Column(db.Integer, db.ForeignKey('project.id'), nullable = False, unique = True)
    project         = db.relationship("Project", back_populates = "project_rating")

    def __init__(self, employee_id, project_id, performance_rating):
        self.employee_id            = employee_id
        self.project_id             = project_id
        self.performance_rating     = performance_rating
