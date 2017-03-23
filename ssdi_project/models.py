from mongoengine import *

class Stakeholders(Document):
    meta = {'allow_inheritance': True}
    username = StringField(required=True, primary_key=True)
    email = EmailField(required=True)
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    gender = StringField(required=True)
    dob = StringField(required=True)
    phone_number = StringField(required=True)
    address = StringField(required=True)
    zipcode = StringField(required=True)
    state = StringField(required=True)

class Appointments(EmbeddedDocument):
    meta = {'allow_inheritance': True}
    date = StringField()
    time = StringField()

class PatientPaymentHistory(EmbeddedDocument):
    date = StringField()
    state = StringField()
    cause = StringField()
    payment_due = FloatField(default=0.0)
    payment_amount_insurance = FloatField()
    payment_amount_patient = FloatField()

class PatientAppointments(Appointments):
    state = StringField()
    under_doctor = StringField()

class Patient(Stakeholders):
    insured = BooleanField(required=True)
    currently_admitted = BooleanField(default=False)
    payment_records = ListField(EmbeddedDocumentField(PatientPaymentHistory))
    patient_appointments = ListField(EmbeddedDocumentField(PatientAppointments))

class TypeOfUser(Document):
    username = StringField(required=True)
    user_status = StringField(required=True)

class Timings(EmbeddedDocument):
    day = StringField()
    time = StringField()

class DoctorAppointments(Appointments):
    patient = StringField()

class Doctor(Stakeholders):
    speciality = StringField(required=True, max_length=25)
    status = StringField(required=True)
    consulting_fees = FloatField()
    office_hours = ListField(EmbeddedDocumentField(Timings))
    doctor_appointments = ListField(EmbeddedDocumentField(DoctorAppointments))

class Receptionist(Stakeholders):
    salary = FloatField(default=3500.0)

class Beds(Document):
    room_type = StringField(required=True)
    location = StringField(required=True, default="NC")
    availability = IntField(default=0)

class Test(Document):
    id = IntField(primary_key=True)
    email = EmailField()