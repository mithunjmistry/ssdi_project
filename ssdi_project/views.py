from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from ssdi_project.models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import random
from django.core.mail import send_mail
from datetime import datetime, timedelta
from collections import OrderedDict, deque
import calendar


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
                td = Patient.objects.create(username=username, email=uemail, first_name=first_name, last_name=last_name,
                                            gender=gender, dob=dob,
                                            insured=insured, phone_number=phone, address=address, zipcode=zipcode,
                                            state=state)
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
            request.session.set_expiry(300)
            login(request, user)
            UserType = FactoryUserStatus(username)
            return redirect(login_successful, UserType, username)
        else:
            return render(request, "login.html", {'error': "Email or password incorrect!"})
    return render(request, "login.html", {'error': None})


@login_required
@never_cache
def login_successful(request, loggeduserstatus, loggedusername):
    return render(request, "{}.html".format(loggeduserstatus),
                  {"message": "How you doing today: {}".format(loggedusername)})


def logout_user(request):
    logout(request)
    return redirect(login_page)


@login_required
@never_cache
def check_beds(request, username):
    if FactoryUserStatus(username) == "receptionist":
        t = Receptionist.objects(username=username).only('state').first()
        b = Beds.objects(location=t.state).exclude('location')
        d = []
        for i in b:
            bed = Bedsh()
            bed = i
            d.append(bed)
        return render(request, "checkbeds.html", {"d": d})
    else:
        return redirect(login_page)



class Bedsh():
    room_type = StringField(required=True)
    location = StringField(required=True, default="NC")
    room_number = IntField(required=True)
    bed_number = IntField(required=True)
    patient_name = StringField(default=None)

@login_required
@never_cache
def discharge_patient(request, username):
    if FactoryUserStatus(username) == "receptionist":
        t = Receptionist.objects(username=username).only('state').first()
        if request.POST.get("patientID") != None:
            patientID = str(request.POST.get("patientID")).strip()
            doctorName = str(request.POST.get("doctorName"))
            for b in Beds.objects():
                if (b.patient_name == patientID):
                    room_t = str(b.room_type)
                    room_no = int(b.room_number)
                    bed_no = int(b.bed_number)
                    loc = str(b.location)
                    break
            Patient.objects(username=patientID).update_one(set__currently_admitted=False)
            Patient.objects(username=patientID).update_one(set__doctor_name=None)
            Doctor.objects(username=patientID).update_one(pull__patients_admitted='')
            Beds.objects(room_type=room_t, room_number=room_no, bed_number=bed_no, location=loc). \
                update_one(set__patient_name=None)
                    #return HttpResponse("Removed by backend.")
    else:
        return redirect(login_page)
    full_name = []
    doctor_name = []
    patient_id = []
    for patient in Patient.objects.only('first_name', 'last_name', 'doctor_name', 'username', 'currently_admitted'):
        if(patient.currently_admitted):
            full_name.append(str(patient.first_name + " " + patient.last_name))
            doctor_name.append(str(patient.doctor_name))
            patient_id.append(str(patient.username))
    content = zip(full_name, doctor_name, patient_id)
    return render(request, "dischargepatient.html",
                  {"content": content})


@login_required
@never_cache
def admit_patient(request, username):

    if FactoryUserStatus(username) == "receptionist":
        cnt = 0
        t = Receptionist.objects(username=username).only('state').first()
        if request.POST.get("patientID")!=None:
            patientID = str(request.POST.get("patientID")).strip()
            doctorName = str(request.POST.get("doctorName"))
            if (Patient.objects(username=patientID).first()) is not None \
                    and (Doctor.objects(username=doctorName).first()) is not None:
                room_no = int(request.POST.get("room"))
                room_type = str(request.POST.get("roomtype")).strip()
                bed = int(request.POST.get("bed"))
                Beds.objects(room_type=room_type,room_number=room_no,bed_number=bed,location=t.state).\
                    update_one(set__patient_name=patientID)
                Patient.objects(username=patientID).update(set__currently_admitted=True)
                Patient.objects(username=patientID).update(set__doctor_name=doctorName.strip())
                Doctor.objects(username=doctorName).update(push__patients_admitted=patientID)
                cnt = 1
                # enter into the db
            else:
                b = Beds.objects(location=t.state).exclude('location')
                d = []
                for i in b:
                    if i.patient_name == None:
                        bed = Bedsh()
                        bed = i
                        d.append(bed)
                if patientID == None:
                    return render(request,"admitpatient.html", {'error': "PatientID incorrect!",'d':d})
                else:
                    return render(request, "admitpatient.html", {'error': "Doctor incorrect!", 'd': d})
        b = Beds.objects(location=t.state).exclude('location')
        d = []
        for i in b:
            if i.patient_name == None:
                bed = i
                d.append(bed)
            else:
                print i.patient_name
        if cnt == 1:
            return render(request, "admitpatient.html", {'d': d, 'message':'Patient admitted'})
        else:
            return render(request, "admitpatient.html", {'d': d})
    else:
        return redirect(login_page)


