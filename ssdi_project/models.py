from mongoengine.django.storage import *

class Test(Document):
    id = IntField(primary_key=True)
    First_Name = StringField(max_length=15, required=True)
    Last_Name = StringField(max_length=15, required=True)
    Age = IntField(min_value=0, max_value=150, required=True)

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