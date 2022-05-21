import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class mst_howner(Base):
	
	# テーブル名
	__tablename__ = 'mst_howner'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	howner_id = fld.CharFields(6,primary_key=True,default='')
	howner_nm = fld.CharFields(20,default='')
	updinfo = fld.CharFields(40,default='')
