# stdlib
from datetime import datetime
import json
import sys
import uuid
from StringIO import StringIO
import os
# third party
import bcrypt
from csvkit import CSVKitWriter, CSVKitReader
from flask import Flask, Response, render_template, request, flash, redirect, session, jsonify, url_for, send_from_directory
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.uuid import FlaskUUID
from jinja2 import StrictUndefined
import stripe
from werkzeug import secure_filename
# local
from model import connect_to_db, db, Company, User, Event, Question, Answer, Registration

stripe.api_key = "sk_test_GATVlXiqmnj4W65d3Bt1k82e"

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#FlaskUUID(app)


# Required to use Flask sessions and the debug toolbar
app.secret_key = "Reggieevents"
# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined

# def allowed_file(filename):
#     """saving the logo"""

#     return '.' in filename and \
#            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

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
    password_bytes = password.encode('utf-8')

    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    new_company = Company(company_name=company_name,
                            company_email=company_email,
                            contact_person=contact_person,
                            company_phone=company_phone,
                            company_address=company_address,
                            password=hashed)

    db.session.add(new_company)
    db.session.commit()

    session["company_id"] = new_company.company_id

    flash("Company %s added." % company_name)
    flash("Logged in")
    return redirect("/company_profile/%s" % new_company.company_id)


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
    password_bytes = password.encode('utf-8')

    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    company = Company.query.filter_by(company_email=company_email).first()

    if not company:
        flash("Incorrect login credentials")
        return redirect("/company_login")

    if bcrypt.hashpw(password_bytes, hashed) == hashed:
        flash("Welcome")
    else:
        flash("Incorrect login credentials")
        return redirect("/company_login")

    session["company_id"] = company.company_id

    flash("Logged in")
    return redirect("/company_profile/%s" % company.company_id)


@app.route("/company_profile/<company_id>")
def company_profile(company_id):
    """Show info about company."""

    company = Company.query.get(company_id)
    company_id = session.get("company_id")

    if company.company_id != company_id:
        raise Exception("Company is not logged in.")

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
    password_bytes = password.encode('utf-8')

    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    new_user = User(user_name=user_name,
                    user_email=user_email,
                    user_phone=user_phone,
                    user_address=user_address,
                    password=hashed)

    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.user_id

    flash("User %s added." % user_email)
    flash("Logged in")
    return redirect("/user_profile/%s" % new_user.user_id)


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
    password_bytes = password.encode('utf-8')

    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    user = User.query.filter_by(user_email=user_email).first()

    if not user:
        flash("Incorrect login credentials")
        return redirect("/user_login")

    if bcrypt.hashpw(password_bytes, hashed) == hashed:
        flash("Welcome")
    else:
        flash("Incorrect login credentials")
        return redirect("/user_login")

    session["user_id"] = user.user_id

    flash("Logged in")
    return redirect("/user_profile/%s" % user.user_id)


@app.route("/user_profile/<user_id>")
def user_detail(user_id):
    """Show info about user."""

    user = User.query.get(user_id)
    logged_user_id = session.get("user_id")

    if user.user_id != logged_user_id:
        raise Exception("User is not logged in.")


    return render_template("user_profile.html", user=user)


@app.route('/create_event', methods=['GET'])
def create_event():
    """create event"""

    return render_template("create_event.html")


@app.route('/create_reg', methods=['GET', 'POST'])
def create_registration_form():
    """create registration form"""


    company_id = session.get('company_id')
    event_name = request.form['event_name']
    number_of_fields = int(request.form['number_of_fields'])
    color = request.form['color']
    logo= request.files['logo']
    logo = logo.filename
    payment_page = request.form.get('payment_page', False)
    price = request.form['price']

    new_event = Event(event_name=event_name, company_id=company_id, number_of_fields=number_of_fields, payment_page=payment_page, price=price, color=color, logo=logo)

    db.session.add(new_event)
    db.session.commit()

    
    if logo:
        upload = upload_file()

    return render_template("create_registration_form.html", new_event=new_event, 
            number_of_fields=number_of_fields)

def allowed_file(filename):
    """saving the logo"""

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file():
    if request.method == 'POST':
        file = request.files['logo']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            

