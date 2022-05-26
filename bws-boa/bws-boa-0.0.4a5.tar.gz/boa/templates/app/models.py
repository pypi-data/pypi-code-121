template="""
from app import db
from datetime import datetime


class ExampleModel(db.Model):
    __tablename__ = 'ms_example'

    id= db.Column(db.Integer, primary_key=True, autoincrement=True)
    name=db.Column(db.String(50), nullable=False)
    created_at=db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at=db.Column(db.DateTime(), default=datetime.utcnow)

"""