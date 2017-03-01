from mongoengine.django.storage import Document, StringField, IntField

class Test(Document):
    id = IntField(primary_key=True)
    First_Name = StringField(max_length=15, required=True)
    Last_Name = StringField(max_length=15, required=True)
    Age = IntField(min_value=0, max_value=150, required=True)