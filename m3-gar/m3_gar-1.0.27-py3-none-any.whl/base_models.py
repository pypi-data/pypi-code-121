# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AddrObj(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name='Уникальный идентификатор записи. Ключевое поле')
    objectid = models.BigIntegerField(verbose_name='Глобальный уникальный идентификатор адресного объекта типа INTEGER')
    objectguid = models.CharField(max_length=36, verbose_name='Глобальный уникальный идентификатор адресного объекта типа UUID')
    changeid = models.BigIntegerField(verbose_name='ID изменившей транзакции')
    name = models.CharField(max_length=250, verbose_name='Наименование')
    typename = models.CharField(max_length=50, verbose_name='Краткое наименование типа объекта')
    name_with_typename = models.CharField(
        max_length=300,
        verbose_name='Наименование c полным наименованием типа объекта',
        null=True,
    )
    level = models.CharField(max_length=10, verbose_name='Уровень адресного объекта')
    opertypeid = models.IntegerField(verbose_name='Статус действия над записью – причина появления записи')
    previd = models.BigIntegerField(verbose_name='Идентификатор записи связывания с предыдущей исторической записью', blank=True, null=True)
    nextid = models.BigIntegerField(verbose_name='Идентификатор записи связывания с последующей исторической записью', blank=True, null=True)
    updatedate = models.DateField(verbose_name='Дата внесения (обновления) записи')
    startdate = models.DateField(verbose_name='Начало действия записи')
    enddate = models.DateField(verbose_name='Окончание действия записи')
    isactual = models.BooleanField(verbose_name='Статус актуальности адресного объекта ФИАС')
    isactive = models.BooleanField(verbose_name='Признак действующего адресного объекта')

    class Meta:
        abstract = True


class AddrObjDivision(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name='Уникальный идентификатор записи. Ключевое поле')
    parentid = models.BigIntegerField(verbose_name='Родительский ID')
    childid = models.BigIntegerField(verbose_name='Дочерний ID')
    changeid = models.BigIntegerField(verbose_name='ID изменившей транзакции')

    class Meta:
        abstract = True


class AddrObjTypes(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='Идентификатор записи')
    level = models.IntegerField(verbose_name='Уровень адресного объекта')
    shortname = models.CharField(max_length=50, verbose_name='Краткое наименование типа объекта')
    name = models.CharField(max_length=250, verbose_name='Полное наименование типа объекта')
    desc = models.CharField(max_length=250, verbose_name='Описание', blank=True, null=True)
    updatedate = models.DateField(verbose_name='Дата внесения (обновления) записи')
    startdate = models.DateField(verbose_name='Начало действия записи')
    enddate = models.DateField(verbose_name='Окончание действия записи')
    isactive = models.BooleanField(verbose_name='Статус активности')

    class Meta:
        abstract = True


class AdmHierarchy(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name='Уникальный идентификатор записи. Ключевое поле')
    objectid = models.BigIntegerField(verbose_name='Глобальный уникальный идентификатор объекта')
    parentobjid = models.BigIntegerField(verbose_name='Идентификатор родительского объекта', blank=True, null=True)
    changeid = models.BigIntegerField(verbose_name='ID изменившей транзакции')
    regioncode = models.CharField(max_length=4, verbose_name='Код региона', blank=True, null=True)
    areacode = models.CharField(max_length=4, verbose_name='Код района', blank=True, null=True)
    citycode = models.CharField(max_length=4, verbose_name='Код города', blank=True, null=True)
    placecode = models.CharField(max_length=4, verbose_name='Код населенного пункта', blank=True, null=True)
    plancode = models.CharField(max_length=4, verbose_name='Код ЭПС', blank=True, null=True)
    streetcode = models.CharField(max_length=4, verbose_name='Код улицы', blank=True, null=True)
    previd = models.BigIntegerField(verbose_name='Идентификатор записи связывания с предыдущей исторической записью', blank=True, null=True)
    nextid = models.BigIntegerField(verbose_name='Идентификатор записи связывания с последующей исторической записью', blank=True, null=True)
    updatedate = models.DateField(verbose_name='Дата внесения (обновления) записи')
    startdate = models.DateField(verbose_name='Начало действия записи')
    enddate = models.DateField(verbose_name='Окончание действия записи')
    isactive = models.BooleanField(verbose_name='Признак действующего адресного объекта')
    path = models.TextField(verbose_name='Материализованный путь к объекту (полная иерархия)', blank=True, null=True)

    class Meta:
        abstract = True


