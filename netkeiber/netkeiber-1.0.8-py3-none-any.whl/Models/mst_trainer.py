import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class mst_trainer(Base):
	
	# テーブル名
	__tablename__ = 'mst_trainer'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	trainer_id = fld.CharFields(5,primary_key=True,default='')
	trainer_nm = fld.CharFields(20,default='')
	birthday = fld.DateFields(default=Null)
	belong = fld.CharFields(20,default='')
	updinfo = fld.CharFields(40,default='')
