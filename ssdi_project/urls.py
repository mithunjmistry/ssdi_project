"""ssdi_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from views import *
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', TemplateView.as_view(template_name="home.html")),
    url(r'^register/', signup_page, name="signup"),
    url(r'^login/', login_page, name="login"),
    url(r'^logout/', logout_user, name="logout"),
    url(r'^doctors/', show_doctors, name="ShowDoctors"),
    url(r'^success/(\w+)/(\w+)', login_successful, name="success"),
    url(r'^timings/(\w+)/', set_office_hours, name="OfficeHours"),
    url(r'^beds/(\w+)/', check_beds, name="CheckBeds"),
    url(r'^doctoradd/(\w+)/', doctor_add, name="doctoradd"),
    url(r'^Admit/(\w+)/',Admit_Patient,name="admitpatient"),
    url(r'^about/', TemplateView.as_view(template_name="about.html")),
    url(r'^testdb/', test_database, name="testdb"),
    url(r'^backenddb/', backend_adder, name="BackEndAdder"),
]

