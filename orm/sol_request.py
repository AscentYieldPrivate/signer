from peewee import Model, CharField, IntegerField, DateTimeField, AutoField, TextField
from datetime import datetime
from .database import *

class SolRequest(Model):
    id = AutoField(primary_key=True)

    transaction = TextField()
    sign_address = CharField(max_length=255, index=True)
    timestamp = DateTimeField(default=datetime.utcnow, index=True)
    
    function = CharField(max_length=1000, index=True, default="")
    signature = TextField(default="")
    status = CharField(default="pending", index=True)
    info = TextField(default="")

    class Meta:
        database = database
        table_name = 'sol_requests'

