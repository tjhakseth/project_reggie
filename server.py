from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

# add the classes after db once established
from model import connect_to_db, db, Company, User, Event, User_event


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

    flash("Company %s added." % email)
    return redirect("/company/%s" % new_company.company_id)

@app.route('/company_login')
def company_login():
    """Company login page"""

    return render_template("company_login_form.html")

@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No such user")
        return redirect("/login")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id

    flash("Logged in")
    return redirect("/users/%s" % user.user_id)


@app.route('/user_login')
def user_login():
    """user login page"""

    return render_template("user_login_form.html")

@app.route("/company/<int:company_id>")
def company_detail(company_id):
    """Show info about company."""

    company = Company.query.get(company_id)
    return render_template("company.html", company=company)

@app.route('/one_page')
def one_page_registration():
    """One page registration"""

    return render_template("sample_form.html")

@app.route('/one_page', methods=["POST"])
def process_one_page():
    """Shows successful registration"""

    first = request.form.get("firstname")
    last = request.form.get("lastname")
    email = request.form.get("email")

    return render_template("sample_success.html",
                            firstname=first,
                            lastname=last,
                            email=email)

 
@app.route('/charge')
def payment():
    """Payment page"""

    return render_template("payment.html")






if __name__ == "__main__":
    
    app.debug = True

    # connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()