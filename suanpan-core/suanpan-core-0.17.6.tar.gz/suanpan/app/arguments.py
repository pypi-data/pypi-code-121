# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import app
from suanpan import arguments as base  # pylint: disable=unused-import
from suanpan.arguments import auto  # pylint: disable=unused-import
from suanpan.dw import arguments as dw
from suanpan.imports import imports
from suanpan.storage import arguments as storage

Int = imports(f"suanpan.{app.TYPE}.arguments.Int")
Float = imports(f"suanpan.{app.TYPE}.arguments.Float")
Bool = imports(f"suanpan.{app.TYPE}.arguments.Bool")
String = imports(f"suanpan.{app.TYPE}.arguments.String")
List = imports(f"suanpan.{app.TYPE}.arguments.List")
ListOfString = imports(f"suanpan.{app.TYPE}.arguments.ListOfString")
ListOfInt = imports(f"suanpan.{app.TYPE}.arguments.ListOfInt")
ListOfFloat = imports(f"suanpan.{app.TYPE}.arguments.ListOfFloat")
ListOfBool = imports(f"suanpan.{app.TYPE}.arguments.ListOfBool")
IntOrFloat = imports(f"suanpan.{app.TYPE}.arguments.IntOrFloat")
IntFloatOrString = imports(f"suanpan.{app.TYPE}.arguments.IntFloatOrString")
BoolOrString = imports(f"suanpan.{app.TYPE}.arguments.BoolOrString")
StringOrListOfFloat = imports(f"suanpan.{app.TYPE}.arguments.StringOrListOfFloat")
Json = imports(f"suanpan.{app.TYPE}.arguments.Json")

NameFile = imports(f"suanpan.{app.TYPE}.arguments.NameFile")
File = imports(f"suanpan.{app.TYPE}.arguments.File")
Folder = imports(f"suanpan.{app.TYPE}.arguments.Folder")
Data = imports(f"suanpan.{app.TYPE}.arguments.Data")
Csv = imports(f"suanpan.{app.TYPE}.arguments.Csv")
Excel = imports(f"suanpan.{app.TYPE}.arguments.Excel")
Npy = imports(f"suanpan.{app.TYPE}.arguments.Npy")
Visual = imports(f"suanpan.{app.TYPE}.arguments.Visual")
Model = imports(f"suanpan.{app.TYPE}.arguments.Model")
H5Model = imports(f"suanpan.{app.TYPE}.arguments.H5Model")
Checkpoint = imports(f"suanpan.{app.TYPE}.arguments.Checkpoint")
JsonModel = imports(f"suanpan.{app.TYPE}.arguments.JsonModel")
Image = imports(f"suanpan.{app.TYPE}.arguments.Image")

Table = imports(f"suanpan.{app.TYPE}.arguments.Table")
DataFrame = imports(f"suanpan.{app.TYPE}.arguments.DataFrame")
