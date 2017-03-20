from mongoengine import *

class Patient(Document):
    username = StringField(required=True, primary_key=True)
    email = EmailField(required=True)
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    gender = StringField(required=True)
    dob = StringField(required=True)
    insured = BooleanField(required=True)
    phone_number = StringField(required=True)
    address = StringField(required=True)
    zipcode = StringField(required=True)
    state = StringField(required=True)

class TypeOfUser(Document):
    username = StringField(required=True)
    user_status = StringField(required=True)

class Test(Document):
    id = IntField(primary_key=True)
    email = EmailField()

class Timings(EmbeddedDocument):
    day = StringField()
    time = StringField()

class Doctor(Document):
    id = IntField(primary_key=True)
    first_name = StringField(max_length=25, min_length=1, required=True)
    last_name = StringField(max_length=25, min_length=1, required=True)
    email = EmailField(required=True)
    speciality = StringField(required=True, max_length=25)
    status = StringField(required=True)
    consulting_fees = IntField()
    office_hours = ListField(EmbeddedDocumentField(Timings))