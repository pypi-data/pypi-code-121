import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class trn_race_info(Base):
	
	# テーブル名
	__tablename__ = 'trn_race_info'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	race_id = fld.CharFields(12,primary_key=True,default='')
	race_no = fld.NumericFields(2,0,default=0)
	race_nm = fld.CharFields(100,default='')
	grade = fld.NumericFields(1,0,default=0)
	course_summary = fld.CharFields(30,default='')
	direction = fld.CharFields(4,default='')
	distance = fld.NumericFields(4,0,default=0)
	ground_kbn = fld.NumericFields(1,0,default=0)
	weather = fld.CharFields(3,default='')
	ground_cond = fld.CharFields(3,default='')
	ground_cond_d = fld.CharFields(3,default='')
	race_time = fld.CharFields(5,default='')
	race_date = fld.DateFields(default=Null)
	open_info = fld.CharFields(30,default='')
	class_nm = fld.CharFields(50,default='')
	horse_sign = fld.CharFields(30,default='')
	head_count = fld.NumericFields(2,0,default=0)
	racecourse_id = fld.CharFields(2,default='')
	refund_id = fld.CharFields(10,default='')
	updinfo = fld.CharFields(40,default='')
