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
from flask.ext.mail import Mail, Message
from jinja2 import StrictUndefined
import stripe
from werkzeug import secure_filename
# local
from model import connect_to_db, db, Company, User, Event, Question, Answer, Registration

stripe.api_key = "sk_test_GATVlXiqmnj4W65d3Bt1k82e"

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    #EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_SSL=False,
    MAIL_USE_TLS=True,
    MAIL_USERNAME = 'reggieevent@gmail.com',
    MAIL_PASSWORD = '31reggieevent'
    )
mail = Mail(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = "Reggieevents"

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
    company_city = request.form["companycity"]
    company_state = request.form["companystate"]
    company_zip = request.form["companyzip"]
    password = request.form["password"]
    password_bytes = password.encode('utf-8')

    # Hashing password
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    new_company = Company(company_name=company_name,
                            company_email=company_email,
                            contact_person=contact_person,
                            company_phone=company_phone,
                            company_address=company_address,
                            company_city=company_city,
                            company_state=company_state,
                            company_zip=company_zip,
                            password=hashed)

    # Adding the new company to the database
    db.session.add(new_company)
    db.session.commit()

    # Saving the session
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

    # Query for the company email
    company = Company.query.filter_by(company_email=company_email).first()

    if not company:
        flash("Incorrect login credentials")
        return redirect("/company_login")

    # Verifying the password
    if bcrypt.hashpw(password_bytes, hashed) == hashed:
        flash("Welcome")
    else:
        flash("Incorrect login credentials")
        return redirect("/company_login")

    # Saving the session
    session["company_id"] = company.company_id

    flash("Logged in")

    return redirect("/company_profile/%s" % company.company_id)


@app.route("/company_profile/<company_id>")
def company_profile(company_id):
    """Show info about company."""

    company = Company.query.get(company_id)
    company_id = session.get("company_id")

    # Verifying the company is logged in
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
    user_firstname = request.form["user_firstname"]
    user_lastname = request.form["user_lastname"]
    user_email = request.form["useremail"]
    user_phone = request.form["userphone"]
    password = request.form["password"]
    password_bytes = password.encode('utf-8')

    # Hashing the password
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    new_user = User(user_firstname=user_firstname,
                    user_lastname=user_lastname,
                    user_email=user_email,
                    user_phone=user_phone,
                    password=hashed)

    # Adding the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # Saving the session
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

    # Hashing the password
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    # Looking up the user in the database 
    user = User.query.filter_by(user_email=user_email).first()

    if not user:
        flash("Incorrect login credentials")
        return redirect("/user_login")

    # Verifying the password
    if bcrypt.hashpw(password_bytes, hashed) == hashed:
        flash("Welcome")
    else:
        flash("Incorrect login credentials")
        return redirect("/user_login")

    # Saving the session
    session["user_id"] = user.user_id

    flash("Logged in")

    return redirect("/user_profile/%s" % user.user_id)


@app.route("/user_profile/<user_id>")
def user_detail(user_id):
    """Show info about user."""

    user = User.query.get(user_id)
    logged_user_id = session.get("user_id")

    # Verifying the user
    if user.user_id != logged_user_id:
        raise Exception("User is not logged in.")

    return render_template("user_profile.html", user=user)


@app.route('/create_event', methods=['GET'])
def create_event():
    """create event"""

    return render_template("create_event.html")


@app.route('/create_reg', methods=['GET', 'POST'])
def create_registration_form():
    """create event for registration form and landing page"""

    # Get form variables
    company_id=session.get('company_id')
    event_name=request.form['event_name']
    venue=request.form['venue']
    address=request.form['address']
    city=request.form['city']
    state=request.form['state']
    zipcode=request.form['zipcode']
    date=request.form['date']
    description=request.form['description']
    number_of_fields = int(request.form['number_of_fields'])
    color = request.form['color']
    logo= request.files['logo']
    logo = logo.filename
    price = request.form['price']

    new_event = Event(event_name=event_name,
                    company_id=company_id,
                    venue=venue,
                    address=address,
                    city=city,
                    state=state,
                    zipcode=zipcode,
                    date=date,
                    description=description, 
                    number_of_fields=number_of_fields, 
                    price=price, 
                    color=color, 
                    logo=logo)

    # Adding new event to the database
    db.session.add(new_event)
    db.session.commit()

    # If there is a logo, calls the upload file function
    if logo:
        upload = upload_file()

    return render_template("create_registration_form.html", new_event=new_event, 
            number_of_fields=number_of_fields)

def allowed_file(filename):
    """formatting the filename"""

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file():
    """saving the logo to folder static/uploads"""

    if request.method == 'POST':
        file = request.files['logo']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            

@app.route("/registration_form_submit/<event_id>", methods=['POST'])
def registration_form_submit(event_id):
    """User builds structure of the registration form"""

    # Get form variables
    labels = request.form.getlist('label')
    print "**************************"
    print labels
    selectors = request.form.getlist('selector')
    print "**************************"
    print selectors
    data = request.form.getlist('data')
    print "**************************"
    print data



    # For each label creates a new question
    for i in range (len(labels)):
        new_question = Question()
        new_question.label=labels[i]
        new_question.selector=selectors[i]
        new_question.ordinal = i
        new_question.event_id = event_id
        field_options = data[i]
        #Json for the options for the selectors
        if field_options:
            new_question.data = json.loads(data[i])
        else:
            new_question.data = None

        # Adds each question to the database
        db.session.add(new_question)
        db.session.commit()

    flash("Successfully created event") 

    return redirect("/event_profile/%s" % event_id)


@app.route("/event_profile/<event_id>")
def event_profile(event_id):
    """Event Dashboard for companies"""

    # Gets the specific event
    event = Event.query.get(event_id)

    # Verify the company login
    company = event.company_id
    company_id = session.get("company_id")

    if company != company_id:
        raise Exception("Company is not logged in.")

    return render_template("event_profile.html", event=event)


@app.route("/event_profile/<event_id>/chart_data.json")
def get_data(event_id):
    """Dashbord charts for the event"""

    # Gets the specific event
    event = Event.query.get(event_id)

    # Empty Dictionary for the Json file
    chart_data = {}

    # Creates the x axis for the chart(date)
    chart_data['labels'] = []
    for reg in event.registrations:
        day =reg.timestamp.day
        month =reg.timestamp.month
        #hour =reg.timestamp.hour
        #minute =reg.timestamp.minute
        date = "%s/%s" %(month, day)
        #time = "%s:%s" %(hour, minute)
        if date not in chart_data['labels']:
            chart_data['labels'].append()

        # data.append(len(event.registrations))

    # Creates the data points 
    number = list(enumerate(event.registrations, start=1)) 
    data = []
    for i in number:
        data.append(i[0])

    # Creats the y axis for the chart and color scheme
    chart_data['datasets'] = [
            {
                "label": "Registrations",
                "fillColor": "rgba(151,187,205,0.2)",
                "strokeColor": "rgba(151,187,205,1)",
                "pointColor": "rgba(151,187,205,1)",
                "pointStrokeColor": "#fff",
                "pointHighlightFill": "#fff",
                "pointHighlightStroke": "rgba(151,187,205,1)",
                "data": data
            },
        ]

    return jsonify(chart_data)


@app.route("/event_list", methods=["GET"])
def event_list():
    """List of all live events"""

    # Gets the events from the database
    events = Event.query.order_by('event_name').all()

    return render_template("event_list.html", events=events)


@app.route("/event_profile/<event_id>/home", methods=['GET'])
def event_landing_page(event_id):
    """Landing page for an event"""

    # Gets the specific event information
    event = Event.query.get(event_id)

    # Checks for a logo and calls upload_file if there is a logo
    if event.logo:
        logo = uploaded_file(event.logo)

    return render_template("landing_page.html", event=event)


def uploaded_file(filename):
    """Uploads the logo on the landing page"""

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/event_profile/<event_id>/live", methods=['GET'])
def event_profile_live(event_id):
    """Registration form for an event"""

    # Gets the specific event information
    event = Event.query.get(event_id)

    # Checks for a logo and calls upload_file if there is a logo
    if event.logo:
        logo = uploaded_file(event.logo)

    return render_template("event_live.html", event=event)

def uploaded_file(filename):
    """Uploads the logo on the landing page"""

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/event_profile/<event_id>/live", methods=['POST'])
def event_submit(event_id):
    """Saves registration information about user for an event"""

    # Gets the specific event information
    event = Event.query.get(event_id)

    # Verifies the user
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to register for event")
        return redirect("/")

    # Gets Form Variables
    questions = event.questions
    values = request.form.getlist("question")

    # Gets Id for each question
    question_ids = [q.id for q in questions]

    # Adds a new registration to the session
    new_registration = Registration()
    new_registration.user_id = user_id
    new_registration.event_id= event_id
    new_registration.timestamp= datetime.now()

    db.session.add(new_registration)
    
    # Adds the answers for each question to the session
    for i in range (len(questions)):
        new_answer = Answer()
        new_answer.value = values[i]
        new_answer.question_id = question_ids[i]
        new_answer.registration = new_registration


        db.session.add(new_answer)
    # Commits both the registration and all the answers to the database    
    db.session.commit()

    # Charge the attendee
    token = request.form.get('stripeToken', None)
    if token is not None:
        charged_id = charge_card(token, event.price)
        # TODO: store the charge_id in the event
        if not charged_id:
            raise Exception("Payment error")
    
    flash("Successfully Registered for event")

    msg = Message("You're Registered!!!!",
                  sender="reggieevents@gmail.com",
                  recipients=["tjhakseth@gmail.com"])
    msg.body = "This is the email body"
    mail.send(msg)

    return redirect("/user_profile/%s" % user_id)

    
def charge_card(token, value):
    """Charges the credit card using Stripe API"""

    stripe.api_key = "sk_test_GATVlXiqmnj4W65d3Bt1k82e"

    # Create the charge on Stripe's servers - this will charge the user's card
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
    """Displays every row of data to the company"""

    # Gets the event specific information
    event = Event.query.get(event_id)

    # Verifies the company
    logged_company_id = session.get("company_id")
    if event.company_id != logged_company_id:
        raise Exception("Company is not logged in.")

    return render_template("event_data.html", event=event)


@app.route("/event_profile/<event_id>/csvdata", methods=['GET'])
def download_to_csv(event_id):
    """Downloads the registration data to a CSV"""

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
    """Displays an individual registrants data"""

    # Gets the event specific information
    event = Event.query.get(event_id)

    # Verifies that the company is logged in
    registration = Registration.query.get(registration_id)
    logged_company_id = session.get("company_id")
    if event.company_id != logged_company_id:
        raise Exception("Company is not logged in.")
    if event.event_id != registration.event_id:
        raise Exception("Event is wrongo")

    return render_template("individual_event_data.html", registration=registration)


@app.route("/event_profile/<event_id>/data/<registration_id>/delete", methods=['POST'])
def delete_record(event_id, registration_id):
    """Deletes an individual registrants data from the site and database"""

    # Gets the registrants information
    registration = Registration.query.get(registration_id)

    # Verifies that the company is logged in
    event = Event.query.get(event_id)
    logged_company_id = session.get("company_id")
    if event.company_id != logged_company_id:
        raise Exception("Company is not logged in.")
    if event.event_id != registration.event_id:
        raise Exception("Event is wrongo")

    # Deletes row from the database
    db.session.delete(registration)
    db.session.commit()

    return redirect("/event_profile/%s/data" % event_id)



if __name__ == "__main__":
    
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()