import mongoengine
from django.http import HttpResponse
from django.shortcuts import render
from mongoengine.django.auth import *
from django.contrib.auth import authenticate
from ssdi_project.models import *

def signup_page(request):
    if request.POST:
        uname = request.POST.get("username")
        upass = request.POST.get("password")
        upass_confirm = request.POST.get("password_confirm")
        uemail = request.POST.get("email")
        if upass == upass_confirm:
            user = User.create_user(username=uname.strip(), email=uemail.strip(), password=upass)
            user.save()
            return HttpResponse("User Created successfully")
        else:
            return HttpResponse("You didn't confirmed your password correctly.")
    return render(request, "signup.html")


def login_page(request):
    if request.POST:
        uname = request.POST.get("username")
        upass = request.POST.get("password")
        user = authenticate(username=uname, password=upass)
        if user is not None:
            return HttpResponse("Welcome " + uname)
        else:
            return HttpResponse("Try again. Please check your username and password again!")
    return render(request, "index.html")

def test_database(request):
    '''
    t = Doctor.objects.create(id=0, first_name="Mithun", last_name="Mistry", email="mithunjmistry@gmail.com",
                              speciality="heart",
                              status="permanent", consulting_fees=50,
                              office_hours=([Timings(day="Monday", time="9 to 5")]))
    t.save()
    '''
    t = Doctor.objects(first_name="Mithun").first()
    t.office_hours.append(Timings(day="Tuesday", time="8 to 5"))
    t.save()
    return render(request, "index.html")