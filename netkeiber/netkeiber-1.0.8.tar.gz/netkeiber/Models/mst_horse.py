import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class mst_horse(Base):
	
	# テーブル名
	__tablename__ = 'mst_horse'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	horse_id = fld.CharFields(10,primary_key=True,default='')
	horse_nm = fld.CharFields(30,primary_key=True,default='')
	horse_nm_en = fld.CharFields(40,default='')
	horse_sign_id = fld.CharFields(2,default='')
	birthday = fld.DateFields(default=Null)
	sex = fld.CharFields(6,default='')
	trainer_id = fld.CharFields(6,default='')
	howner_id = fld.CharFields(7,default='')
	breeder_id = fld.CharFields(7,default='')
	producing_area = fld.CharFields(30,default='')
	trn_price = fld.NumericFields(9,0,default=0)
	trn_note = fld.CharFields(30,default='')
	peds_id = fld.CharFields(12,default='')
	updinfo = fld.CharFields(40,default='')
