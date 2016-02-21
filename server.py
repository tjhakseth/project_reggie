from jinja2 import StrictUndefined
from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import json
# add the classes after db once established
from model import connect_to_db, db, Company, User, Event, Question, Answer


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "Reggieevents"
# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def homepage():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/create_company', methods=['GET'])
def create_company():
    """Show form for company to signup."""

    return render_template("create_company_form.html")


@app.route('/create_company', methods=['POST'])
def process_create_company():
    """Process a newly created company"""

    # Get form variables
    company_name = request.form["companyname"]
    company_email = request.form["companyemail"]
    contact_person = request.form["contactperson"]
    company_phone = request.form["companyphone"]
    company_address = request.form["companyaddress"]
    password = request.form["password"]

    new_company = Company(company_name=company_name,
                            company_email=company_email,
                            contact_person=contact_person,
                            company_phone=company_phone,
                            company_address=company_address,
                            password=password)

    db.session.add(new_company)
    db.session.commit()

    flash("Company %s added." % company_name)
    return redirect("/company_login")


@app.route('/company_login', methods=['GET'])
def company_login():
    """Company login page"""

    return render_template("company_login_form.html")


@app.route('/company_login', methods=['POST'])
def company_login_process():
    """Process company login."""

    # Get form variables
    company_email = request.form["company_email"]
    password = request.form["password"]

    company = Company.query.filter_by(company_email=company_email).first()

    if not company:
        flash("No such company")
        return redirect("/company_login")

    if company.password != password:
        flash("Incorrect password")
        return redirect("/company_login")

    session["company_id"] = company.company_id

    flash("Logged in")
    return redirect("/company_profile/%s" % company.company_id)


@app.route("/company_profile/<int:company_id>")
def company_profile(company_id):
    """Show info about company."""

    company = Company.query.get(company_id)

    return render_template("company_profile.html", company=company)


@app.route('/create_user', methods=['GET'])
def create_user():
    """Show form for users to signup."""

    return render_template("create_user_form.html")


@app.route('/create_user', methods=['POST'])
def process_create_user():
    """Process a newly created user"""

    # Get form variables
    user_name = request.form["username"]
    user_email = request.form["useremail"]
    user_phone = request.form["userphone"]
    user_address = request.form["useraddress"]
    password = request.form["password"]

    new_user = User(user_name=user_name,
                    user_email=user_email,
                    user_phone=user_phone,
                    user_address=user_address,
                    password=password)

    db.session.add(new_user)
    db.session.commit()

    flash("User %s added." % user_email)
    return redirect("/user_login")


@app.route('/user_login', methods=['GET'])
def user_login():
    """user login page"""

    return render_template("user_login_form.html")


@app.route('/user_login', methods=['POST'])
def user_login_process():
    """Process user login."""

    # Get form variables
    user_email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(user_email=user_email).first()

    if not user:
        flash("No such user")
        return redirect("/user_login")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/user_login")

    session["user_id"] = user.user_id

    flash("Logged in")
    return redirect("/user_profile/%s" % user.user_id)


@app.route("/user_profile/<int:user_id>")
def user_detail(user_id):
    """Show info about user."""

    user = User.query.get(user_id)
    events = set()

    for answer in user.answers:
        events.add(answer.event)

    #look at optimzing this

    return render_template("user_profile.html", user=user, events=events)


@app.route('/create_event', methods=['GET'])
def create_event():
    """create event"""

    return render_template("create_event.html")


@app.route("/event_profile/<int:event_id>")
def event_profile(event_id):
    """Show info about company."""

    event = Event.query.get(event_id)

    return render_template("event_profile.html", event=event)


@app.route('/create_reg', methods=['POST'])
def create_registration_form():
    """create registration form"""

    company_id = session.get('company_id')
    event_name = request.form['event_name']
    number_of_fields = int(request.form['number_of_fields'])
    color = request.form['color']
    logo = request.form['logo']
    payment_page = request.form.get('payment_page', False)

    new_event = Event(event_name=event_name, company_id=company_id, number_of_fields=number_of_fields, payment_page=payment_page, color=color, logo=logo)

    db.session.add(new_event)
    db.session.commit()

    return render_template("create_registration_form.html", new_event=new_event, 
            number_of_fields=number_of_fields)


@app.route("/registration_form_submit/<int:event_id>", methods=['POST'])
def registration_form_submit(event_id):

    labels = request.form.getlist('label')
    selectors = request.form.getlist('selector')
    data = request.form.getlist('options')



    print "*****************************************"
    print data

    for i in range (len(labels)):
        new_question = Question()
        new_question.label=labels[i]
        new_question.selector=selectors[i]
        new_question.ordinal = i
        new_question.event_id = event_id
        field_options = data[i]
        if field_options:
            new_question.data = json.loads(data[i])
        else:
            new_question.data = None

        db.session.add(new_question)
        db.session.commit()

    flash("Successfully created event") 

    return redirect("/event_profile/%s" % event_id)


@app.route("/event_profile/<int:event_id>/live", methods=['GET'])
def event_profile_live(event_id):

    event = Event.query.get(event_id)

    return render_template("event_live.html", event=event)



@app.route("/event_profile/<int:event_id>/live", methods=['POST'])
def event_submit(event_id):

    event = Event.query.get(event_id)
    user_id = session.get("user_id")
    questions = event.questions
    values = request.form.getlist("question")
    
    question_ids = [q.id for q in questions]

    if not user_id:
        flash("Please log in to register for event")
        return redirect("/")

    for i in range (len(questions)):
        new_answer = Answer()
        new_answer.value = values[i]
        new_answer.question_id = question_ids[i]
        new_answer.user_id = user_id
        new_answer.event_id= event_id

        db.session.add(new_answer)
        db.session.commit()

    flash("Successfully Registered for event")


    return redirect("/user_profile/%s" % user_id)


@app.route("/event_profile/<int:event_id>/data", methods=['GET'])
def event_data(event_id):

    event = Event.query.get(event_id)
    answers = set()

    for answer in event.answers:
        answers.add(answer.event)

    user_id = answer.user_id

    return render_template("event_data.html", event=event, answers=answers, user_id=user_id)

@app.route("/event_profile/<int:event_id>/data/<int:user_id>", methods=['GET'])
def individual_event_data(event_id, user_id):

    event = Event.query.get(event_id)
    user = User.query.get(user_id)
    answers = set()

    for answer in event.answers:
        answers.add(answer.event)

    return render_template("individual_event_data.html", event=event, answers=answers, user=user)


@app.route("/event_profile/<int:event_id>/data/<int:user_id>", methods=['POST'])
def delete_record(event_id, user_id):

    user = User.query.get(user_id)
    event = Event.query.get(event_id)
    answers_for_user_and_event = Answer.query.filter_by(user_id=user_id, event_id=event_id).all()

    for answer in answers_for_user_and_event:
        db.session.delete(answer)
        db.session.commit()

    return redirect("/event_profile/%s/data" % event_id)



if __name__ == "__main__":
    
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()