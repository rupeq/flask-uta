from application import app, db, api
from flask import render_template, request, Response, json, jsonify, redirect, flash, session
from flask_restful import Resource
from application.models import User, Course, Enrollment
from application.forms import *

# REST

class GetPostAPI(Resource):
    def get(self):
        return jsonify(User.objects.all())
    def post(self):
        data = api.payload
        user = User(user_id=data['user_id'], email=data['email'], first_name=data['first_name'], last_name=data['last_name'])
        user.set_password(data['password'])
        user.save()
        return jsonify(User.objects(user_id=data['user_id']))

class GetUpdateDeleteAPI(Resource):
    def get(self, idx):
        return jsonify(User.objects(user_id=idx))


# Flask

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template('index.html', index=True)

@app.route("/courses/")
@app.route("/courses/<term>")
def courses(term=None):
    if term is None:
        term = "Fall 2020"
    classes = Course.objects.order_by("+courseID")
    return render_template('courses.html', coursesData=classes, courses=True, term=term)

@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_id = User.objects.count()
        user_id += 1

        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data

        user = User(user_id=user_id, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()

        flash("You are successfully registered!", "success")
        return redirect("/index")
    return render_template('register.html', title="Register", form=form, register=True)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('username'):
        return redirect('/index')

    form = LoginForm()
    if form.validate_on_submit():
        email    = form.email.data
        password = form.password.data
        user     = User.objects(email=email).first()
        if user and user.get_password(password):
            flash(f"{user.first_name}, you are successfully logged in!", "success")
            session['user_id'] = user.user_id
            session['username'] = user.first_name
            return redirect("/index")
        else:
            flash("Sorry, try again! Something went wrong.", "danger")
    return render_template('login.html', title="Login", form=form, login=True)

@app.route("/logout")
def logout():
    session['user_id'] = False
    session.pop('username', None)
    return redirect("/index")

@app.route("/enrollment", methods=["GET", "POST"])
def enrollment():
    if not session.get('username'):
        return redirect('/login')
    courseID = request.form.get('courseID')
    courseTitle = request.form.get('title')
    user_id = session.get('user_id')
    if courseID:
        if Enrollment.objects(user_id=user_id, courseID=courseID):
            flash(f"Oops! You are already registered in the course {courseTitle}!", "danger")
            return redirect('/courses')
        else:
            Enrollment(user_id=user_id, courseID=courseID).save()
            flash(f"You are enrolled in {courseTitle}!", "success")
    classes = list(User.objects.aggregate(*[
            {
                '$lookup': {
                    'from': 'enrollment',
                    'localField': 'user_id',
                    'foreignField': 'user_id',
                    'as': 'enrolled1'
                }
            }, {
                '$unwind': {
                    'path': '$enrolled1',
                    'includeArrayIndex': 'enrolled1_id',
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$lookup': {
                    'from': 'course',
                    'localField': 'enrolled1.courseID',
                    'foreignField': 'courseID',
                    'as': 'enrolled2'
                }
            }, {
                '$unwind': {
                    'path': '$enrolled2',
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$match': {
                    'user_id': user_id
                }
            }, {
                '$sort': {
                    'courseID': 1
                }
            }
        ]))

    return render_template('enrollment.html', enrollment=True, classes=classes)


@app.route("/user")
def user():
    users = User.objects.all()
    return render_template("user.html", users=users)