class Apartments(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name='Уникальный идентификатор записи. Ключевое поле')
    objectid = models.BigIntegerField(verbose_name='Глобальный уникальный идентификатор объекта типа INTEGER')
    objectguid = models.CharField(max_length=36, verbose_name='Глобальный уникальный идентификатор адресного объекта типа UUID')
    changeid = models.BigIntegerField(verbose_name='ID изменившей транзакции')
    number = models.CharField(max_length=50, verbose_name='Номер комнаты')
    aparttype = models.IntegerField(verbose_name='Тип комнаты')
    opertypeid = models.BigIntegerField(verbose_name='Статус действия над записью – причина появления записи')
    previd = models.BigIntegerField(verbose_name='Идентификатор записи связывания с предыдущей исторической записью', blank=True, null=True)
    nextid = models.BigIntegerField(verbose_name='Идентификатор записи связывания с последующей исторической записью', blank=True, null=True)
    updatedate = models.DateField(verbose_name='Дата внесения (обновления) записи')
    startdate = models.DateField(verbose_name='Начало действия записи')
    enddate = models.DateField(verbose_name='Окончание действия записи')
    isactual = models.BooleanField(verbose_name='Статус актуальности адресного объекта ФИАС')
    isactive = models.BooleanField(verbose_name='Признак действующего адресного объекта')

    class Meta:
        abstract = True


class ApartmentTypes(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='Идентификатор типа (ключ)')
    name = models.CharField(max_length=50, verbose_name='Наименование')
    shortname = models.CharField(max_length=50, verbose_name='Краткое наименование', blank=True, null=True)
    desc = models.CharField(max_length=250, verbose_name='Описание', blank=True, null=True)
    updatedate = models.DateField(verbose_name='Дата внесения (обновления) записи')
    startdate = models.DateField(verbose_name='Начало действия записи')
    enddate = models.DateField(verbose_name='Окончание действия записи')
    isactive = models.BooleanField(verbose_name='Статус активности')

    class Meta:
        abstract = True


class Carplaces(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name='Уникальный идентификатор записи. Ключевое поле')
    objectid = models.BigIntegerField(verbose_name='Глобальный уникальный идентификатор объекта типа INTEGER')
    objectguid = models.CharField(max_length=36, verbose_name='Глобальный уникальный идентификатор адресного объекта типа UUID')
    changeid = models.BigIntegerField(verbose_name='ID изменившей транзакции')
    number = models.CharField(max_length=50, verbose_name='Номер машиноместа')
    opertypeid = models.IntegerField(verbose_name='Статус действия над записью – причина появления записи')
    previd = models.BigIntegerField(verbose_name='Идентификатор записи связывания с предыдущей исторической записью', blank=True, null=True)
    nextid = models.BigIntegerField(verbose_name='Идентификатор записи связывания с последующей исторической записью', blank=True, null=True)
    updatedate = models.DateField(verbose_name='Дата внесения (обновления) записи')
    startdate = models.DateField(verbose_name='Начало действия записи')
    enddate = models.DateField(verbose_name='Окончание действия записи')
    isactual = models.BooleanField(verbose_name='Статус актуальности адресного объекта ФИАС')
    isactive = models.BooleanField(verbose_name='Признак действующего адресного объекта')

    class Meta:
        abstract = True


class ChangeHistory(models.Model):
    changeid = models.BigIntegerField(primary_key=True, verbose_name='ID изменившей транзакции')
    objectid = models.BigIntegerField(verbose_name='Уникальный ID объекта')
    adrobjectid = models.CharField(max_length=36, verbose_name='Уникальный ID изменившей транзакции (GUID)')
    opertypeid = models.IntegerField(verbose_name='Тип операции')
    ndocid = models.BigIntegerField(verbose_name='ID документа', blank=True, null=True)
    changedate = models.DateField(verbose_name='Дата изменения')

    class Meta:
        abstract = True


