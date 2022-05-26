#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import re
import sys
import time
import sqlalchemy
import asyncio
import tornado.gen
from tornado.ioloop import IOLoop
from lycium.asynchttphandler import async_route, args_as_dict, request_body_as_json
from lycium.dbproxy import DbProxy
from lycium.webapplication import WebApplication
from sqlalchemy.orm import query

from lycium.modelutils import ModelBase, MongoBase, MODEL_DB_MAPPING
from lycium.behaviors import AppBehevior, ModifyingBehevior
from sqlalchemy import Column, Integer, SmallInteger, String
from mongoengine import StringField, IntField, DateTimeField, ObjectIdField

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

rdbms = {}
mongodbs = {}

from .builtin_dbconfig import *
try:
    from .local_dbconfig import *
except:
    pass

class TestingModelDemo1(ModelBase, AppBehevior, ModifyingBehevior):
    __tablename__ = '_t_testing_model_demo1'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    code = Column('code', String(50), index=True, unique=True)
    name = Column('name', String(255), index=True)
    description = Column('desc', String(1000))
    flag = Column('flag', SmallInteger)

class TestingModelDemo2(ModelBase, AppBehevior, ModifyingBehevior):
    __tablename__ = '_t_testing_model_demo2'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    code = Column('code', String(50), index=True, unique=True)
    name = Column('name', String(255), index=True)

class TestingModelDemo1Oracle(ModelBase, AppBehevior, ModifyingBehevior):
    __tablename__ = '_ora_t_testing_model_demo1'
    id = Column('id', Integer, sqlalchemy.Sequence('id_seq_1'), primary_key=True, autoincrement=True)
    code = Column('code', String(50), index=True, unique=True)
    name = Column('name', String(255), index=True)
    description = Column('desc', String(1000))
    flag = Column('flag', SmallInteger)

class TestingModelDemo2Oracle(ModelBase, AppBehevior, ModifyingBehevior):
    __tablename__ = '_ora_t_testing_model_demo2'
    id = Column('id', Integer, sqlalchemy.Sequence('id_seq_2'), primary_key=True, autoincrement=True)
    code = Column('code', String(50), index=True, unique=True)
    name = Column('name', String(255), index=True)

class TestingMongoModelDemo3(MongoBase):
    type = StringField()
    name = StringField()
    code = StringField()
    meta = {
        'collection': '_t_testing_model_demo3',
        'indexes': [
            ('code'),
        ]
    }

MODEL_DB_MAPPING[TestingModelDemo1.__name__] = "debug_sqlite"
MODEL_DB_MAPPING[TestingModelDemo2.__name__] = "debug_sqlite"

async def test_ensure_tables(db_category):
    dbproxy = DbProxy()
    async with dbproxy.get_dbinstance(db_category).begin() as conn:
        await conn.run_sync(ModelBase.metadata.drop_all)
    async with dbproxy.get_dbinstance(db_category).begin() as conn:
        await conn.run_sync(ModelBase.metadata.create_all)

