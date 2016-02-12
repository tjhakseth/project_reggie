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

    flash("Company %s added." % company_name)
    return redirect("/company/%s" % new_company.company_id)


@app.route('/company_login', methods=['GET'])
def company_login():
    """Company login page"""

    return render_template("company_login_form.html")

@app.route("/company_profile/<int:company_id>")
def company_profile(company_id):
    """Show info about company."""

    company = Company.query.get(company_id)

    return render_template("company_profile.html", company=company)


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
    return redirect("/user/%s" % new_user.user_id)


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
    return redirect("/user/%s" % user.user_id)


@app.route("/user/<int:user_id>")
def user_detail(user_id):
    """Show info about user."""

    user = User.query.get(user_id)
    return render_template("user.html", user=user)

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

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()