@login_required
@never_cache
def delete_user(request, username):
    try:
        u = User.objects.get(username=username)
        u.delete()
        logout(request)
        return render(request, "user_deleted.html")
    except:
        return HttpResponse("Oops! Something went wrong!")

def get_clean_timings_array(text):
    to_return = []
    if text.lower() != "holiday":
        a = text.split(",")
        b = a[0].split("to")
        inter = []
        t2_one = ""
        t2_two = ""
        if len(b) >= 2:
            t1_one = b[0].strip()
            t1_two = b[1].strip()
        if len(a) >= 2:
            c = a[1].strip()
            d = c.split("to")
            if len(d) >= 2:
                t2_one = d[0].strip()
                t2_two = d[1].strip()
        inter.append(t1_one)
        inter.append(t1_two)
        for i in range(0, len(a)):
            if len(inter[0]) < 6:
                m = inter[0].split()
                m = str(m[0]) + ":00 " + m[1]
            else:
                m = inter[0].strip()

            if len(inter[1].strip()) < 6:
                m1 = inter[1].split()
                m1 = str(m1[0]) + ":00 " + m1[1]
            else:
                m1 = inter[1].strip()

            to_return.append(m)
            to_return.append(m1)
        return to_return
    else:
        return ["Not available"]


@login_required
@never_cache
def set_office_hours(request, username, day):
    time_o = []
    time = ""
    message = None
    if FactoryUserStatus(username) == "doctor":
        if request.POST:
            time1 = request.POST.get("starttime")
            time2 = request.POST.get("endtime")
            time3 = request.POST.get("starttime2")
            time4 = request.POST.get("endtime2")
            new_time = "{} to {}, {} to {}".format(time1, time2, time3, time4)
            Doctor.objects.filter(username=username, office_hours__day=day).update(
                set__office_hours__S__time=new_time)
            message = "Office hours updated successfully."
            d = Doctor.objects(username=username).only("office_hours").first()
            for i in d.office_hours:
                time_o.append(i.time)
            if day.lower() == "monday":
                time = time_o[0]
            elif day.lower() == "tuesday":
                time = time_o[1]
            elif day.lower() == "wednesday":
                time = time_o[2]
            elif day.lower() == "thursday":
                time = time_o[3]
            elif day.lower() == "friday":
                time = time_o[4]
            elif day.lower() == "saturday":
                time = time_o[5]
            else:
                time = "Incorrect Day"
            return render(request, "setofficehours.html", {"time": time, "message": message})
        d = Doctor.objects(username=username).only("office_hours").first()
        for i in d.office_hours:
            time_o.append(i.time)
        if day.lower() == "monday":
            time = time_o[0]
        elif day.lower() == "tuesday":
            time = time_o[1]
        elif day.lower() == "wednesday":
            time = time_o[2]
        elif day.lower() == "thursday":
            time = time_o[3]
        elif day.lower() == "friday":
            time = time_o[4]
        elif day.lower() == "saturday":
            time = time_o[5]
        else:
            time = "Incorrect Day"
        return render(request, "setofficehours.html", {"time": time, "message": message})




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
                    td = Doctor.objects.create(username=username, email=uemail, first_name=first_name,
                                               last_name=last_name, gender=gender, dob=dob,
                                               phone_number=phone, address=address, zipcode=zipcode, state=state,
                                               speciality=speciality, status=status)
                    td.save()
                    tr = TypeOfUser.objects.create(username=username, user_status="doctor")
                    tr.save()
                    message = "Hello Doctor,\nYou are registered in our group of hospitals successfully. Your username is {} and password is {}. Please change your password after logging in.\nHave a great day.".format(
                        username, upass)
                    send_mail(subject=("Registration Status"), message=str(message),
                              from_email="ssdigroupproject@gmail.com", recipient_list=[uemail])
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
    username = []

    for doctor in Doctor.objects.only('first_name', 'last_name', 'speciality', 'state', 'username'):
        full_name.append(str(doctor.first_name + " " + doctor.last_name))
        speciality.append(str(doctor.speciality))
        state.append(str(doctor.state))
        username.append(str(doctor.username))

    content = zip(full_name, speciality, state, username)
    return render(request, "ShowDoctors.html",
                  {"content": content})


