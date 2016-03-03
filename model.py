"""Models and database functions for Reggie."""
import heapq
import time
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy import text


db = SQLAlchemy()

##############################################################################
# Model definitions

class Company(db.Model):
    """Company account in Reggie"""

    __tablename__ = "companies"

    company_id = db.Column(UUID, server_default=text("uuid_generate_v4()"), primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    company_email = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(50))
    company_phone = db.Column(db.String(30))
    company_address = db.Column(db.String(200))
    company_city = db.Column(db.String(100))
    company_state = db.Column(db.String(200))
    company_zip = db.Column(db.String(200))
    password = db.Column(db.String(100))
    
    def __repr__(self):
        """Provides helpful representation when printed"""

        return "<Company company_id=%s, company_name=%s, company_email%s>" % (self.company_id, self.company_name, self.company_email)

class Event(db.Model):
    """Create an Event in reggie"""

    __tablename__ = "events"

    event_id = db.Column(UUID, server_default=text("uuid_generate_v4()"), primary_key=True)
    company_id = db.Column(UUID, db.ForeignKey('companies.company_id'))
    event_name = db.Column(db.String(100), nullable=False)
    venue = db.Column(db.String(100))
    address = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state  = db.Column(db.String(100))
    zipcode  = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    description = db.Column(db.String(1000))
    price =db.Column(db.Integer, nullable=True)
    color =db.Column(db.String(100))
    logo =db.Column(db.String(100))
    status = db.Column(db.String(30))

    company = db.relationship("Company",
                           backref=db.backref("events", order_by=event_id))

    def __repr__(self):
        """Provides helpful representation when printed"""

        return "<Event event_id=%s, event_name=%s, company_id%s>" % (self.event_id, self.event_name, self.company_id)

class Question(db.Model):
    """Questions within a form"""

    __tablename__ = "questions"

    id =db.Column(UUID, server_default=text("uuid_generate_v4()"), primary_key=True)
    event_id =db.Column(UUID, db.ForeignKey('events.event_id'))
    label =db.Column(db.String(100), nullable=False)
    selector =db.Column(db.String(100), nullable=False)
    ordinal=db.Column(db.Integer, nullable=False)
    data=db.Column(JSON)

    form = db.relationship("Event",
                           backref=db.backref("questions", order_by=ordinal))

    def __repr__(self):
        """Provides helpful representation when printed"""

        return "<Question id=%s, event_id=%s, label=%s, selector=%s, ordinal=%s>" % (self.id, self.event_id, self.label, self.selector, self.ordinal)

class Answer(db.Model):
    """User Answers with a form"""

    __tablename__ = "answers"

    id =db.Column(UUID, server_default=text("uuid_generate_v4()"), primary_key=True)
    question_id =db.Column(UUID, db.ForeignKey('questions.id'), nullable=False)
    registration_id =db.Column(UUID, db.ForeignKey('registrations.id'), nullable=False)
    value =db.Column(db.String(100))

    registration = db.relationship("Registration",
                           backref=db.backref("answers"))

    question = db.relationship("Question",
                           backref=db.backref("answers"))

    def __repr__(self):
        """Provides helpful representation when printed"""

        return "<Answer id=%s, registration_id=%s, question_id=%s, value=%s>" % (self.id, self.registration_id, self.question_id, self.value)

class Registration(db.Model):
    """Registration to event"""

    __tablename__="registrations"

    id=db.Column(UUID, server_default=text("uuid_generate_v4()"), primary_key=True)
    user_id=db.Column(UUID, db.ForeignKey('users.user_id'))
    event_id=db.Column(UUID, db.ForeignKey('events.event_id'))
    timestamp=db.Column(db.DateTime, nullable=False)


    user=db.relationship("User",
                           backref=db.backref("registrations"))

    event=db.relationship("Event",
                           backref=db.backref("registrations"))


    def __repr__(self):
        """Provides helpful representation when printed"""

        return "<Registration id=%s, user_id=%s, event_id=%s, timestamp=%s>" % (self.id, self.user_id, self.event_id, self.timestamp)

class User(db.Model):
    """User account in Reggie"""

    __tablename__ = "users"

    user_id = db.Column(UUID, server_default=text("uuid_generate_v4()"), primary_key=True)
    user_firstname = db.Column(db.String(100), nullable=False)
    user_lastname = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    user_phone = db.Column(db.String(30))
    password = db.Column(db.String(100))

    def __repr__(self):
        """Provides helpful representation when printed"""

        return "<User user_id=%s, user_name=%s, user_email%s>" % (self.user_id, self.user_name, self.user_email)



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///reggiedb'
    #app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."



