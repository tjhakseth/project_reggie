"""Flask Endpoints for Reggie."""
from datetime import datetime
import json
from StringIO import StringIO
import os
# third party
import bcrypt
from csvkit import CSVKitWriter
from flask import Flask, Response, render_template, request, flash, redirect, session, jsonify, send_from_directory
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.mail import Mail, Message
from jinja2 import StrictUndefined
import stripe
from werkzeug import secure_filename
from werkzeug.exceptions import Forbidden
# local
from model import connect_to_db, db, Company, User, Event, Question, Answer, Registration

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_SSL=False,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='reggieevent@gmail.com',
    MAIL_PASSWORD='31reggieevent',
    STRIPE_KEY="sk_test_GATVlXiqmnj4W65d3Bt1k82e"
)
mail = Mail(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = "Reggieevents"

app.jinja_env.undefined = StrictUndefined
stripe.api_key = app.config['STRIPE_KEY']


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

    flash("%s added." % company_name, "success")

    return redirect("/company_profile/%s" % new_company.company_id)


@app.route('/company_login', methods=['GET'])
def company_login():
    """Company login page"""

    return render_template("company_login_form.html")


@app.route('/company_login', methods=['POST'])
def company_login_process():
    """Process company login."""

    # Get form variables
    company_email = request.form["email"]
    password = request.form["password"]
    password_bytes = password.encode('utf-8')

    # Query for the company email
    company = Company.query.filter_by(company_email=company_email).first()
    company_pw = company.password.encode('utf-8')

    if not company:
        flash("Incorrect login credentials", "danger")
        return redirect("/company_login")

    # Verifying the password
    if bcrypt.hashpw(password_bytes, company_pw) == company_pw:
        flash("Succcessfully Logged In", "success")
    else:
        flash("Incorrect login credentials", "danger")
        return redirect("/company_login")

    # Saving the session
    session["company_id"] = company.company_id

    return redirect("/company_profile/%s" % company.company_id)


@app.route("/company_profile/<company_id>")
def company_profile(company_id):
    """Show info about company."""

    company = Company.query.get(company_id)
    company_id = session.get("company_id")

    # Verifying the company is logged in
    if company.company_id != company_id:
        raise Forbidden("Company is not logged in.")

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
    user_email = request.form["user_email"]
    user_phone = request.form["user_phone"]
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

    flash("%s added." % user_email, "success")

    return redirect("/user_profile/%s" % new_user.user_id)


@app.route('/user_login', methods=['GET'])
def user_login():
    """User login page"""

    return render_template("user_login_form.html")


@app.route('/user_login', methods=['POST'])
def user_login_process():
    """Process user login."""

    # Get form variables
    user_email = request.form["email"]
    password = request.form["password"]
    password_bytes = password.encode('utf-8')

    # Looking up the user in the database
    user = User.query.filter_by(user_email=user_email).first()
    user_pw = user.password.encode('utf-8')

    if not user:
        flash("Incorrect login credentials", "danger")
        return redirect("/user_login")

    # Verifying the password
    if bcrypt.hashpw(password_bytes, user_pw) == user_pw:
        flash("Succcessfully Logged In", "success")
    else:
        flash("Incorrect login credentials", "danger")
        return redirect("/user_login")

    # Saving the session
    session["user_id"] = user.user_id

    return redirect("/user_profile/%s" % user.user_id)


@app.route("/user_profile/<user_id>")
def user_detail(user_id):
    """Show info about user."""

    user = User.query.get(user_id)
    logged_user_id = session.get("user_id")

    # Verifying the user
    if user.user_id != logged_user_id:
        raise Forbidden("User is not logged in.")

    return render_template("user_profile.html", user=user)


@app.route('/create_event', methods=['GET'])
def create_event():
    """Create event"""

    return render_template("create_event.html")


@app.route('/create_reg', methods=['GET', 'POST'])
def create_registration_form():
    """Create event for registration form and landing page"""

    company_id = session.get('company_id')
    if not company_id:
        raise Forbidden("Company is not logged in.")

    errors = ''
    event_name = request.form['event_name']
    venue = request.form['venue']
    address = request.form['address']
    city = request.form['city']
    state = request.form['state']
    zipcode = request.form['zipcode']
    start_date = request.form['startdate']
    end_date = request.form['enddate']
    start_time = request.form['starttime']
    end_time = request.form['endtime']
    description = request.form['description']
    color = request.form['color']
    logo = request.files['logo']
    logo = logo.filename
    price = request.form['price']

    fields = [
        event_name, venue, address, city, state, zipcode, start_date, end_date,
        start_time, end_time, description, color, logo, price
    ]
    fields_empty = [not f for f in fields]

    if any(fields_empty):
        errors = "errors"
        flash("Please enter all required fields", "warning")

    if not errors:
        new_event = Event(
            event_name=event_name,
            company_id=company_id,
            venue=venue,
            address=address,
            city=city,
            state=state,
            zipcode=zipcode,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            description=description,
            price=price,
            color=color,
            logo=logo
        )

        # Adding new event to the database
        db.session.add(new_event)
        db.session.commit()

        # If there is a logo, calls the upload file function
        if logo:
            upload_file()

        return render_template("create_registration_form.html", new_event=new_event)

    return render_template("create_event.html", errors=errors)


def allowed_file(filename):
    """Formatting the filename"""

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file():
    """Saving the logo to folder static/uploads"""

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
    for i in range(len(labels)):
        new_question = Question()
        new_question.label = labels[i]
        new_question.selector = selectors[i]
        new_question.ordinal = i
        new_question.event_id = event_id
        field_options = data[i]
        # Json for the options for the selectors
        if field_options:
            new_question.data = json.loads(data[i])
        else:
            new_question.data = None

        # Adds each question to the database
        db.session.add(new_question)
        db.session.commit()

    flash("Successfully created event", "success")

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
        raise Forbidden("Company is not logged in.")

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
        # day =reg.timestamp.day
        # month =reg.timestamp.month
        hour = reg.timestamp.hour
        minute = reg.timestamp.minute
        # date = "%s/%s" %(month, day)
        time = "%s:%s" % (hour, minute)
        if time not in chart_data['labels']:
            chart_data['labels'].append(time)

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
                "fillColor": "#e6e6e6",
                "strokeColor": "#7a5252",
                "pointColor": "#7a5252",
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
        uploaded_file(event.logo)

    return render_template("landing_page.html", event=event)


def uploaded_file(filename):
    """Uploads the logo on the landing page"""

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/event_profile/<event_id>/live", methods=['GET'])
def event_profile_live(event_id):
    """Registration form for an event"""

    # Gets the specific event information
    event = Event.query.get(event_id)

    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to register for event", "warning")
        return redirect("/")
    user = User.query.get(user_id)
    print"****************************"
    print event
    print user

    if event.logo:
        uploaded_file(event.logo)

    return render_template("event_live.html", event=event, user=user)


@app.route("/event_profile/<event_id>/live", methods=['POST'])
def event_submit(event_id):
    """Saves registration information about user for an event"""

    # Gets the specific event information
    event = Event.query.get(event_id)

    # Verifies the user
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to register for event", "warning")
        return redirect("/")
    # user = User.query.get(user_id)

    # Gets Form Variables
    questions = event.questions
    values = request.form.getlist("question")

    # Gets Id for each question
    question_ids = [q.id for q in questions]

    # Adds a new registration to the session
    new_registration = Registration()
    new_registration.user_id = user_id
    new_registration.event_id = event_id
    new_registration.timestamp = datetime.now()

    db.session.add(new_registration)

    # Adds the answers for each question to the session
    for i in range(len(questions)):
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

    flash("Successfully Registered for event", "success")

    msg = Message("You're Registered!!!!",
                  sender="reggieevents@gmail.com",
                  recipients=["tjhakseth@gmail.com"])
    msg.body = "This is the email body"
    mail.send(msg)

    # return redirect("/user_profile/%s" % user_id)
    return render_template("success.html", event=event, user_id=user_id)


def charge_card(token, value):
    """Charges the credit card using Stripe API"""
    # Create the charge on Stripe's servers - this will charge the user's card
    result = None
    try:
      charge = stripe.Charge.create(
          amount=value * 100,  # amount in cents, again
          currency="usd",
          source=token,
          description="Example charge"
      )
      result = charge.id
    except stripe.error.CardError:
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
        raise Forbidden("Company is not logged in.")

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
        sorted_answers = sorted(registration.answers, key=lambda a: a.question.ordinal)
        for answer in sorted_answers:
            data.append(answer.value)
        writer.writerow(data)

    return Response(f.getvalue(), mimetype='text/csv')


@app.route("/event_profile/<event_id>/data/<registration_id>", methods=['GET', 'POST'])
def individual_registration(event_id, registration_id):
    """Displays an individual registrants data"""

    # Gets the event specific information
    event = Event.query.get(event_id)

    # Verifies that the company is logged in
    registration = Registration.query.get(registration_id)

    logged_company_id = session.get("company_id")
    if event.company_id != logged_company_id:
        raise Forbidden("Company is not logged in.")
    if event.event_id != registration.event_id:
        raise Forbidden("Event is wrongo")

    return render_template("individual_event_data.html", registration=registration)


@app.route("/event_profile/<event_id>/data/<registration_id>/delete", methods=['POST'])
def delete_record(event_id, registration_id):
    """Deletes an individual registrants data from the site and database"""

    # Gets the registrants information
    registration = Registration.query.get(registration_id)
    event = Event.query.get(event_id)

    # Verifies that the company is logged in
    logged_company_id = session.get("company_id")
    if event.company_id != logged_company_id:
        raise Forbidden("Company is not logged in.")
    if event.event_id != registration.event_id:
        raise Forbidden("Event is wrongo")

    answers_for_reg = Answer.query.filter_by(registration_id=registration_id).all()

    for answer in answers_for_reg:
         db.session.delete(answer)

    # Deletes row from the database
    db.session.delete(registration)
    db.session.commit()

    return redirect("/event_profile/%s/data" % event_id)


def get_sorted_registration_answers(registration):
    """Fetches all answers for the registration, sorted by question.ordinal"""
    answers = Answer.query.join(
        Question
    ).filter(
        Answer.registration == registration
    ).order_by(
        Question.ordinal
    ).all()

    return answers


@app.route("/event_profile/<event_id>/data/<registration_id>/edit", methods=['GET'])
def edit_record(event_id, registration_id):
    """Opens the editable an individual registrants data from the site and database"""

    registration = Registration.query.get(registration_id)

    return render_template("edit_record.html", registration=registration)


@app.route("/event_profile/<event_id>/data/<registration_id>/edit", methods=['POST'])
def edit_record_submit(event_id, registration_id):
    """Submits the edited individual registrants data from the site and database"""

    registration = Registration.query.get(registration_id)

    event = Event.query.get(event_id)
    logged_company_id = session.get("company_id")
    if event.company_id != logged_company_id:
        raise Forbidden("Company is not logged in.")
    if event.event_id != registration.event_id:
        raise Forbidden("Event is wrongo")

    # import pdb; pdb.set_trace()
    answers = get_sorted_registration_answers(registration)
    for i in range(len(answers)):
        answer = answers[i]
        print answer.question.label
        print "**********************"
        print answer
        value_key = 'value_%s' % i
        value = request.form.get(value_key)
        print "**********************"
        print value_key
        if answer.value != value:
            answer.value = value
            db.session.add(answer)

    db.session.commit()

    return redirect("/event_profile/%s/data/%s" % (event_id, registration_id))


if __name__ == "__main__":
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
