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
        else:
            return HttpResponse("You didn't confirmed your password correctly.")
    return render(request, "index.html")


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
    test = Test.objects.create(id=0, First_Name="Mithun", Last_Name="Mistry", Age=18)
    test.save()
    return render(request, "index.html")