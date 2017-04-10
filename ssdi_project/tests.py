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

    # Test that ShowDoctors does not return None
    def test_show_doctors(self):
        from django.http import HttpRequest
        from views import show_doctors
        testrequest = HttpRequest()
        self.assertIsNotNone(show_doctors(testrequest))

    # View appointments for Doctors
    def test_view_appointments_doctors(self):
        from django.http import HttpRequest
        from views import view_appointments_doctors
        testrequest = HttpRequest()
        testuser = User()
        testuser.username='dcole0'
        testuser.password='1234567890'
        testuser.is_active = True
        testrequest.user = testuser
        self.assertIsNotNone(view_appointments_doctors(testrequest,testrequest.user.username))

    # View appointments for Patients
    def test_view_appointments_patients(self):
        from django.http import HttpRequest
        from views import view_appointments_patients
        testrequest = HttpRequest()
        testuser = User()
        testuser.username = 'sscott0'
        testuser.password = '1234567890'
        testuser.is_active = True
        testrequest.user = testuser
        self.assertIsNotNone(view_appointments_patients(testrequest, testrequest.user.username))


    # View Time for patients
    def test_view_time(self):
        from django.http import HttpRequest
        from views import view_time
        testrequest = HttpRequest()
        testuser = User()
        testuser.username = 'dcole0'
        testuser.password = '1234567890'
        testuser.is_active = True
        testrequest.user = testuser
        self.assertIsNotNone(view_time(testrequest, testrequest.user.username))

    # Test Admit Patient
    def test_admit_patient(self):
        import requests
        from views import admit_patient
        import json
        headers = {'content-type': 'application/json'}
        url = 'http://127.0.0.1:8000/admit/aferguson0/'
        data = {"data": {"patientID": None}}
        params = {'sessionKey': '9ebbd0b25760557393a43064a92bae539d962103', 'format': 'xml', 'platformId': 1}
        self.assertIsNotNone(requests.post(url, params={}, data=json.dumps(data), headers=None))


    # Test Add Doctors
    def test_doctor_add(self):
        from views import  doctor_add
        import requests
        import json
        url = 'http://127.0.0.1:8000/doctoradd/aferguson0/'
        data = {"data": {"patientID": None}}
        params = {'sessionKey': '9ebbd0b25760557393a43064a92bae539d962103', 'format': 'xml', 'platformId': 1}
        self.assertIsNotNone(requests.post(url, params={}, data=json.dumps(data), headers=None))

if __name__ == '__main__':
    unittest.main()
