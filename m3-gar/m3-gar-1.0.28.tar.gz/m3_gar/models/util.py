from django.apps import (
    apps,
)
from django.db import (
    models,
)

import django_cte


def make_fk(model, field_name, **kwargs):
    field = model._meta.get_field(field_name)
    _, db_column = field.get_attname_column()

    unique = kwargs.pop('unique', False)
    kwargs.setdefault('on_delete', models.DO_NOTHING)
    kwargs.setdefault('related_name', '+')
    kwargs.setdefault('verbose_name', field.verbose_name)
    kwargs.setdefault('null', field.null)
    kwargs.setdefault('blank', field.blank)
    kwargs.setdefault('db_column', db_column)

    if unique:
        new_field_type = models.OneToOneField
    else:
        new_field_type = models.ForeignKey

    new_field = new_field_type(**kwargs)

    model._meta.local_fields.remove(field)
    new_field.contribute_to_class(model, field_name)


def add_params(addr_model, params_model):
    @property
    def params(self):
        Param = apps.get_model(params_model)

        class ParamManager(Param._default_manager.__class__):
            def get_queryset(manager):
                return super().get_queryset().filter(objectid=self.objectid_id)

        manager = ParamManager()
        manager.model = Param

        return manager

    addr_model.params = params


class RegionCodeModelMixin(models.Model):
    region_code = models.SmallIntegerField(verbose_name='Код региона')

    class Meta:
        abstract = True


class HierarchyMixin(models.Model):
    """
    Класс предоставляет часть интерфейса иерархической модели
    """
    parent_link_field = 'parentobjid'
    objects = django_cte.CTEManager()

    class Meta:
        abstract = True

    def get_ancestors(self, include_self=False):
        """
        Получение всех записей, стоящих выше данной в иерархии
        по parent_id (предков).
        """
        cls = self.__class__

        def make_cte(cte):
            col_parent_id = getattr(cte.col, cls.parent_link_field)

            query = cls.objects.filter(
                id=self.id
            ).values(
                "id",
                cls.parent_link_field,
                level=models.Value(0, output_field=models.IntegerField()),
            ).union(
                cte.join(
                    cls.objects.filter(isactive=True),
                    objectid=col_parent_id,
                ).values(
                    "id",
                    cls.parent_link_field,
                    level=(
                            models.ExpressionWrapper(cte.col.level, output_field=models.IntegerField()) -
                            models.Value(1, output_field=models.IntegerField())
                    )
                ),
                all=True,
            )

            return query

        ctexpr = django_cte.With.recursive(make_cte)

        ancestors = ctexpr.join(
            cls.objects.all(), id=ctexpr.col.id
        ).with_cte(
            ctexpr
        ).annotate(
            level=ctexpr.col.level,
        ).order_by("level")

        if not include_self:
            ancestors = ancestors.exclude(id=self.id)

        return ancestors

    @property
    def has_children(self):
        return self.__class__.objects.filter(
            isactive=True,
            objectid__levelid=self.objectid.levelid_id + 1,
            **{self.parent_link_field: self.objectid_id},
        ).exists()
