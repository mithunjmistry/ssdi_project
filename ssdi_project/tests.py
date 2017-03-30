import unittest
#from django.http import HttpResponse
#from django.test.client import RequestFactory
from django.test import Client
from django.contrib.auth.models import User


class MyTestCase(unittest.TestCase):
    def test_get_boolean(self):
        from views import get_boolean
        self.assertEqual(get_boolean("yes"), True)


    def test_FactoryUserStatus(self):  # Running
        from views import FactoryUserStatus
        self.assertEquals("receptionist", FactoryUserStatus("rachel"))

    def test_check_login_page_getusername(self):
        from views import login_page
        from django.http import HttpRequest
        get_req= HttpRequest()
        get_req.user=User()
        get_req.user.username="rachel"
        get_req.user.password="123456780"
        self.assertTrue(login_page(get_req))

    '''
    def test_check_login_page_POST(self):
        from views import login_page
        from django.http import HttpRequest
        get_req= HttpRequest()
        #get_req.user=User()
        #get_req.user.username="rachel"
        #get_req.user.password="1234567890"
        self.user = User.objects.create_user(
            username='rachel', email='mithunjmistry@gmail.com', password='1234567890')
        get_req.POST.appendlist("username","rachel")
        get_req.POST.appendlist("password", "1234567890")
        get_req.session()
        response = login_page(get_req)
        self.assertTrue(login_page(get_req))




    def test_login_successful(self):
        v = views()
        request = RequestFactory()
        post_request = request.post('/submit/', {'foo': 'bar'})
        self.assertEquals("{}.html.format(loggeduserstatus), {message: How you doing today: {}.format(loggedusername)",
                          v.login_successful(request, "receptionist", "rachel"))
                          '''

if __name__ == '__main__':
    unittest.main()
