import unittest
#from django.http import HttpResponse
#from django.test.client import RequestFactory
from django.test import Client
from django.contrib.auth.models import User
from pip._vendor.requests import session


class MyTestCase(unittest.TestCase):
    def test_FactoryUserStatus(self):  # Running
        from views import FactoryUserStatus
        self.assertEquals("receptionist", FactoryUserStatus("rachel"))

    def test_get_boolean(self):
        from views import get_boolean
        self.assertEqual(get_boolean("yes"), True)


    def test_sign_up_success(self):
        from views import signup_page
        from django.test import Client
        c = Client()
        response = c.post('/register/',{'username':'Monika','password':'123456','confirm_password':'123456','fname':'testName',
                     'lname':'testLastName','gender':'Female','dob':'testDate','insurance':'yes',
                     'mobileno':'testmobno','address':'testAddress','zipcode':'dfgdgd','state':'testState'})

        #print response.status_code
        self.assertIsNotNone(response.content)

    def test_sign_up_fail(self):
        from views import signup_page
        from django.test import Client
        c = Client()
        response = c.post('/register/', {'username': 'rachel', 'password': '123456', 'confirm_password': '123456',
                                         'fname': 'testName',
                                         'lname': 'testLastName', 'gender': 'Female', 'dob': 'testDate',
                                         'insurance': 'yes',
                                         'mobileno': 'testmobno', 'address': 'testAddress', 'zipcode': 'dfgdgd',
                                         'state': 'testState'})


        #self.assertIsNotNone(response.url)
        #self.assertTemplateUsed(response,'register.html')
        #self.assertContains(response, 'This username is already being taken!')

    def test_getDoctors(self):
        from views import show_doctors
        from django.http import HttpRequest
        get_req = HttpRequest()
        names = show_doctors(get_req)
        self.assertIsNotNone(names)
        #print names.content

    def test_checkBeds(self):
        from django.http import HttpRequest
        from views import check_beds
        get_req = HttpRequest()
        get_req.user=User()
        get_req.user.username="rachel"
        get_req.user.password="1234567890"
        from django.test import Client
        c = Client()
        response= c.post('/check_beds/')
        self.assertIsNotNone(check_beds(get_req,'rachel'))

    def test_login_sucessfull(self):
        from views import login_successful
        from django.http import HttpRequest
        get_req = HttpRequest()
        get_req.user=User()
        self.assertTrue(login_successful(get_req,"receptionist","rachel"))



    def test_check_login_page_POST(self):
        from django.http import HttpRequest
        from views import login_page
        get_req = HttpRequest()
        self.user = User.objects.create_user(
            username='pheebs', email='mithunjmistry@gmail.com', password='1234567890')
        get_req.user = self.user
        response = login_page(get_req)
        #print response.status_code
        self.assertTrue(login_page(get_req))



    '''
    def test_login_successful(self):
        v = views()
        request = RequestFactory()
        post_request = request.post('/submit/', {'foo': 'bar'})
        self.assertEquals("{}.html.format(loggeduserstatus), {message: How you doing today: {}.format(loggedusername)",
                          v.login_successful(request, "receptionist", "rachel"))
                          '''
    ''' def test_check_login_page_getusername(self):
            from views import login_page
            from django.http import HttpRequest
            get_req= HttpRequest()
            get_req.user=User()
            get_req.user.username="Monika"
            get_req.user.password="123456"
            from django.test import Client
            c = Client()
            #response=c.login(self)
            response = c.login(username='Monika',password='123456')
            self.assertTrue(login_page(get_req))'''

if __name__ == '__main__':
    unittest.main()
