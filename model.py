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
    number_of_fields = db.Column(db.Integer, nullable=False)
    payment_page =db.Column(db.Boolean, nullable=True)
    color =db.Column(db.String(100))
    logo =db.Column(db.String(100))
    location = db.Column(db.String(100))
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
    user_id =db.Column(UUID, db.ForeignKey('users.user_id'))
    event_id =db.Column(UUID, db.ForeignKey('events.event_id'))
    question_id =db.Column(UUID, db.ForeignKey('questions.id'))
    value =db.Column(db.String(100))

    user = db.relationship("User",
                           backref=db.backref("answers"))

    event = db.relationship("Event",
                           backref=db.backref("answers"))

    question = db.relationship("Question",
                           backref=db.backref("answers"))

    def __repr__(self):
        """Provides helpful representation when printed"""

        return "<Answer id=%s, user_id=%s, question_id=%s, value=%s>" % (self.id, self.user_id, self.question_id, self.value)


class User(db.Model):
    """User account in Reggie"""

    __tablename__ = "users"

    user_id = db.Column(UUID, server_default=text("uuid_generate_v4()"), primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    user_phone = db.Column(db.String(30))
    user_address = db.Column(db.String(200))
    password = db.Column(db.String(100))

    def __repr__(self):
        """Provides helpful representation when printed"""

        return "<User user_id=%s, user_name=%s, user_email%s>" % (self.user_id, self.user_name, self.user_email)




# class UserEvent(db.Model):
#     """User events in Reggie"""

#     __tablename__ = "user_events"

#     user_event_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))
#     user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

#     event = db.relationship("Event",
#                            backref=db.backref("user_events", order_by=user_event_id))

#     user = db.relationship("User",
#                            backref=db.backref("user_events", order_by=user_event_id))



#     def __repr__(self):
#         """Provides helpful representation when printed"""

#         return "<User_event user_event_id=%s>" % (self.user_event_id)


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