async def unit_test_rdbms_operations(db_category):
    Demo1Model = TestingModelDemo1
    Demo2Model = TestingModelDemo2
    if rdbms[db_category]['connector'] == 'oracle':
        Demo1Model = TestingModelDemo1Oracle
        Demo2Model = TestingModelDemo2Oracle
    MODEL_DB_MAPPING[Demo1Model.__name__] = db_category
    MODEL_DB_MAPPING[Demo2Model.__name__] = db_category
    engine_name = rdbms[db_category]['connector']
    t0 = time.time()
    t1 = time.time()
    dbproxy = DbProxy()
    one = Demo1Model()
    one.app_id = '1001'
    one.code = 'initial-0'
    one.name = 'initial-name-0'
    one.description = 'initial-desc-0'
    row = await dbproxy.insert_item(one)
    assert row.id > 0
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.insert_item', t2 - t1))

    t1 = time.time()
    row_got = await dbproxy.find_item(Demo1Model, {Demo1Model.code=='initial-0'})
    assert row_got
    assert row_got.code == row.code
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.find_item', t2 - t1))

    t1 = time.time()
    row_got.name = 'name-changed'
    row_got.description = 'desc-changed'
    row_updated = await dbproxy.update_item(row_got)
    assert row_updated
    assert (row_updated.name == 'name-changed')
    row_got = await dbproxy.find_item(Demo1Model, {Demo1Model.code=='initial-0'})
    assert row_got
    assert (row_got.code == row.code and row_got.name == 'name-changed' and row_got.description == 'desc-changed')
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.update_item', t2 - t1))
    
    t1 = time.time()
    del_count = await dbproxy.del_item(row_got)
    assert del_count == 1
    row_got = await dbproxy.find_item(Demo1Model, {Demo1Model.code=='initial-0'})
    assert not row_got
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.del_item', t2 - t1))

    t1 = time.time()
    inserts = []
    for i in range(1, 2000):
        one = Demo1Model()
        one.app_id = '1001'
        one.code = 'code-%d' % (i)
        one.name = 'name-%d' % (i)
        one.description = 'desc-%s' % (i)
        inserts.append(one)
        one = Demo2Model()
        one.app_id = '1001'
        one.code = 'code-%d' % (i)
        one.name = 'name-%d' % (i)
        inserts.append(one)
    rows1_result = await dbproxy.insert_items(inserts)
    assert rows1_result
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.insert_items', t2 - t1))

    t1 = time.time()
    rows_got1 = await dbproxy.query_all(Demo1Model, {Demo1Model.code.like('code-%')})
    assert len(rows_got1) == (len(inserts) / 2)
    rows_got2 = await dbproxy.query_all(Demo2Model, {Demo2Model.code.like('code-%')})
    assert len(rows_got2) == (len(inserts) / 2)
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.query_all', t2 - t1))

    t1 = time.time()
    updates_values = {'name': 'name-changed', 'description': 'desc-changed'}
    updated_count = await dbproxy.update_values(Demo1Model, {Demo1Model.code.like('code-199%')}, updates_values)
    assert updated_count == 11
    rows_got3 = await dbproxy.query_all(Demo1Model, {Demo1Model.code.like('code-199%')})
    assert len(rows_got3) == updated_count
    assert (rows_got3[0]['name'] == 'name-changed' and rows_got3[0]['description'] == 'desc-changed')
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.update_values', t2 - t1))

    t1 = time.time()
    del_count = await dbproxy.del_items(Demo1Model, {Demo1Model.code.like('code-199%')})
    assert del_count == 11
    got_count = await dbproxy.get_count(Demo1Model, {Demo1Model.code.like('code-199%')})
    assert (got_count == 0)
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.del_items', t2 - t1))

    t1 = time.time()
    rows_got5, total = await dbproxy.query_list(Demo1Model, {Demo1Model.code.like('code-%')}, limit=20, offset=20, sort='code', direction='asc')
    assert len(rows_got5) == 20
    assert total > 0
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.query_list', t2 - t1))

    t1 = time.time()
    qry_stmt = query.Query(Demo1Model).filter(Demo1Model.code.like('code-%')).order_by('code').limit(500).offset(100)
    db_inst = dbproxy.get_model_dbinstance(Demo1Model)
    qry_sql = qry_stmt.statement.compile(db_inst.engine, compile_kwargs={"literal_binds": True})
    rows_got6 = await dbproxy.exec_query(db_inst.name, qry_sql.string)
    assert rows_got6
    assert len(rows_got6) == 500
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.exec_query', t2 - t1))

    t1 = time.time()
    update_stmt = sqlalchemy.update(Demo1Model).filter(Demo1Model.code.like('code-188%')).values(**updates_values)
    db_inst = dbproxy.get_model_dbinstance(Demo1Model)
    update_sql = update_stmt.compile(db_inst.engine, compile_kwargs={"literal_binds": True})
    update_sql_result = await dbproxy.exec_update(db_inst.name, update_sql.string)
    assert update_sql_result
    rows_got7 = await dbproxy.query_all(Demo1Model, {Demo1Model.code.like('code-188%')})
    assert len(rows_got7) == 11
    assert (rows_got7[0]['name'] == 'name-changed' and rows_got7[0]['description'] == 'desc-changed')
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.exec_update', t2 - t1))
    
    t1 = time.time()
    rows_got9, total = await dbproxy.query_list(Demo1Model, {Demo1Model.code.like('code-%')}, limit=20, offset=20, sort='code', direction='asc', selections=['code', 'name', 'description'])
    assert len(rows_got9) == 20
    assert total > 0
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.query_list with selections', t2 - t1))

    print('== <TESTING RDBMS %s FINISHED in %.02f secs> ==' % (db_category, time.time() - t0))