def option_maker(text, doctor_username, day):
    to_return = []
    if text.lower() != "holiday":
        a = text.split(",")
        b = a[0].split("to")
        inter = []
        t2_one = ""
        t2_two = ""
        if len(b) >= 2:
            t1_one = b[0].strip()
            t1_two = b[1].strip()
        if len(a) >= 2:
            c = a[1].strip()
            d = c.split("to")
            if len(d) >= 2:
                t2_one = d[0].strip()
                t2_two = d[1].strip()
        inter.append(t1_one)
        inter.append(t1_two)
        for i in range(0, len(a)):
            if len(inter[0]) < 6:
                m = inter[0].split()
                m = str(m[0]) + ":00 " + m[1]
            else:
                m = inter[0].strip()

            if len(inter[1].strip()) < 6:
                m1 = inter[1].split()
                m1 = str(m1[0]) + ":00 " + m1[1]
            else:
                m1 = inter[1].strip()

            time_obj = datetime.strptime(m, '%I:%M %p')
            time_obj_two = datetime.strptime(m1, '%I:%M %p')

            to_return.append(time_obj.strftime("%H:%M %p")[:-3])
            while time_obj != time_obj_two:
                time_obj += timedelta(minutes=15)
                to_return.append(time_obj.strftime("%H:%M %p")[:-3])
            del to_return[-1]
            inter[0] = t2_one
            inter[1] = t2_two
        booked_timings = []
        doctor = Doctor.objects(username=doctor_username).only("doctor_appointments").first()
        for i in doctor.doctor_appointments:
            if datetime.strptime(i.date, "%Y-%m-%d").strftime("%A").lower() == day.lower():
                booked_timings.append(i.time)
        to_return_final = [x for x in to_return if x not in booked_timings]
        return to_return_final
    else:
        return ["Not available"]

@login_required
@never_cache
def view_appointments_doctors(request, username):
    name = []
    date = []
    time = []
    day = []
    doctor = Doctor.objects(username=str(request.user.get_username()).strip()).first()
    for p in doctor.doctor_appointments:
        name.append(p.patient)
        date.append(p.date)
        time.append(p.time)
        day.append(datetime.strptime(p.date, "%Y-%m-%d").strftime("%A"))
    content = zip(name, date, time, day)
    return render(request, "doctorvappt.html", {"content": content})


@login_required
@never_cache
def view_appointments_patients(request, username):
    name = []
    date = []
    time = []
    day = []
    state = []
    patient = Patient.objects(username=str(request.user.get_username()).strip()).first()
    for p in patient.patient_appointments:
        name.append(p.under_doctor)
        date.append(p.date)
        time.append(p.time)
        state.append(p.state)
        print p.date
        day.append(datetime.strptime(p.date, "%Y-%m-%d").strftime("%A"))
    content = zip(name, date, time, day, state)
    return render(request, "patientvappt.html", {"content": content})


@never_cache
def book_appointment(request, username):
    user_name = request.session["username"]
    date = request.session["date"]
    time = request.session["time"]
    state = request.session["state"]
    doctor_name = request.session["name"]
    if request.user.get_username():
        patient = Patient.objects(username=request.user.get_username()).first()
        patient.patient_appointments.append(
            PatientAppointments(date=date, time=time, state=state, under_doctor=doctor_name,
                                doctor_username=username))
        patient.save()
        doctor = Doctor.objects(username=str(user_name)).first()
        doctor.doctor_appointments.append(
            DoctorAppointments(date=date, time=time, patient="{} {}".format(patient.first_name, patient.last_name),
                               patient_username=str(request.user.get_username()).strip()))
        doctor.save()
        return render(request, "appointment_booked.html")
    else:
        if request.POST:
            username = request.POST.get("username")
            upass = request.POST.get("password")
            user = authenticate(username=username, password=upass)
            if user is not None:
                login(request, user)
                return redirect(book_appointment, user_name)
            else:
                return render(request, "login.html", {'error': "Email or password incorrect!"})
        return render(request, "login.html", {'error': None})


