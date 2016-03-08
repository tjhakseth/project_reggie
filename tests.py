"""Testing Doc"""

import unittest
import server
from model import connect_to_db, db, Company, User, Event, Question, Answer, Registration
from server import app


class FlaskTests(unittest.TestCase):
    """Tests for Reggie app"""

    TEST_DATABASE_URI = 'postgresql://localhost/fakereggiedb'
    TESTING = True

    def setUp(self):
        """Set up a fake browser"""
        # Get the Flask test client
        self.client = app.test_client()

        app.config['TESTING'] = self.TESTING
        app.config['DEBUG'] = False
        connect_to_db(app, self.TEST_DATABASE_URI)

        # Create secret key to access session
        app.secret_key = "Reggieevents"

        # Connect to fake database
        db.create_all()

    def tearDown(self):
        """Close DB session and drop all tables"""
        db.session.remove()
        db.drop_all()

    ################################################################
    # Route tests

    def test_homepage(self):
        """Does the homepage load correctly?"""

        result = self.client.get('/')
        self.assertEqual(result.status_code, 200)
        self.assertIn('text/html', result.headers['Content-Type'])
        self.assertIn('Reggie', result.data)

    def test_create_company(self):
        """Does the signup form load correctly?"""

        result = self.client.get('/create_company')
        self.assertIn("Create Company Account", result.data)

    # def create_company(self, company_name, company_email, contact_person, company_phone, company_address, company_city, company_state, company_zip, password):

    #     return self.client.post('/create_company', data={
    #                         'company_name': company_name,
    #                         'company_email': company_email,
    #                         'contact_person': contact_person,
    #                         'company_phone': company_phone,
    #                         'company_address': company_address,
    #                         'company_city': company_city,
    #                         'company_state': company_state,
    #                         'company_zip': company_zip,
    #                         'password': password}, follow_redirects=True)

    # def test_company_confirm(self):
    #     """Company can sign up for a new account?"""

    #     result = self.create_company('coolbeans', 'boringbeanies@cool.com', 'Sam Beans', '5551234567', '500 Fake St.', 'Palo Alto', 'CA', '94200', 'password')

    #     self.assertIn("You successfully created an account", result.data)
    #     Company.query.filter_by(email='boringbeanies@cool.com').delete()
    #     db.session.commit()

    # def company_login(self, email, password):
    #     return self.client.post('/login-confirm', data={'email': email, 'password': password})

    # def test_company_login(self):
    #     """Does login/logout work?"""

    #     result = self.company_login('test@testing.com', 'jinja2')
    #     self.assertIn('"confirmed_user": true', result.data)

    # def test_wrong_company_login(self):
    #     """Does password check work?"""

    #     result = self.company_login('test@testing.com', '80dqhj')
    #     self.assertIn('"confirmed_user": false', result.data)

    # def individual_login(self, email, password):
    #     return self.client.post('/login-confirm', data={'email': email, 'password': password})

    # def test_individual_login(self):
    #     """Does login/logout work?"""

    #     result = self.individual_login('test@testing.com', 'jinja2')
    #     self.assertIn('"confirmed_user": true', result.data)

    # def test_wrong_individual_login(self):
    #     """Does password check work?"""

    #     result = self.individual_login('test@testing.com', '80dqhj')
    #     self.assertIn('"confirmed_user": false', result.data)

    # def display_edit_profile(self, userid):
    #     return self.client.get("/editprofile/%d" % userid)

    # def test_display_edit_profle(self):
    #     """Can the edit profile page be successfully displayed?"""

    #     self.login('test@testing.com', 'jinja2')
    #     result = self.display_edit_profile(14)
    #     self.assertIn('test@testing.com', result.data)




################################################################################


if __name__ == "__main__":
    unittest.main(verbosity=2)
