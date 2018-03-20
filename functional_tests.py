import unittest

from flask_testing import LiveServerTestCase
from selenium import webdriver

from app import create_app, db
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'


class NewVisitorTest(LiveServerTestCase):

    
    def create_app(self):
        return create_app(TestConfig)
    '''
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        db.create_all()
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()
        db.session.remove()
        db.drop_all()
        '''
    def setUp(self):
        self.app = self.create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.browser = webdriver.Firefox()
        
    def tearDown(self):
        self.browser.quit()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def fill_form(self, **kwargs):
        for key, value in kwargs.items():
            self.browser.find_element_by_id(key).send_keys(value)

    def test_login_unregistered_new_user(self):
        # She goes to the new cool microblog page
        self.browser.get('http://localhost:5000/')

        # She notices the page title and header mention Microblog
        self.assertIn('Microblog', self.browser.title)

        #She sees login form
        header_text = self.browser.find_element_by_tag_name('h1').text
        form = self.browser.find_element_by_tag_name('form')
        
        self.assertEqual('Sign In', header_text)
        self.assertIsNotNone(form)

        # She clicks on Home button and sees
        # message Please log in to access this page
        home_link = self.browser.find_element_by_xpath(
            '//nav/div/div[2]/ul/li/a')
        home_link.click()
        alert_text = self.browser.find_element_by_class_name(
            'alert').text
        
        self.assertIn('Please log in', alert_text)
        
        # She clicks on button sign in and message 
        # Please fill out this field pops up
        self.browser.find_element_by_id('submit').click()    
        username_input = self.browser.find_element_by_id('username')
        validation_message = username_input.get_attribute(
            'validationMessage')
        
        self.assertIn('Please fill out', validation_message)   
            
        # She tries to sign in and message 
        # Invalid username or password appears
        self.fill_form(username='ABC', password='DFG')        
        self.browser.find_element_by_id('submit').click()
        alert_text = self.browser.find_element_by_class_name(
            'alert').text
            
        self.assertEqual('Invalid username or password', alert_text)
        
    def test_register_and_login_new_user(self):
        # She clicks on Click to Register button and 
        # register form appears
        self.browser.get('http://localhost:5000/')
        register_link = self.browser.find_element_by_link_text(
            'Click to Register')
        register_link.click()
        
        self.assertIn('Register', self.browser.title)
        
        # She fills out register form and click submit, 
        # the login form appear        
        self.fill_form(
            username='Eve', 
            email='eve@expl.com',
            password='pass',
            password2='pass')
        self.browser.find_element_by_id('submit').click()        
        alert_text = self.browser.find_element_by_class_name(
            'alert').text
        
        self.assertIn('Sign', self.browser.title)
        self.assertIn('registered user', alert_text)
        
        #She fills out login form and successfuly logs in
        self.fill_form(username='Eve', password='pass')
        self.browser.find_element_by_id('submit').click()
        
        self.assertIn('Home', self.browser.title)

if __name__ == '__main__':
    unittest.main(verbosity=2)