def view_time(request, username):
    error = None
    day = []
    time = []
    d = {}
    date = []
    for doctor in Doctor.objects(username=username).only('office_hours', 'first_name', 'last_name',
                                                         'speciality', 'consulting_fees', 'state', 'email'):
        for idx, i in enumerate(doctor.office_hours):
            day.append(i.day)
            time.append(i.time)
            d[str(idx + 1) + ". " + i.day] = option_maker(str(i.time), username, str(i.day))

        full_name = str(doctor.first_name) + " " + str(doctor.last_name)
        speciality = doctor.speciality
        consulting_fees = doctor.consulting_fees
        state = doctor.state
        contact = doctor.email
    d1 = OrderedDict(sorted(d.items()))
    k = list(d1.keys())
    l = list(d1.values())
    date.append(str(datetime.now())[:10])
    for i in range(1, 7):
        date.append(str(datetime.now() + timedelta(days=i))[:10])
    m = date[0].split("-")
    n = calendar.weekday(int(m[0]), int(m[1]), int(m[2]))
    items = deque(date)
    items.rotate(n)
    date_refined = list(items)
    content = zip(k, l, time, date_refined, day)
    if request.POST:
        got_time = str(request.POST.get("slot")).strip()
        if 'Monday' in request.POST:
            dts = date_refined[0]
            request.session["name"] = full_name
            request.session["date"] = dts
            request.session["time"] = got_time
            request.session["state"] = state
            request.session["username"] = username
            return redirect(book_appointment, username)
        elif 'Tuesday' in request.POST:
            dts = date_refined[1]
            return redirect(book_appointment, username, full_name, dts, got_time, state)
        elif 'Wednesday' in request.POST:
            dts = date_refined[2]
            return redirect(book_appointment, username, full_name, dts, got_time, state)
        elif 'Thursday' in request.POST:
            dts = date_refined[3]
            return redirect(book_appointment, username, full_name, dts, got_time, state)
        elif 'Friday' in request.POST:
            dts = date_refined[4]
            return redirect(book_appointment, username, full_name, dts, got_time, state)
        elif 'Saturday' in request.POST:
            dts = date_refined[5]
            return redirect(book_appointment, username, full_name, dts, got_time, state)
        else:
            error = "You cannot book appointment on Sunday"
    return render(request, "view_timings.html", {"content": content, "name": full_name, "speciality": speciality,
                                                 "consulting_fees": consulting_fees, "location": state,
                                                 "contact": contact, "error": error})


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
    return HttpResponse("This is nice!")


def backend_adder(request):
    Beds.objects(room_type='General', room_number=1, bed_number=1, location='NC'). \
        update_one(set__patient_name=None)
    Patient.objects(username='').update_one(set__currently_admitted=False)
    Patient.objects(username='').update_one(set__doctor_name=None)
    Doctor.objects(username='').update_one(pull__patients_admitted='')
    return HttpResponse("Added by backend.")


def test_page(request):
    '''
    #Doctor.objects.filter(username="dcole0", office_hours__day="Monday").update(set__office_hours__S__time="9 am to 10 am, 5 pm to 6 pm")
    b2 = Beds.objects.create(room_type="AC Deluxe", room_number=10, bed_number=1)
    b2.save()
    b2 = Beds.objects.create(room_type="AC Deluxe", room_number=11, bed_number=2)
    b2.save()
    
    return HttpResponse("hi")
    '''
    return render(request, "transferpatient.html", {"name": "Mithun", "location": "NC"})

@never_cache
@login_required
def transferpatient(request, receptionist_username, patient_username):
    error = None
    if Receptionist.objects(username=receptionist_username).only("username").first():
        patient = Patient.objects(username=patient_username).only("first_name", "last_name", "email", "state").first()
        if request.POST:
            doctorID = request.POST.get("doctorID").strip()
            description = request.POST.get("description").strip()
            doctor = Doctor.objects(username=doctorID).first()
            if doctor:
                if doctor.state != patient.state:
                    try:
                        doctor.transfer_request.append(TransferRequests(patient_id=patient_username, patient_name="{} {}".format(patient.first_name, patient.last_name),
                                                                        location=patient.state, description=description))
                        doctor.save()
                        return render(request, "ptransfers.html")
                    except:
                        error ="Something went wrong. Try again!"
                else:
                    error = "No need for approvals in internal transfer."
            else:
                error = "Doctor ID is not valid."
        return render(request, "transferpatient.html", {"name": "{} {}".format(patient.first_name, patient.last_name),
                                                        "location": patient.state, "contact": patient.state, "error": error})
    else:
        return redirect(login_page)

def validate_doctor(request):
    if request.POST:
        to_return = ""
        text = request.POST.get("doctorID")
        text1 = request.POST.get("doctorName")
        if len(text) > 4:
            doctor = Doctor.objects(username=text).only("first_name", "last_name", "speciality", "state").first()
            if doctor:
                to_return = "{} {} is {} in {}.".format(doctor.first_name, doctor.last_name,
                                                               doctor.speciality, doctor.state)
                return HttpResponse(to_return)
        elif len(text1) > 4:
            t = text1.split()
            if len(t) > 1:
                first_name = t[0]
                last_name = t[1]
                d = Doctor.objects(first_name=first_name, last_name=last_name).only("username", "speciality", "state")
                if d:
                    for doctor in d:
                        to_return += "DoctorID is {} for {} {} who is {} in {}.\n".format(doctor.username, first_name,
                                                                                      last_name, doctor.speciality, doctor.state)
                    return HttpResponse(to_return)
            else:
                d = Doctor.objects(first_name=text1).only("username", "speciality", "state", "first_name", "last_name")
                if d:
                    for doctor in d:
                        to_return += "DoctorID is {} for {} {} who is {} in {}.\n".format(doctor.username, doctor.first_name,
                                                                                          doctor.last_name, doctor.speciality,
                                                                                          doctor.state)
                    return HttpResponse(to_return)
        return HttpResponse("No doctor found.")