class Houses(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name='Уникальный идентификатор записи. Ключевое поле')
    objectid = models.BigIntegerField(verbose_name='Глобальный уникальный идентификатор объекта типа INTEGER')
    objectguid = models.CharField(max_length=36, verbose_name='Глобальный уникальный идентификатор адресного объекта типа UUID')
    changeid = models.BigIntegerField(verbose_name='ID изменившей транзакции')
    housenum = models.CharField(max_length=50, verbose_name='Основной номер дома', blank=True, null=True)
    addnum1 = models.CharField(max_length=50, verbose_name='Дополнительный номер дома 1', blank=True, null=True)
    addnum2 = models.CharField(max_length=50, verbose_name='Дополнительный номер дома 1', blank=True, null=True)
    housetype = models.IntegerField(verbose_name='Основной тип дома', blank=True, null=True)
    addtype1 = models.IntegerField(verbose_name='Дополнительный тип дома 1', blank=True, null=True)
    addtype2 = models.IntegerField(verbose_name='Дополнительный тип дома 2', blank=True, null=True)
    opertypeid = models.IntegerField(verbose_name='Статус действия над записью – причина появления записи')
    previd = models.BigIntegerField(verbose_name='Идентификатор записи связывания с предыдущей исторической записью', blank=True, null=True)
    nextid = models.BigIntegerField(verbose_name='Идентификатор записи связывания с последующей исторической записью', blank=True, null=True)
    updatedate = models.DateField(verbose_name='Дата внесения (обновления) записи')
    startdate = models.DateField(verbose_name='Начало действия записи')
    enddate = models.DateField(verbose_name='Окончание действия записи')
    isactual = models.BooleanField(verbose_name='Статус актуальности адресного объекта ФИАС')
    isactive = models.BooleanField(verbose_name='Признак действующего адресного объекта')

    class Meta:
        abstract = True


class HouseTypes(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='Идентификатор')
    name = models.CharField(max_length=50, verbose_name='Наименование')
    shortname = models.CharField(max_length=50, verbose_name='Краткое наименование', blank=True, null=True)
    desc = models.CharField(max_length=250, verbose_name='Описание', blank=True, null=True)
    updatedate = models.DateField(verbose_name='Дата внесения (обновления) записи')
    startdate = models.DateField(verbose_name='Начало действия записи')
    enddate = models.DateField(verbose_name='Окончание действия записи')
    isactive = models.BooleanField(verbose_name='Статус активности')

    class Meta:
        abstract = True


class MunHierarchy(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name='Уникальный идентификатор записи. Ключевое поле')
    objectid = models.BigIntegerField(verbose_name='Глобальный уникальный идентификатор адресного объекта ')
    parentobjid = models.BigIntegerField(verbose_name='Идентификатор родительского объекта', blank=True, null=True)
    changeid = models.BigIntegerField(verbose_name='ID изменившей транзакции')
    oktmo = models.CharField(max_length=11, verbose_name='Код ОКТМО', blank=True, null=True)
    previd = models.BigIntegerField(verbose_name='Идентификатор записи связывания с предыдущей исторической записью', blank=True, null=True)
    nextid = models.BigIntegerField(verbose_name='Идентификатор записи связывания с последующей исторической записью', blank=True, null=True)
    updatedate = models.DateField(verbose_name='Дата внесения (обновления) записи')
    startdate = models.DateField(verbose_name='Начало действия записи')
    enddate = models.DateField(verbose_name='Окончание действия записи')
    isactive = models.BooleanField(verbose_name='Признак действующего адресного объекта')
    path = models.TextField(verbose_name='Материализованный путь к объекту (полная иерархия)', blank=True, null=True)

    class Meta:
        abstract = True


