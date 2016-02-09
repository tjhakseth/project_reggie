"""Models and database functions for Reggie."""

import time
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

##############################################################################
# Model definitions

class Company(db.Model):
    """Company account in Reggie"""

    __tablename__ = "companies"

    company_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    company_email = db.Column(db.String(100), nullable=False)
    company_phone = db.Column(db.String(30))
    company_address = db.Column(db.Sting(200))
    contact_person = db.Column(db.String(50))

    def __repr__(self):
        """Provides helpful representation when printed"""

        return "<Company company_id=%s, company_name=%s, company_email%s>" % 
                (self.company_id, self.company_name, self.company_email)



class User(db.Model):
    """User account in Reggie"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    user_phone = db.Column(db.String(30))
    user_address = db.Column(db.Sting(200))

    def __repr__(self):
        """Provides helpful representation when printed"""

        return "<User user_id=%s, user_name=%s, user_email%s>" % 
                (self.user_id, self.user_name, self.user_email)



class Event(db.Model):
    """Event in Reggie"""

    __tablename__ = "events"

    event_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'))
    event_name = user_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(30))

    company = db.relationship("Company",
                           backref=db.backref("events", order_by=event_id))


    def __repr__(self):
        """Provides helpful representation when printed"""

        return "<Event event_id=%s, event_name=%s, company_id%s>" % 
                (self.event_id, self.event_name, self.company_id)


class User_event(db.Model):
    """User events in Reggie"""

    __tablename__ = "events"

    user_event_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'))
    user_id = user_name = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    event = db.relationship("Events",
                           backref=db.backref("user_events", order_by=user_event_id))

    user = db.relationship("Users",
                           backref=db.backref("user_events", order_by=user_event_id))



    def __repr__(self):
        """Provides helpful representation when printed"""

        return "<User_event user_event_id=%s>" % 
                (self.user_event_id)




