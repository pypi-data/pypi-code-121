import logging
import sys

from django.core.management import (
    BaseCommand,
)
from m3_gar_constants import (
    GAR_LEVELS_PLACE,
    CODE_PARAM_TYPES_OFFICIAL,
    GAR_LEVELS_STREET,
)
from m3_gar.models import (
    AddrObj,
    AddrObjParams,
    ParamTypes,
)
from m3_gar.models.hierarchy import (
    MunHierarchy,
    AdmHierarchy,
)


CACHE_OBJECTS = {}


def create_logger():
    """Возвращает объект для логгирования выполнения команды"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = create_logger()


def chunks(lst, n):
    """Разбивает лист на несколько листов размером n"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def add_object_to_cache(objectid, name):
    """Кэширование объектов запроса для сокращения количества запросов в БД"""
    CACHE_OBJECTS[objectid] = name


class Command(BaseCommand):
    """
    Команда для обновления поля name_with_parents в моделях иерархий и поля name_with_typename в модели AddrObj

    Доступные аргументы:
    --parents - заполняем поля name_with_parents
        --adm - поля обновляются для административной иерархии
        --guids - можно через запятую указать guid-ы объектов, для которых нужно обновить поле
        --levels - можно через запятую указать уровни объектов, для которых нужно обновить поле
    --typenames - заполняем поля name_with_typename для уровней 7 и 8
        --guids_typenames - можно через запятую указать guid-ы объектов, для которых нужно обновить поле
    """
    help = 'Утилита для заполнения дополнительного поля name_with_parents в модели Hierarchy и ' \
           'поля name_with_typename в модели AddrObj'

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            '--parents',
            action='store_true',
            default=None,
            help='Fill column name_with_parents',
        )

        parser.add_argument(
            '--typenames',
            action='store_true',
            default=None,
            help='Fill column name_with_typename',
        )

        parser.add_argument(
            '--adm',
            action='store_true',
            default=None,
            help='Change hierarchy model to AdmHierarchy',
        )

        parser.add_argument(
            '--guids',
            default=None,
            help='Add objects guid for filter columns for adding name_with_parents column',
        )

        parser.add_argument(
            '--guids_typenames',
            default=None,
            help='Add objects guid for filter for adding name_with_typename column',
        )

        parser.add_argument(
            '--levels',
            default=None,
            help='Add objects level for filter columns for adding data',
        )

    @staticmethod
    def get_name_with_full_typename(obj, official_type):

        addr_obj_name = ''

        try:
            addr_obj = AddrObj.objects.get(
                objectid=obj.objectid_id,
                isactual=True,
            )

            official_param = None
            if official_type:
                official_param = AddrObjParams.objects.filter(
                    objectid=obj.objectid_id,
                    typeid=official_type,
                )
        except Exception as err:
            logger.info(f'В ходе выполнения команды возникла ошибка: {err}')
        else:
            if addr_obj:
                type_name = addr_obj.type_full_name
                # Если Респ, то Республика, а если г., то город
                if addr_obj.typename and addr_obj.typename[0].islower():
                    type_name = type_name.lower()

                # Делаем так, чтобы не "область Кировская", а "Кировская область"
                # Впрочем, если есть официальное название, то используем его.
                # Перестановки остаются на уровне районов, городов и т.д.
                if official_param:
                    for actual_param in official_param:
                        # Может быть два официальных названия: Пермский край и Пермская область. Используем то,
                        # которое используется на данный момент. При этом заранее присваиваем наименование,
                        # чтобы не возникла ошибка, когда в рамках цикла по какой-либо причине условие не выполнится.
                        official_name = actual_param.value
                        if type_name.lower() in actual_param.value.lower():
                            official_name = actual_param.value
                            break

                    addr_obj_name = f'{official_name}'
                elif addr_obj.is_prefix_type:
                    addr_obj_name = f'{type_name} {addr_obj.name}'
                else:
                    addr_obj_name = f'{addr_obj.name} {type_name}'

            return addr_obj_name, addr_obj.level

    def get_name_with_parents(self, obj, official_type, max_level_value):

        result_parts = []

        for item in obj.get_ancestors(include_self=True):
            object_id = item.objectid_id

            if object_id in CACHE_OBJECTS:
                addr_obj_name = CACHE_OBJECTS[object_id]

            else:
                addr_obj_name, addr_obj_level = self.get_name_with_full_typename(item, official_type)
                if addr_obj_level != max_level_value:
                    CACHE_OBJECTS[object_id] = addr_obj_name

            result_parts.append(addr_obj_name)

        result = ', '.join(result_parts)

        return result

    @staticmethod
    def update_db_data(
            model,
            data_for_update,
            column_name,
            fill_column_function,
            max_level_value=None,
    ):

        logger.info(f'Запущено обновление полей {column_name} для модели {model.__name__}')

        official_type = ParamTypes.objects.filter(code=CODE_PARAM_TYPES_OFFICIAL, isactive=True).get()
        data = data_for_update.order_by('id')
        data_length = data.count()
        length_checked_lines = 0

        for index, lines_list in enumerate(chunks(data, 500), start=1):
            lines_for_update = []

            for line in lines_list:
                if column_name == 'name_with_parents':
                    column_value = fill_column_function(line, official_type, max_level_value)
                    if line.name_with_parents != column_value:
                        line.name_with_parents = column_value
                        lines_for_update.append(line)
                elif column_name == 'name_with_typename':
                    column_value = fill_column_function(line, official_type)[0]
                    if line.name_with_typename != column_value:
                        line.name_with_typename = column_value
                        lines_for_update.append(line)

            length_checked_lines += len(lines_list)
            logger.info(
                f'На необходимость обновления проверено {length_checked_lines} записей из {data_length} записей'
            )
            if lines_for_update:
                logger.info(f'Будет обработано {len(lines_for_update)} записей')

                model.objects.bulk_update(
                    objs=lines_for_update,
                    fields=(
                        column_name,
                    ),
                )

                logger.info(f'{len(lines_for_update)} полей записаны успешно')
            else:
                logger.info(f'Записи не нуждаются в обновлении')

    def handle(self, *args, parents, typenames, adm, guids, guids_typenames, levels, **options):

        if parents:
            # Муниципальная модель иерархии по умолчанию
            hierarchy_model = MunHierarchy
            if adm:
                hierarchy_model = AdmHierarchy

            levels_list = GAR_LEVELS_PLACE

            if guids:
                guids_list = guids.split(',')
                object_ids = AddrObj.objects.filter(
                    objectguid__in=guids_list, level__in=levels_list
                ).values_list('objectid', flat=True)
                hierarchy_data = hierarchy_model.objects.filter(objectid__in=object_ids)

            elif levels:
                levels_list = levels.split(',')
                object_ids = AddrObj.objects.filter(level__in=levels_list).values_list('objectid', flat=True)
                hierarchy_data = hierarchy_model.objects.filter(objectid__in=object_ids)

            else:
                object_ids = AddrObj.objects.filter(level__in=levels_list).values_list('objectid', flat=True)
                hierarchy_data = hierarchy_model.objects.filter(objectid__in=object_ids)

            # Максимальное значение уровня, чтобы не кэшировать объекты этого уровня
            max_level_value = str(max(levels_list))

            self.update_db_data(
                model=hierarchy_model,
                data_for_update=hierarchy_data,
                column_name='name_with_parents',
                fill_column_function=self.get_name_with_parents,
                max_level_value=max_level_value,
            )

        if typenames:
            if guids_typenames:
                guids_list = guids_typenames.split(',')
                typenames_data = AddrObj.objects.filter(
                    isactive=True,
                    objectguid__in=guids_list,
                    level__in=GAR_LEVELS_STREET,
                )

            else:
                typenames_data = AddrObj.objects.filter(
                    isactive=True,
                    level__in=GAR_LEVELS_STREET,
                )

            self.update_db_data(
                model=AddrObj,
                data_for_update=typenames_data,
                column_name='name_with_typename',
                fill_column_function=self.get_name_with_full_typename,
            )