class NormativeDocs(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name='Уникальный идентификатор документа')
    name = models.CharField(max_length=8000, verbose_name='Наименование документа')
    date = models.DateField(verbose_name='Дата документа')
    number = models.CharField(max_length=150, verbose_name='Номер документа')
    type = models.IntegerField(verbose_name='Тип документа')
    kind = models.IntegerField(verbose_name='Вид документа')
    updatedate = models.DateField(verbose_name='Дата обновления')
    orgname = models.CharField(max_length=255, verbose_name='Наименование органа создвшего нормативный документ', blank=True, null=True)
    regnum = models.CharField(max_length=100, verbose_name='Номер государственной регистрации', blank=True, null=True)
    regdate = models.DateField(verbose_name='Дата государственной регистрации', blank=True, null=True)
    accdate = models.DateField(verbose_name='Дата вступления в силу нормативного документа', blank=True, null=True)
    comment = models.CharField(max_length=8000, verbose_name='Комментарий', blank=True, null=True)

    class Meta:
        abstract = True


class NormativeDocsKinds(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='Идентификатор записи')
    name = models.CharField(max_length=500, verbose_name='Наименование')

    class Meta:
        abstract = True


class NormativeDocsTypes(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='Идентификатор записи')
    name = models.CharField(max_length=500, verbose_name='Наименование')
    startdate = models.DateField(verbose_name='Дата начала действия записи')
    enddate = models.DateField(verbose_name='Дата окончания действия записи')

    class Meta:
        abstract = True


class ObjectLevels(models.Model):
    level = models.IntegerField(primary_key=True, verbose_name='Уникальный идентификатор записи. Ключевое поле. Номер уровня объекта')
    name = models.CharField(max_length=250, verbose_name='Наименование')
    shortname = models.CharField(max_length=50, verbose_name='Краткое наименование', blank=True, null=True)
    updatedate = models.DateField(verbose_name='Дата внесения (обновления) записи')
    startdate = models.DateField(verbose_name='Начало действия записи')
    enddate = models.DateField(verbose_name='Окончание действия записи')
    isactive = models.BooleanField(verbose_name='Признак действующего адресного объекта')

    class Meta:
        abstract = True


class OperationTypes(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='Идентификатор статуса (ключ)')
    name = models.CharField(max_length=100, verbose_name='Наименование')
    shortname = models.CharField(max_length=100, verbose_name='Краткое наименование', blank=True, null=True)
    desc = models.CharField(max_length=250, verbose_name='Описание', blank=True, null=True)
    updatedate = models.DateField(verbose_name='Дата внесения (обновления) записи')
    startdate = models.DateField(verbose_name='Начало действия записи')
    enddate = models.DateField(verbose_name='Окончание действия записи')
    isactive = models.BooleanField(verbose_name='Статус активности')

    class Meta:
        abstract = True


class Param(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name='Идентификатор записи')
    objectid = models.BigIntegerField(verbose_name='Глобальный уникальный идентификатор адресного объекта ')
    changeid = models.BigIntegerField(verbose_name='ID изменившей транзакции', blank=True, null=True)
    changeidend = models.BigIntegerField(verbose_name='ID завершившей транзакции')
    typeid = models.IntegerField(verbose_name='Тип параметра')
    value = models.CharField(max_length=8000, verbose_name='Значение параметра')
    updatedate = models.DateField(verbose_name='Дата внесения (обновления) записи')
    startdate = models.DateField(verbose_name='Дата начала действия записи')
    enddate = models.DateField(verbose_name='Дата окончания действия записи')

    class Meta:
        abstract = True


class ParamTypes(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='Идентификатор типа параметра (ключ)')
    name = models.CharField(max_length=50, verbose_name='Наименование')
    code = models.CharField(max_length=50, verbose_name='Краткое наименование')
    desc = models.CharField(max_length=120, verbose_name='Описание', blank=True, null=True)
    updatedate = models.DateField(verbose_name='Дата внесения (обновления) записи')
    startdate = models.DateField(verbose_name='Начало действия записи')
    enddate = models.DateField(verbose_name='Окончание действия записи')
    isactive = models.BooleanField(verbose_name='Статус активности')

    class Meta:
        abstract = True


