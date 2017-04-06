from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from ssdi_project.models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import random
from django.core.mail import send_mail

def Admit_Patient():
    patient_name = 'Shalaka'
    if (Patient.objects(username=patient_name)):
        Beds.objects(room_type='AC Deluxe',location='NC',room_number=1,bed_number=2,patient_name=patient_name)
        Patient.objects(username=patient_name).update(set__currently_admitted=True)
        return HttpResponse('Patient admitted successfully')
    else:
        return HttpResponse('Patient non existent')

def get_boolean(value):
    if value.lower() == "yes":
        return True
    elif value.lower() == "no":
        return False
    else:
        raise Exception

def FactoryUserStatus(loggeduser):
    t = TypeOfUser.objects(username=loggeduser).first()
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
                user = User.objects.create_user(username=username, email=uemail, password=upass)
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
    if request.user.get_username():
        return redirect(login_successful, FactoryUserStatus(request.user.get_username()), request.user.get_username())
    if request.POST:
        username = request.POST.get("username")
        upass = request.POST.get("password")
        user = authenticate(username=username, password=upass)
        if user is not None:
            login(request, user)
            UserType = FactoryUserStatus(username)
            return redirect(login_successful, UserType, username)
        else:
            return render(request, "login.html", {'error': "Email or password incorrect!"})
    return render(request, "login.html", {'error': None})

@login_required
@never_cache
def login_successful(request, loggeduserstatus, loggedusername):
    return render(request, "{}.html".format(loggeduserstatus), {"message": "How you doing today: {}".format(loggedusername)})

def logout_user(request):
    logout(request)
    return redirect(login_page)

@login_required
@never_cache
def check_beds(request, username):
    if FactoryUserStatus(username) == "receptionist":
        t = Receptionist.objects(username=username).only('state').first()
        b = Beds.objects(location=t.state).exclude('location')
        d = {}
        for i in b:
            d[i.room_type] = i.availability
        return render(request, "checkbeds.html", {"d": d})
    else:
        return redirect(login_page)

@login_required
@never_cache
def delete_user(request, username):
    try:
        u = User.objects.get(username = username)
        u.delete()
        logout(request)
        return render(request, "user_deleted.html")
    except:
        return HttpResponse("Oops! Something went wrong!")

@login_required
@never_cache
def set_office_hours(request, username):
    if FactoryUserStatus(username) == "doctor":
        return "Hi"
    else:
        return redirect(login_page)

@login_required
@never_cache
def doctor_add(request, username):
    if FactoryUserStatus(username) == "receptionist":
        if request.POST:
            uemail = str(request.POST.get("email")).strip()
            uemail_confirm = str(request.POST.get("email_confirm")).strip()
            username = str(request.POST.get("username")).strip()
            upass = random.randint(11111111, 999999999)
            first_name = str(request.POST.get("fname")).strip()
            last_name = str(request.POST.get("lname")).strip()
            gender = str(request.POST.get("gender")).strip()
            dob = str(request.POST.get("dob")).strip()
            phone = str(request.POST.get("mobileno")).strip()
            address = str(request.POST.get("address")).strip()
            zipcode = str(request.POST.get("zipcode")).strip()
            state = str(request.POST.get("state"))
            speciality = str(request.POST.get("speciality"))
            status = str(request.POST.get("status"))
            if uemail == uemail_confirm:
                try:
                    user = User.objects.create_user(username=username, email=uemail, password=upass)
                    user.save()
                    td = Doctor.objects.create(username=username, email=uemail, first_name=first_name, last_name=last_name, gender=gender, dob=dob,
                                                phone_number=phone, address=address, zipcode=zipcode, state=state, speciality=speciality, status=status)
                    td.save()
                    tr = TypeOfUser.objects.create(username=username, user_status="doctor")
                    tr.save()
                    message = "Hello Doctor,\nYou are registered in our group of hospitals successfully. Your username is {} and password is {}. Please change your password after logging in.\nHave a great day.".format(username, upass)
                    send_mail(subject=("Registration Status"),message=str(message),from_email="ssdigroupproject@gmail.com", recipient_list=[uemail])
                    return render(request, "user_created.html")
                except:
                    return render(request, "doctoradd.html", {'error': "This username is already being taken!"})
            else:
                return render(request, "doctoradd.html", {'error': "You didn't confirmed email address properly!"})
        return render(request, "doctoradd.html", {"error": None})
    else:
        return redirect(login_page)

