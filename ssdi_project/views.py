import mongoengine
from django.http import HttpResponse
from django.shortcuts import render, redirect
from mongoengine.django.auth import *
from django.contrib.auth import authenticate, login, logout
from ssdi_project.models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

def get_boolean(value):
    if value.lower() == "yes":
        return True
    elif value.lower() == "no":
        return False
    else:
        raise Exception

def FactoryUserStatus(loggeduser):
    t = TypeOfUser.objects(username=loggeduser).first()
    t.user_status
    print t.user_status
    return str(t.user_status)

def signup_page(request):
    if request.POST:
        uemail = str(request.POST.get("email")).strip()
        username = str(request.POST.get("username")).strip()
        upass = request.POST.get("password")
        upass_confirm = request.POST.get("confirm_password")
        first_name = str(request.POST.get("fname")).strip()
        last_name = str(request.POST.get("lname")).strip()
        gender = str(request.POST.get("gender")).strip()
        dob = str(request.POST.get("dob")).strip()
        insurance = request.POST.get("insurance")
        phone = str(request.POST.get("mobileno")).strip()
        address = str(request.POST.get("address")).strip()
        zipcode = str(request.POST.get("zipcode")).strip()
        state = str(request.POST.get("state"))
        if upass == upass_confirm:
            try:
                user = User.create_user(username=username, email=uemail, password=upass)
                user.save()
                insured = get_boolean(insurance)
                td = Patient.objects.create(username=username, email=uemail, first_name=first_name, last_name=last_name, gender=gender, dob=dob,
                                            insured=insured, phone_number=phone, address=address, zipcode=zipcode, state=state)
                td.save()
                tr = TypeOfUser.objects.create(username=username, user_status="patient")
                tr.save()
                return render(request, "user_created.html")
            except:
                return render(request, "register.html", {'error': "This username is already being taken!"})
        else:
            return render(request, "register.html", {'error': "You didn't confirmed your password correctly!"})
    return render(request, "register.html", {'error': None})

def login_page(request):
    if request.POST:
        username = request.POST.get("username")
        upass = request.POST.get("password")
        user = authenticate(username=username, password=upass)
        if user is not None:
            login(request, user)
            UserType = FactoryUserStatus(username)
            return redirect(login_successful, loggeduserstatus=UserType, loggedusername=username)
        else:
            return render(request, "login.html", {'error': "Email or password incorrect!"})
    return render(request, "login.html", {'error': None})

@login_required
@never_cache
def login_successful(request, loggeduserstatus, loggedusername):
    return render(request, "{}.html".format(loggeduserstatus), {"message": "How you doing today: {}".format(loggedusername), "user": loggedusername})

@login_required
def logout_user(request):
    logout(request)
    redirect(login_page)

def test_database(request):
    '''
    t = Doctor.objects.create(id=1, first_name="Shalaka", last_name="Thombre", email="shalaka@gmail.com",
                              speciality="heart",
                              status="permanent", consulting_fees=50,
                              office_hours=([Timings(day="Monday", time="9 to 5")]))
    t.save()


    t = Doctor.objects(first_name="Shalaka").first()
    t.office_hours.append(Timings(day="Tuesday", time="8 to 5"))
    t.save()

    t = Test.objects.create(id=0, email="mithunjmistry@gmail.com")
    t.save()

    td = Patient.objects.create(email="mithunjmistry@gmail.com", first_name="Mithun", last_name="Mistry", gender="Male", dob="04-12-1995",
                                            insured=True, phone_number="9033914035", address="abhilasha", zipcode="396195", state="Gujarat")
    td.save()
    '''
    tr = TypeOfUser.objects.create(username="mithun", user_status="patient")
    tr.save()
    return HttpResponse("This database is nice.")