@app.route("/registration_form_submit/<event_id>", methods=['POST'])
def registration_form_submit(event_id):

    labels = request.form.getlist('label')
    selectors = request.form.getlist('selector')
    data = request.form.getlist('options')

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


@app.route("/event_profile/<event_id>")
def event_profile(event_id):
    """Show info about company."""

    event = Event.query.get(event_id)
    # company = event.company_id
    # company_id = session.get("company_id")

    # if company != company_id:
    #     raise Exception("Company is not logged in.")

    return render_template("event_profile.html", event=event)


@app.route("/event_list", methods=["GET"])
def event_list():

    events = Event.query.order_by('event_name').all()

    return render_template("event_list.html", events=events)


@app.route("/event_profile/<event_id>/live", methods=['GET'])
def event_profile_live(event_id):

    # import pdb; pdb.set_trace()


    event = Event.query.get(event_id)

    if event.logo:
        logo = uploaded_file(event.logo)

    return render_template("event_live.html", event=event)

def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route("/event_profile/<event_id>/live", methods=['POST'])
def event_submit(event_id):

    event = Event.query.get(event_id)
    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in to register for event")
        return redirect("/")

    questions = event.questions
    values = request.form.getlist("question")

    
    question_ids = [q.id for q in questions]


    new_registration = Registration()
    new_registration.user_id = user_id
    new_registration.event_id= event_id
    new_registration.timestamp= datetime.now()

    db.session.add(new_registration)
    

    for i in range (len(questions)):
        new_answer = Answer()
        new_answer.value = values[i]
        new_answer.question_id = question_ids[i]
        new_answer.registration = new_registration


        db.session.add(new_answer)
    db.session.commit()

    flash("Successfully Registered for event")

    # Charge if necessary
    token = request.form.get('stripeToken', None)
    # import pdb; pdb.set_trace()
    if token is not None:
        charged_id = charge_card(token, event.price)
        # TODO: store the charge_id in the event
        if not charged_id:
            raise Exception("Payment error")
    
    return redirect("/user_profile/%s" % user_id)

    
def charge_card(token, value):
    stripe.api_key = "sk_test_GATVlXiqmnj4W65d3Bt1k82e"

    # # Create the charge on Stripe's servers - this will charge the user's card
    result = None
    try:
      charge = stripe.Charge.create(
          amount=value * 100, # amount in cents, again
          currency="usd",
          source=token,
          description="Example charge"
      )
      result = charge.id
    except stripe.error.CardError, e:
        pass
    
    return result


@app.route("/event_profile/<event_id>/data", methods=['GET'])
def event_data(event_id):

    event = Event.query.get(event_id)
    logged_company_id = session.get("company_id")

    if event.company_id != logged_company_id:
        raise Exception("Company is not logged in.")


    return render_template("event_data.html", event=event)


@app.route("/event_profile/<event_id>/csvdata", methods=['GET'])
def download_to_csv(event_id):

    f = StringIO()
    writer = CSVKitWriter(f)

    # List headers
    event = Event.query.get(event_id)
    headers = []
    for question in event.questions:
        headers.append(question.label)
    writer.writerow(headers)
    
    # List entries for each registration
    for registration in event.registrations:
        data = []
        for answer in registration.answers:
            data.append(answer.value)
        writer.writerow(data)

    return Response(f.getvalue(), mimetype='text/csv')


@app.route("/event_profile/<event_id>/data/<registration_id>", methods=['GET'])
def individual_registration(event_id, registration_id):

    event = Event.query.get(event_id)
    registration = Registration.query.get(registration_id)
    logged_company_id = session.get("company_id")

    if event.company_id != logged_company_id:
        raise Exception("Company is not logged in.")
    if event.event_id != registration.event_id:
        raise Exception("Event is wrongo")


    return render_template("individual_event_data.html", registration=registration)


@app.route("/event_profile/<event_id>/data/<registration_id>/delete", methods=['POST'])
def delete_record(event_id, registration_id):

    registration = Registration.query.get(registration_id)
    event = Event.query.get(event_id)
    logged_company_id = session.get("company_id")

    if event.company_id != logged_company_id:
        raise Exception("Company is not logged in.")
    if event.event_id != registration.event_id:
        raise Exception("Event is wrongo")

    db.session.delete(registration)
    db.session.commit()

    return redirect("/event_profile/%s/data" % event_id)



if __name__ == "__main__":
    
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()