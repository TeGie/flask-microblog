import unittest

from selenium import webdriver


class NewVisitorTest(unittest.TestCase):
    
    def setUp(self):
        self.browser = webdriver.Firefox()
        
    def tearDown(self):
        self.browser.quit()

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
        submit_button = self.browser.find_element_by_id('submit')
        submit_button.click()      
        username_input = self.browser.find_element_by_id('username')
        validation_message = username_input.get_attribute(
            'validationMessage')
        
        self.assertIn('Please fill out', validation_message)   
            
        # She tries to sign in and message 
        # Invalid username or password appears
        username_input = self.browser.find_element_by_id('username')
        password_input = self.browser.find_element_by_id('password')
        submit_button = self.browser.find_element_by_id('submit')
        username_input.send_keys('ABC')
        password_input.send_keys('DFG')
        submit_button.click()
        alert_text = self.browser.find_element_by_class_name(
            'alert').text
            
        self.assertEqual('Invalid username or password', alert_text)

        #She clicks on Click to Register button and 
        # register form appears
        register_link = self.browser.find_element_by_link_text(
            'Click to Register')
        register_link.click()
        
        self.assertIn('Register', self.browser.title)
        
    def register_new_user(self):
        pass


if __name__ == '__main__':
    unittest.main(warnings='ignore', verbosity=2)
