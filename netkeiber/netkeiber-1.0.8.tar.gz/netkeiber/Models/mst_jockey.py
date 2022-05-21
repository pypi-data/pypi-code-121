import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class mst_jockey(Base):
	
	# テーブル名
	__tablename__ = 'mst_jockey'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	jockey_id = fld.CharFields(5,primary_key=True,default='')
	jockey_nm = fld.CharFields(20,default='')
	jcokey_nm_kana = fld.CharFields(30,default='')
	birthday = fld.DateFields(default=Null)
	belogn = fld.CharFields(20,default='')
	updinfo = fld.CharFields(40,default='')