async def unit_test_rdbms_stored_procedure(db_category):
    procedure_create_sql = ''
    engine_name = rdbms[db_category]['connector']
    procedure_name = 't_stored_proc_demo1'
    if 'oracle' == engine_name:
        procedure_create_sql = f'''CREATE OR REPLACE PROCEDURE {procedure_name} (P_COUNT IN NUMBER, V_COUNT OUT NUMBER)
        AS
        BEGIN
        V_COUNT := P_COUNT + 1;
        END;
        '''
    elif 'mysql' == engine_name:
        procedure_create_sql = f'''DROP PROCEDURE IF EXISTS {procedure_name};
        CREATE PROCEDURE {procedure_name} (IN P_COUNT INTEGER, OUT V_COUNT INTEGER)
        BEGIN
        SET V_COUNT = P_COUNT + 1;
        END;
        '''
    elif 'mssql' == engine_name:
        procedure_create_sql = ''
    elif 'postgresql' == engine_name or 'cockroachdb' == engine_name:
        procedure_create_sql = ''
    
    if not procedure_create_sql:
        print(' - testing engine[%s] stored procedure while skipping the unsupported stored procedure' % (engine_name))
        return
    
    t0 = time.time()
    t1 = time.time()
    await DbProxy().exec_update(db_category, procedure_create_sql)
    t2 = time.time()
    print(' - testing engine[%s] create testing procedure %s finished in %.3f secs.' % (engine_name, procedure_name, t2-t1))
    
    t1 = time.time()
    proc_result = await DbProxy().call_procedure(db_category, procedure_name, [1], {'v_count': 'NUMBER'})
    if isinstance(proc_result, dict):
        assert proc_result['v_count'] == 2
    else:
        print(' - testing engine[%s] call_procedure %s result:%s' % (engine_name, procedure_name, str(proc_result)))
    t2 = time.time()
    print(' - testing engine[%s] call procedure %s finished in %.3f secs.' % (engine_name, procedure_name, t2-t1))
    print('== <TESTING RDBMS %s FINISHED in %.02f secs> ==' % (db_category, time.time() - t0))

async def unit_test_mongo_operations(db_category):
    t0 = time.time()
    engine_name = 'mongodb'
    
    t1 = t0
    result0 = await DbProxy().del_item_mongo(TestingMongoModelDemo3, {'code': re.compile(r'TESTING.*')})
    assert result0
    result0 = await DbProxy().query_all_mongo(TestingMongoModelDemo3, {'code': re.compile(r'TESTING.*')})
    assert len(result0) == 0
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'clean testing data', t2 - t1))

    t1 = time.time()
    inserts = []
    item = TestingMongoModelDemo3()
    item.type = 'TESTING'
    item.name = 'TESTING'
    item.code = 'TESTING-01'
    result1 = await DbProxy().insert_mongo(TestingMongoModelDemo3, item)
    assert result1
    result1 = await DbProxy().insert_mongo(TestingMongoModelDemo3, {'type': 'TESTING', 'name': 'TESTING', 'code': 'TESTING-02'})
    assert result1
    for i in range(1, 10):
        item = TestingMongoModelDemo3()
        item.type = 'TESTING'
        item.name = 'TESTING'
        item.code = 'TESTING-%02d' % (i+2)
        inserts.append(item)
    result1 = await DbProxy().insert_mongo(TestingMongoModelDemo3, inserts)
    assert result1
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.insert_mongo', t2 - t1))

    t1 = time.time()
    result2 = await DbProxy().find_one_mongo(TestingMongoModelDemo3, code='TESTING-01')
    assert result2
    assert result2.code == 'TESTING-01' and result2.name == 'TESTING'
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.find_one_mongo', t2 - t1))

    t1 = time.time()
    result2.name = 'CHANGED-TESTING'
    result3 = await DbProxy().save_mongo(result2)
    assert result3
    result3 = await DbProxy().find_one_mongo(TestingMongoModelDemo3, code='TESTING-01')
    assert result3
    assert result3.code == 'TESTING-01' and result3.name == 'CHANGED-TESTING'
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.save_mongo', t2 - t1))

    t1 = time.time()
    result4 = await DbProxy().del_item_mongo(TestingMongoModelDemo3, {'code': 'TESTING-01'})
    assert result4
    result4 = await DbProxy().find_one_mongo(TestingMongoModelDemo3, code='TESTING-01')
    assert not result4
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.del_item_mongo', t2 - t1))

    t1 = time.time()
    result5 = await DbProxy().update_mongo(TestingMongoModelDemo3, {'name': 'CHANGED-TESTING'}, {'code': 'TESTING-02'})
    assert result5
    result5 = await DbProxy().find_one_mongo(TestingMongoModelDemo3, code='TESTING-02')
    assert result5
    assert result5.code == 'TESTING-02' and result5.name == 'CHANGED-TESTING'
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.update_mongo', t2 - t1))

    t1 = time.time()
    result6 = await DbProxy().query_all_mongo(TestingMongoModelDemo3, {'code': re.compile(r'TESTING.*')})
    assert len(result6) == 10
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.query_all_mongo', t2 - t1))

    t1 = time.time()
    rows, total = await DbProxy().query_list_mongo(TestingMongoModelDemo3, {}, 10, 0, None, None)
    assert len(rows) == 10
    assert total >= 10
    t2 = time.time()
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.query_list_mongo', t2 - t1))

    t1 = time.time()
    result7 = await DbProxy().mongo_aggregate(TestingMongoModelDemo3, [{'$group': {'_id': {'type': '$type', 'name': '$name'}, 'occurrence': { '$sum': 1 }}}, { '$sort': { "occurrence": -1 } }])
    assert result7
    t2 = time.time()
    print(' -  aggregate testing result', result7)
    print(' - testing engine[%s] %s finished in %.03f secs.' % (engine_name, 'dbproxy.mongo_aggregate', t2 - t1))

    print('== <TESTING MONGODB %s FINISHED in %.02f secs> ==' % (db_category, time.time() - t0))
    return rows, total