def show_doctors(request):
    full_name = []
    speciality = []
    state = []

    for doctor in Doctor.objects:
        full_name.append(str(doctor.first_name + " " + doctor.last_name))
        speciality.append(str(doctor.speciality))
        state.append(str(doctor.state))

    content = zip(full_name, speciality, state)
    return render(request, "ShowDoctors.html",
                  {"full_name": full_name, "speciality": speciality, "state": state, "content": content})

def test_database(request):
    '''
    user = User.objects.create_user(username="Shalaka", email="shalaka@gmail.com", password="1234567890")
    user.save()


    tr = TypeOfUser.objects.create(username="Shalaka", user_status="patient")
    tr.save()

    td = Patient.objects.create(username='Shalaka',email="shalaka@gmail.com", first_name="Shalaka", last_name="Thombare", gender="Female",
                                dob="20-10-1991",
                                insured=True, phone_number="9803202869", address="abhilasha", zipcode="28262",
                                state="NC")
    td.save()

    tr = TypeOfUser.objects.create(username="mithun", user_status="patient")
    tr.save()

    user = User.objects.create_user(username="rachel", email="mithunjmistry@gmail.com", password="1234567890")
    user.save()
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

    tr = TypeOfUser.objects.create(username="mithun", user_status="patient")
    tr.save()

    return HttpResponse("This database is nice.")


    tr = Beds.objects.create(room_type="General", location="NC", availability=10)
    tr.save()
    tr1 = Beds.objects.create(room_type="ICU", location="NC", availability=5)
    tr1.save()
    tr2 = Beds.objects.create(room_type="Emergency", location="NC", availability=2)
    tr2.save()
    tr3 = Beds.objects.create(room_type="AC Deluxe", location="NC", availability=4)
    tr3.save()

    user = User.objects.create_user(username="rachel", email="mithunjmistry@gmail.com", password="1234567890")
    user.save()
    td = Receptionist.objects.create(username="rachel", email="mithunjmistry@gmail.com", first_name="Rachel", last_name="Green", gender="Female", dob="04-12-1995",
                                                phone_number="5086152876", address="434 Barton Creek Dr", zipcode="28262", state="NC")
    td.save()

    tr = TypeOfUser.objects.create(username="rachel", user_status="receptionist")
    tr.save()

    user = User.objects.create_user(username="pheebs", email="mithunjmistry@gmail.com", password="1234567890")
    user.save()
    td = Doctor.objects.create(username="pheebs", email="mithunjmistry@gmail.com", first_name="Phoebe", last_name="Buffay", gender="Female", dob="04-12-1995",
                                                phone_number="5086152876", address="434 Barton Creek Dr", zipcode="28262", state="NC", speciality="cardiac", status="permanent", consulting_fees=50.0,
                               office_hours=[Timings(day="Monday", time="9 to 5")])
    td.save()

    tr = TypeOfUser.objects.create(username="pheebs", user_status="doctor")
    tr.save()
    
    full_name = []
    speciality = []
    state = []

    for doctor in Doctor.objects:
        full_name.append(str(doctor.first_name + " " + doctor.last_name))
        speciality.append(str(doctor.speciality))
        state.append(str(doctor.state))

    content = zip(full_name,speciality,state)
    return render(request, "ShowDoctors.html", {"full_name": full_name, "speciality": speciality, "state": state, "content": content})
    '''
    return HttpResponse('This is nice')


def backend_adder(request):

    patient_name = 'Shalaka'
    if (Patient.objects(username=patient_name)):
        Beds.objects(room_type='AC Deluxe').update_one(push__patient_name='Shalaka', location='NC',
                     room_number=3, bed_number=3)
        #Patient.objects(username=patient_name).update(set__currently_admitted=True)
        return HttpResponse('Patient admitted successfully')
    else:
        return HttpResponse('Patient non existent')
    return HttpResponse("Added by backend.")
    '''
    b = Beds.objects()
    for bed in b:
        print bed.patient_name
        '''
