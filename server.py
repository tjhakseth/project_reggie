from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

# add the classes after db once established
# from model import connect_to_db, db


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

@app.route('/company_login')
def company_login():
    """Company login page"""

    return render_template("company_login_form.html")

@app.route('/user_login')
def user_login():
    """user login page"""

    return render_template("user_login_form.html")

@app.route('/one_page')
def one_page_registration():
    """One page registration"""

    return render_template("sample_form.html")

# @app.route('/login', methods=['POST'])
# def login_process():
#     """Process login."""

#     # Get form variables
#     email = request.form["email"]
#     password = request.form["password"]

#     user = User.query.filter_by(email=email).first()

#     if not user:
#         flash("No such user")
#         return redirect("/login")

#     if user.password != password:
#         flash("Incorrect password")
#         return redirect("/login")

#     session["user_id"] = user.user_id

#     flash("Logged in")
#     return redirect("/users/%s" % user.user_id)





if __name__ == "__main__":
    
    app.debug = True

    # connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()