async def unit_test_rdbms_query(prefer_engines = ['oracle', 'mssql', 'postgresql', 'cockroachdb', 'mysql', 'sqlite']):
    queries = []
    dbproxy = DbProxy()
    db_categories = []
    for k in rdbms.keys():
        if not k.startswith('ignore'):
            db_categories.append(k)
    fetched_category = ''
    for engine_name in prefer_engines:
        for db_category in db_categories:
            if rdbms[db_category]['connector'] == engine_name:
                fetched_category = db_category
                break
        if fetched_category:
            break
    if not fetched_category:
        return 'not found prefered database'

    db_category = fetched_category
    Demo1Model = TestingModelDemo1
    Demo2Model = TestingModelDemo2
    if rdbms[db_category]['connector'] == 'oracle':
        Demo1Model = TestingModelDemo1Oracle
        Demo2Model = TestingModelDemo2Oracle
    MODEL_DB_MAPPING[Demo1Model.__name__] = db_category
    MODEL_DB_MAPPING[Demo2Model.__name__] = db_category
    queries = [
        dbproxy.query_list(Demo1Model, {Demo1Model.code.like('code-%')}, limit=500, offset=20, sort='code', direction='asc'),
        dbproxy.query_all(Demo1Model, {Demo1Model.code.like('code-1%')}),
        dbproxy.query_list(Demo2Model, {Demo2Model.code.like('code-%')}, limit=500, offset=20, sort='code', direction='asc'),
        dbproxy.query_all(Demo2Model, {Demo2Model.code.like('code-1%')})
    ]
    await asyncio.wait(queries)

@async_route('/debug', methods=['GET'])
@tornado.gen.coroutine
def test_debug_rdbms_handler(handler, request):
    print(' >>>> handling request of rdbms debug handler on [%s]' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
    yield unit_test_rdbms_query(['oracle', 'mssql', 'postgresql', 'cockroachdb', 'mysql', 'sqlite'])
    return 'done.'

@async_route('/debug_pg', methods=['GET'])
@tornado.gen.coroutine
def test_debug_rdbms_handler(handler, request):
    print(' >>>> handling request of rdbms debug handler on [%s]' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
    yield unit_test_rdbms_query(['postgresql', 'cockroachdb', 'sqlite', 'mysql', 'oracle', 'mssql'])
    return 'done.'

@async_route('/mongo', methods=['GET'])
@tornado.gen.coroutine
def test_query_mongo(handler, request):
    rows, total = yield unit_test_mongo_operations('')
    return json.dumps({
        'total': total,
        'data': rows
    })

async def test_dbunit_rdbms_tests():
    DbProxy().setup_rdbms(rdbms)
    db_categories = []
    for k in rdbms.keys():
        if not k.startswith('ignore'):
            db_categories.append(k)
    for db_category in db_categories:
        await test_ensure_tables(db_category)
        await unit_test_rdbms_operations(db_category)

async def test_dbunit_mongodb_tests():
    DbProxy().setup_mongodbs(mongodbs)
    db_categories = []
    for k in mongodbs.keys():
        if not k.startswith('ignore'):
            db_categories.append(k)
    for db_category in db_categories:
        await unit_test_mongo_operations(db_category)

async def test_rdbms_stored_procedure():
    DbProxy().setup_rdbms(rdbms)
    db_categories = []
    for k in rdbms.keys():
        if not k.startswith('ignore'):
            db_categories.append(k)
    for db_category in db_categories:
        await unit_test_rdbms_stored_procedure(db_category)

def test_dbunittest_main():
    DbProxy().setup_rdbms(rdbms)
    DbProxy().setup_mongodbs(mongodbs)

    web_app = WebApplication()
    web_app.listen(port=8081, address='0.0.0.0')
    print('starting...')
    IOLoop.instance().start()

if __name__ == "__main__":
    test_dbunittest_main()
