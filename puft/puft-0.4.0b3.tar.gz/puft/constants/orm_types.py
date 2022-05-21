from ..models.services.database import native_db


# Helper references for shorter writing at ORMs.
Model = native_db.Model
column = native_db.Column
integer = native_db.Integer
string = native_db.String
text = native_db.Text
dbfloat = native_db.Float  # Longer name to avoid conflicts with Python's float object.
boolean = native_db.Boolean
foreign_key = native_db.ForeignKey
table = native_db.Table
check_constraint = native_db.CheckConstraint
relationship = native_db.relationship
backref = native_db.backref
pickle = native_db.PickleType
binary = native_db.LargeBinary
dtime = native_db.DateTime  # Shorter name to avoid conflicts with Python's datetime object.
