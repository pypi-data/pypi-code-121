from rest_framework.utils import model_meta


def get_prefetch_fields(model, serializer, depth, prepend_string=''):
    '''
    This method should then be used with queryset.prefetch_related, to auto-fetch joined resources (to speed up nested serialization)
    This can speed up ModelViewSet and LDPViewSet alike by as high a factor as 2
    :param model: the model to be analysed
    :param serializer: an LDPSerializer instance. Used to extract the fields for each nested model
    :param depth: the depth at which to stop the recursion (should be set to the configured depth of the ViewSet)
    :param prepend_string: should be set to the default. Used in recursive calls
    :return: set of strings to prefetch for a given model. Including serialized nested fields and foreign keys recursively
    called on many-to-many fields until configured depth reached
    '''
    # the objective is to build a list of fields and nested fields which should be prefetched for the optimisation
    # of database queries
    fields = set()

    # get a list of all fields which would be serialized on this model
    # TODO: dynamically generating serializer fields is necessary to retrieve many-to-many fields at depth > 0,
    #  but the _all_ default has issues detecting reverse many-to-many fields
    # meta_args = {'model': model, 'depth': 0, 'fields': Model.get_meta(model, 'serializer_fields', '__all__')}
    # meta_class = type('Meta', (), meta_args)
    # serializer = (type(LDPSerializer)('TestSerializer', (LDPSerializer,), {'Meta': meta_class}))()
    serializer_fields = set([f for f in serializer.get_fields()])
    empty_containers = getattr(model._meta, 'empty_containers', [])

    # we are only interested in foreign keys (and many-to-many relationships)
    model_relations = model_meta.get_field_info(model).relations
    for field_name, relation_info in model_relations.items():
        # foreign keys can be added without fuss
        if not relation_info.to_many:
            fields.add((prepend_string + field_name))
            continue

        # nested fields should be added if serialized
        if field_name in serializer_fields and field_name not in empty_containers:
            fields.add((prepend_string + field_name))

            # and they should also have their immediate foreign keys prefetched if depth not reached
            if depth >= 0:
                new_prepend_str = prepend_string + field_name + '__'
                fields = fields.union(get_prefetch_fields(relation_info.related_model, serializer, depth - 1, new_prepend_str))

    return fields