class ReestrObjects(models.Model):
    objectid = models.BigIntegerField(primary_key=True, verbose_name='Уникальный идентификатор объекта')
    createdate = models.DateField(verbose_name='Дата создания')
    changeid = models.BigIntegerField(verbose_name='ID изменившей транзакции')
    levelid = models.IntegerField(verbose_name='Уровень объекта')
    updatedate = models.DateField(verbose_name='Дата обновления')
    objectguid = models.CharField(max_length=36, verbose_name='GUID объекта')
    isactive = models.BooleanField(verbose_name='Признак действующего объекта (1 - действующий, 0 - не действующий)')

    class Meta:
        abstract = True


class Rooms(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name='Уникальный идентификатор записи. Ключевое поле')
    objectid = models.BigIntegerField(verbose_name='Глобальный уникальный идентификатор объекта типа INTEGER')
    objectguid = models.CharField(max_length=36, verbose_name='Глобальный уникальный идентификатор адресного объекта типа UUID')
    changeid = models.BigIntegerField(verbose_name='ID изменившей транзакции')
    number = models.CharField(max_length=50, verbose_name='Номер комнаты или офиса')
    roomtype = models.IntegerField(verbose_name='Тип комнаты или офиса')
    opertypeid = models.IntegerField(verbose_name='Статус действия над записью – причина появления записи')
    previd = models.BigIntegerField(verbose_name='Идентификатор записи связывания с предыдущей исторической записью', blank=True, null=True)
    nextid = models.BigIntegerField(verbose_name='Идентификатор записи связывания с последующей исторической записью', blank=True, null=True)
    updatedate = models.DateField(verbose_name='Дата внесения (обновления) записи')
    startdate = models.DateField(verbose_name='Начало действия записи')
    enddate = models.DateField(verbose_name='Окончание действия записи')
    isactual = models.BooleanField(verbose_name='Статус актуальности адресного объекта ФИАС')
    isactive = models.BooleanField(verbose_name='Признак действующего адресного объекта')

    class Meta:
        abstract = True


class RoomTypes(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='Идентификатор типа (ключ)')
    name = models.CharField(max_length=100, verbose_name='Наименование')
    shortname = models.CharField(max_length=50, verbose_name='Краткое наименование', blank=True, null=True)
    desc = models.CharField(max_length=250, verbose_name='Описание', blank=True, null=True)
    updatedate = models.DateField(verbose_name='Дата внесения (обновления) записи')
    startdate = models.DateField(verbose_name='Начало действия записи')
    enddate = models.DateField(verbose_name='Окончание действия записи')
    isactive = models.BooleanField(verbose_name='Статус активности')

    class Meta:
        abstract = True


class Steads(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='Уникальный идентификатор записи. Ключевое поле')
    objectid = models.IntegerField(verbose_name='Глобальный уникальный идентификатор объекта типа INTEGER')
    objectguid = models.CharField(max_length=36, verbose_name='Глобальный уникальный идентификатор адресного объекта типа UUID')
    changeid = models.IntegerField(verbose_name='ID изменившей транзакции')
    number = models.CharField(max_length=250, verbose_name='Номер земельного участка')
    opertypeid = models.CharField(max_length=2, verbose_name='Статус действия над записью – причина появления записи')
    previd = models.IntegerField(verbose_name='Идентификатор записи связывания с предыдущей исторической записью', blank=True, null=True)
    nextid = models.IntegerField(verbose_name='Идентификатор записи связывания с последующей исторической записью', blank=True, null=True)
    updatedate = models.DateField(verbose_name='Дата внесения (обновления) записи')
    startdate = models.DateField(verbose_name='Начало действия записи')
    enddate = models.DateField(verbose_name='Окончание действия записи')
    isactual = models.BooleanField(verbose_name='Статус актуальности адресного объекта ФИАС')
    isactive = models.BooleanField(verbose_name='Признак действующего адресного объекта')

    class Meta:
        abstract = True
