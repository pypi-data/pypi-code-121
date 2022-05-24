import datetime

from django import (
    db,
)
from django.conf import (
    settings,
)
from progress import (
    Infinite,
)

from m3_gar.importer.consts import (
    DEFAULT_BULK_LIMIT,
)
from m3_gar.importer.signals import (
    post_import_table,
    pre_import_table,
)


class LoadingBar(Infinite):
    """
    Индикатор загрузки
    T: Table (Таблица) - импортируемая в данный момент таблица
    L: Loaded (Загружено) - количество уже загруженных в таблицу строк
    U: Updated (Обновлено) - количество обновлённых записей
    FN: Filename (Имя файла) - имя файла импортируемой таблицы
    """

    text = (
        'T: %(table)s.'
        ' L: %(loaded)d'
        ' | U: %(updated)d'
        ' \tFN: %(filename)s'
    )

    hide_cursor = False
    check_tty = False

    def __init__(self, message=None, **kwargs):
        self.loaded = 0
        self.updated = 0
        self.table = kwargs.pop('table', 'unknown')
        self.filename = kwargs.pop('filename', 'unknown')

        super().__init__(message=message, **kwargs)

    def __getitem__(self, key):
        if key.startswith('_'):
            return None
        return getattr(self, key, None)

    def update(self, loaded=0, updated=0):
        if loaded:
            self.loaded = loaded
        if updated:
            self.updated = updated

        ln = self.text % self
        self.writeln(ln)


class TableLoader:
    """
    Класс для сохранения новых данных в БД. Обеспечивает пакетное сохранение
    согласно указанному лимиту и отображение индикатора загрузки в консоли.
    Обновление не поддерживается. При попытке сохранения данных по уже
    существующему в БД ключу может быть выброшен IntegrityError
    """

    def __init__(self, limit=DEFAULT_BULK_LIMIT):
        self.limit = int(limit)
        self.counter = 0
        self.upd_counter = 0
        self.today = datetime.date.today()

    def create(self, table, objects, bar):
        table.model.objects.bulk_create(objects)

        if settings.DEBUG:
            db.reset_queries()

    def load(self, tablelist, table):
        pre_import_table.send(sender=self.__class__, table=table)
        self.do_load(tablelist=tablelist, table=table)
        post_import_table.send(sender=self.__class__, table=table)

    def do_load(self, tablelist, table):
        bar = LoadingBar(table=table.name, filename=table.filename)
        bar.update()

        objects = []
        for item in table.rows(tablelist=tablelist):
            objects.append(item)
            self.counter += 1

            if self.counter and self.counter % self.limit == 0:
                self.create(table, objects, bar=bar)
                objects = []
                bar.update(loaded=self.counter)

        if objects:
            self.create(table, objects, bar=bar)

        bar.update(loaded=self.counter)
        bar.finish()


class TableUpdater(TableLoader):
    """
    Класс для сохранения или обновления данных в БД.
    Субкласс TableLoader, отличается поддержкой обновления данных.
    """

    def __init__(self, limit=DEFAULT_BULK_LIMIT):
        self.upd_limit = 100

        super().__init__(limit=limit)

    def do_load(self, tablelist, table):
        bar = LoadingBar(table=table.name, filename=table.filename)

        model = table.model
        objects = []
        for item in table.rows(tablelist=tablelist):
            try:
                model.objects.only('pk').get(pk=item.pk)
            except model.DoesNotExist:
                objects.append(item)
                self.counter += 1
            else:
                item.save()
                self.upd_counter += 1

            if self.counter and self.counter % self.limit == 0:
                self.create(table, objects, bar=bar)
                objects = []
                bar.update(loaded=self.counter)

            if self.upd_counter and self.upd_counter % self.upd_limit == 0:
                bar.update(updated=self.upd_counter)

        if objects:
            self.create(table, objects, bar=bar)

        bar.update(loaded=self.counter, updated=self.upd_counter)
        bar.finish()
