import copy
import json
import logging
import re

from .helpers import api_collection_id, uuid, content_hash

metabase_io_log = logging.getLogger('metabase.io')

def log_item_io(activity, item):
  metabase_io_log.info("{} {} {}: {}".format(activity, item['model'], item['id'], item.get('name', '')))


class MetabaseIO:
  """
    This class holds the logic to export and import metabase objects to/from a JSON file
  """
  def __init__(self, client):
    self.client = client

  def export_json(self, collection):
    """
      Generate dictionary representation of JSON export file for all the items of the given collection name
    """
    source = self.client.get_by_name('collection', collection)
    result = {
        'items': self.get_items(source['id']),
    }
    metabase_io_log.info("⬇️ datamodel")
    result['datamodel'] = self.get_datamodel(result['items'])
    mapper = Mapper(self.client)
    metabase_io_log.info("⬇️ mappings")
    result['mappings'] = mapper.add_items(result['items'], result['datamodel'])
    return result

  def import_json(self, source, collection, with_metadata=False, overwrite=False, db_map=[]):
    """
      Create in the given collection name all the items of the source data (dictionary representation of JSON export).
      If `with_metadata` is True, the extra metadata about the model is also imported
    """
    has_items = len(source['items']) > 0
    if has_items:
      destination = self.client.get_by_name('collection', collection)
      if not overwrite and len(self.client.get('collection', destination['id'], 'items')) > 0:
          raise Exception("The destination collection is not empty")

    if has_items or with_metadata:
      mapper = Mapper(self.client)
      mapper.resolve_mappings(source['mappings'], source['datamodel'], overwrite, destination['id'], db_map)
      if with_metadata:
        self.import_metadata(source['datamodel'], mapper)
      if has_items:
        self.add_items(source['items'], destination['id'], mapper, overwrite)
    
  def get_items(self, collection_id):
    """
      Recursively retrieve the items of a collection and return the nested list of items.
      Make sure each item has a model and collection_id properties
    """
    result = []
    items = self.client.get('collection', collection_id, 'items')

    for i in items:
      log_item_io('⬇️', i)
      item = self.client.get(i['model'], i['id'])
      item['model'] = i['model']
      item = Trimmer.trim_data(item)

      if item['model'] == 'collection':
        item['items'] = self.get_items(item['id'])
      if 'collection_id' not in item:
        item['collection_id'] = collection_id
      result.append(item)

    return result

  def import_metadata(self, datamodel, mapper):
    for db in datamodel['databases'].values():
      for table in db['tables'].values():
        for field in table['fields'].values():
          dest_field_id = mapper.mappings['fields'][field['id']]

          update_attrs = {}
          field_values = field.get('has_field_values', 'none')
          if field_values != 'none':
            update_attrs['has_field_values'] = field_values

          special_type = field.get('special_type', None)
          if special_type is not None:
            update_attrs['special_type'] = special_type

          fk_target_field_id = field.get('fk_target_field_id', None)
          if fk_target_field_id is not None:
            update_attrs['fk_target_field_id'] = mapper.mappings['fields'][fk_target_field_id]

          if 'settings' in field:
            update_attrs['settings'] = field['settings']
          
          if update_attrs:
            metabase_io_log.info("🏷️ setting custom field values for {}.{}: {}".format(table['name'], field['name'], update_attrs))
            self.client.update_field(dest_field_id, update_attrs)

          if 'dimensions' in field:
            dest_field = self.client.get('field', dest_field_id)

            dimensions = field['dimensions'].copy()
            if 'human_readable_field_id' in dimensions:
              mapper.deref(dimensions, 'human_readable_field_id', mapper.mappings['fields'])

            metabase_io_log.info("🏷️ setting custom dimensions for {}.{}: {}".format(table['name'], field['name'], dimensions))
            # XXX should we not always update this ?  what if dimensions change ?
            # if 'dimensions' not in dest_field:
            self.client.add_dimension(dimensions, dest_field_id)

    for seg_id, segment in datamodel['segments'].items():
      segment['model'] = 'segment'
      if segment in mapper and not mapper.has_changed(segment):
        log_item_io('⏭️', segment)

      else:
        log_item_io('⬆️', segment)
        segment = mapper.deref_segment(segment)
        mapper.add_version_to(segment)
        if segment in mapper:
          segment['id'] = mapper[segment]
          # Mandatory revision message
          segment['revision_message'] = "Keanu update"
          upserted_segment = self.client.update_segment(segment)
        else:
          upserted_segment = self.client.add_segment(segment)
          mapper[segment] = upserted_segment['id']


  def add_items(self, items, collection_id, mapper, overwrite, only_model='all', result=[]):
    """
      Create the given items into the given collection.
      Collections are created recursively.
      The `mappings` parameter holds the information to translate db, table, field and card ids
      in the context of current Metabase instance. The object may be modified with ids of card created during the process.
      Return the nested list of created items.
    """
    if only_model == 'all':
      self.add_items(items, collection_id, mapper, overwrite, 'collection', result)
      self.add_items(items, collection_id, mapper, overwrite, 'card', result)
      self.add_items(items, collection_id, mapper, overwrite, 'dashboard', result)
      if len(mapper.missing_mapping_cards) > 0:
        # Some cards refer to dashboards that were imported after the card, update them now
        for card in mapper.missing_mapping_cards:
          c = next(filter(lambda r: r['id'] == mapper.mappings['collections'][card['collection_id']], result))
          self.add_items([card], c['id'], mapper, overwrite, 'card', c['items'])

    else:
      for item in items:
        if overwrite:
          mapper.add_version_to(item)

        if item['model'] == 'collection':
          if only_model == 'collection':
            # Is this an only-collection phase? If so, get or create the collection
            if item in mapper and not mapper.has_changed(item):
              log_item_io('⏭️', item)
              c = self.client.get('collection', mapper[item])

            else:
              log_item_io('⬆️', item)
              if item in mapper:
                dst_item = item.copy() # shallow copy is fine
                mapper.deref(dst_item, 'id', mapper.mappings['collections'])
                c = self.client.update_collection(dst_item, collection_id)
              else:
                c = self.client.add_collection(item, collection_id)
                mapper[item] = c['id']

            c['items'] = []
            result.append(c)
          else:
            # Is this non-collection insert phase? Get the collection id that was created
            c = next(filter(lambda r: r['id'] == mapper[item], result))

          # Whether its collection or non-collection phase, add all items with
          # destination collection as parent
          self.add_items(item['items'], c['id'], mapper, overwrite, only_model, c['items'])

        elif item['model'] == 'card' and only_model == 'card':
          if item in mapper and not mapper.has_changed(item):
            log_item_io('⏭️', item)
            upserted_card = self.client.get('card', mapper[item])

          else:
            log_item_io('⬆️', item)
            card = mapper.deref_card(item)
            if item in mapper:
              card['id'] = mapper[item]
              upserted_card = self.client.update_card(card, collection_id)
            else:
              upserted_card = self.client.add_card(card, collection_id)
              mapper[item] = upserted_card['id']

          result.append(upserted_card)

        # Note:
        # For cards and collections we did a copy of the object before dereferencing it,
        # while for dashboards we modify the source item.
        # this is not so important because we use them only once, but this can lead to errors if caution is not taken.
        # Immutable data structures would be useful here.
        elif item['model'] == 'dashboard' and only_model == 'dashboard':
          if item in mapper and not mapper.has_changed(item):
            log_item_io('⏭️', item)
            d = self.client.get('dashboard', mapper[item])

          else:
            log_item_io('⬆️', item)
            mapper.deref_dashboard(item)
            if item in mapper:
              mapper.deref(item, 'id', mapper.mappings['dashboards'])
              d = self.client.update_dashboard(item, collection_id)
              self.client.clear_dashboard(d)
            else:
              d = self.client.add_dashboard(item, collection_id)
              mapper[item] = d['id']
            d = self.add_dashboard_cards(item['ordered_cards'], d)

          result.append(d)

    return result

  def add_dashboard_cards(self, cards, dashboard):
    dashboard['ordered_cards'] = []
    for card in cards:
      c = self.client.add_dashboard_card(card, dashboard['id'])
      dashboard['ordered_cards'].append(c)
    return dashboard

  def get_datamodel(self, items):
    """
    Return a description (with properties of databases, tables and fields) of all databases used in items,
    as well as of all segments used by any of these databases
    """
    db_ids = self.get_database_ids(items)
    table_ids = set()
    result = { 'databases': {} }
    for db_id in db_ids:
      result['databases'][db_id] = self.db_data(self.client.get('database', db_id, 'metadata'))
      table_ids |= result['databases'][db_id]['tables'].keys()

    segments = filter(lambda s: s['table_id'] in table_ids, self.client.get('segment'))
    result['segments'] = dict(map(lambda s: (s['id'], Trimmer.trim_data(s, Trimmer.keep_segment_keys)), segments))

    return result

  def get_database_ids(self, items, result = None):
    """
    Search items for cards (questions), recursively scanning collections, and
    return a set of database_id's the cards are using.
    """
    if result is None:
      result = set()

    for item in items:
      if item['model'] == 'collection':
        self.get_database_ids(item['items'], result)
      elif item['model'] == 'card':
        result.add(item['database_id'])

    return result

  def db_data(self, db):
    f_db = { k: db[k] for k in ['id', 'name'] }
    f_db['tables'] = {}

    for table in db['tables']:
      f_table = { k: table[k] for k in ['id', 'name', 'description', 'display_name'] }
      f_table['fields'] = {}
      f_db['tables'][table['id']] = f_table

      for field in table['fields']:
        if field['special_type'] == 'type/FK':
          # If the field may have dimensions, retrieve the fields to get them
          field = self.client.get('field', field['id'])

        f_field = { k: field[k] for k in ['id', 'name', 'has_field_values', 'description', 'display_name', 'settings', 'special_type', 'fk_target_field_id'] }
        if 'dimensions' in field and len(field['dimensions']) > 0:
          f_field['dimensions'] = { k: field['dimensions'][k] for k in ['type', 'name', 'human_readable_field_id'] }

        # see https://github.com/metabase/metabase/blob/master/src/metabase/api/field.clj#L221
        if f_field['has_field_values'] == 'list' or f_field['has_field_values'] == 'type/Boolean':
          f_field['values'] = self.client.get('field', field['id'], 'values')['values']

        f_table['fields'][field['id']] = f_field

    return f_db

class Mapper:
  """
    Functions to record and translate all the ids of an export file
  """
  def __init__(self, client):
    self.client = client
    self.missing_mapping_cards = []
    self.dest_content_hashes = {}

  def add_version_to(self, item):
    source_desc = self.source_map[item['model'] + 's'][str(item['id'])]
    version_str = "Version: {}:{}".format(source_desc['uuid'], source_desc['content_hash'])
    pattern = 'Version: .{32}:.{32}'
    if item['description']:
      if re.search(pattern, item['description']):
        item['description'] = re.sub(pattern, version_str, item['description'])
      else:
        item['description'] += "\n" + version_str
    else:
      item['description'] = version_str

    return item

  def extract_version(self, item):
    version = None
    if item['description'] is not None:
      pattern = 'Version: (.{32}):(.{32})'
      m = re.search(pattern, item['description'])
      if m:
        version = { 'uuid': m.group(1), 'content_hash': m.group(2) }
    return version

  def versionned_mapping(self, item):
    return {
      'name': item['name'],
      'uuid': uuid(item),
      'content_hash': content_hash(item)
    }

  def add_items(self, items, datamodel, result = None):
    """
      Browse recursively a nested list of items and record into `result` the ids
      that will need to be translated during import.
      If `result` is not given, a new dictionary is created.
      Return the updated result.
    """
    if result is None:
      result = {'cards': {}, 'collections': {}, 'dashboards': {}, 'databases': {}, 'segments': {}}

    for item in items:
      result[item['model'] + 's'][item['id']] = self.versionned_mapping(item)
      if item['model'] == 'collection':
        self.add_items(item['items'], datamodel, result)
      elif item['model'] == 'card':
        self.add_card(item, datamodel, result)

    return result

  def add_table(self, db_id, table_id, mappings):
    if str(table_id).startswith('card__'):
      # The table is actually a saved question
      card_id = int(table_id[6:])
      if card_id not in mappings['cards']:
        mappings['cards'][card_id] = 'source_card_' + str(card_id)
    elif table_id not in mappings['databases'][db_id]['tables']:
      table = self.client.get('table', table_id)
      mappings['databases'][db_id]['tables'][table_id] = {
        'name': table['name'],
        'fields': {}
      }

  def add_fields(self, expression, datamodel, mappings):
    """
    Browse recursively a metabase expression object and add to mappings all the datamodel items (db, table, field, segment)
    (Could be better named)
    """
    if isinstance(expression, list):
      if len(expression) == 2 and expression[0] == 'field-id':
        field_id = expression[1]
        field = self.client.get('field', field_id)
        db_id = field['table']['db_id']
        table_id = field['table_id']
        if db_id not in mappings['databases']:
          mappings['databases'][db_id] = { 'name': field['table']['db']['name'], 'tables': {} }
        if table_id not in mappings['databases'][db_id]['tables']:
          mappings['databases'][db_id]['tables'][table_id] = { 'name': field['table']['name'], 'fields': {} }
        mappings['databases'][db_id]['tables'][table_id]['fields'][field_id] = field['name']
      elif len(expression) == 2 and expression[0] == 'segment':
        segment_id = expression[1]
        if segment_id not in mappings['segments']:
          segment = datamodel['segments'][segment_id]
          mappings['segments'][segment_id] = self.versionned_mapping(segment)
      else:
        for factor in expression:
          self.add_fields(factor, datamodel, mappings)

  def add_card(self, card, datamodel, mappings):
    if 'dataset_query' in card:
      dquery = card['dataset_query']
      if 'database' in dquery:
        db_id = dquery['database']
        if db_id not in mappings['databases']:
          mappings['databases'][db_id] = {
            'name': self.client.get('database', db_id)['name'],
            'tables': {}
          }

        if 'query' in dquery:
          query = dquery['query']
          if 'source-table' in query:
            table_id = query['source-table']
            self.add_table(db_id, table_id, mappings)

          for exp in query.get('expressions', {}).values():
            self.add_fields(exp, datamodel, mappings)

          for join in query.get('joins', []):
            table_id = join['source-table']
            self.add_table(db_id, table_id, mappings)
            self.add_fields(join['condition'], datamodel, mappings)

          self.add_fields(query.get('fields', []), datamodel, mappings)
          self.add_fields(query.get('filter', []), datamodel, mappings)
          self.add_fields(query.get('breakout', []), datamodel, mappings)
          self.add_fields(query.get('order-by', []), datamodel, mappings)
          
        if 'native' in dquery and 'template-tags' in dquery['native']:
          for tag in dquery['native']['template-tags'].values():
            self.add_fields(tag['dimension'], datamodel, mappings)

  def add_dashboard(self, dashboard, mappings):
    for card in dashboard['ordered_cards']:
      if 'card_id' not in card or card['card_id'] is None:
        next    # text card, wholly embedded, no mapping is needed
      #   card['card_id'] = card['id']  
      if card['card_id'] not in mappings['cards']:
        mappings['cards'][card['card_id']] = 'source_card_' + str(card['card_id'])

      for pm in card['parameter_mappings']:
        pm['card_id'] = card['card_id']
        for target_spec in pm['target']:
          if isinstance(target_spec, list):
            self.add_fields(target_spec, datamodel, mappings)

  def resolve_mappings(self, source_map, datamodel, overwrite, collection_id, db_map):
    """Translates all the ids found in source_map into corresponding ids for the
    current Metabase instance Return a dictionary { model => { source_id =>
    translated_id } }, also stored in this object

      When overwrite is True, cards, collections and dashboards are searched
      under collection_id in destination MB.

      When overwrite is False, these are not resolved because their id will be
      known after creating them. They will be added to mapping on the go.

    """
    self.source_map = source_map
    self.mappings = {'databases': {}, 'tables': {}, 'fields': {}, 'segments': {},
                     'cards': {}, 'collections': {}, 'dashboards': {}}

    for db_id, db in datamodel['databases'].items():
      dest_db = self.client.get_by_name('database', db_map.get(db['name'], db['name']))
      self.mappings['databases'][int(db_id)] = dest_db['id']

      db_data = self.client.get('database', dest_db['id'], 'metadata')
      for table_id, table in db['tables'].items():
        dest_table = list(filter(lambda t: t['name'] == table['name'], db_data['tables']))
        if len(dest_table) == 0:
          raise Exception("Table {}.{} could not be mapped".format(db['name'], table['name']))
        dest_table = dest_table[0]
        self.mappings['tables'][int(table_id)] = dest_table['id']

        for field_id, field in table['fields'].items():
          dest_field = list(filter(lambda f: f['name'] == field['name'], dest_table['fields']))
          if len(dest_field) == 0:
            raise Exception("Field {}.{}.{} could not be mapped".format(db['name'], table['name'], field['name']))
          self.mappings['fields'][int(field_id)] = dest_field[0]['id']

    if overwrite:
      dest_items = self.existing_items(collection_id)
      unmapped = self.resolve_with('uuid', source_map, dest_items)
      self.resolve_with('name', unmapped, dest_items)

    return self.mappings

  def existing_items(self, collection_id):
    dest_location = '/' if collection_id == 'root' else "/{}/".format(collection_id)
    dest_items = {
      'collections': list(filter(lambda c: dest_location in c.get('location', ''), self.client.get('collection')))
    }

    collection_ids = set(map(lambda c: c['id'], dest_items['collections']))
    # The collection ids are going to be compared to ids returned by the API, so they need to be api_collection_id'ed
    # But this affects only the root collection, and we know that root collection cannot be listed in the imported one
    # so only `collection_id` needs this treatment
    collection_ids.add(api_collection_id(collection_id))

    dest_items['cards'] = list(filter(lambda m: m['collection_id'] in collection_ids, self.client.get('card')))
    dest_items['dashboards'] = list(filter(lambda m: m['collection_id'] in collection_ids, self.client.get('dashboard')))
    dest_items['segments'] = self.client.get('segment')

    for model in ['collections', 'cards', 'dashboards', 'segments']:
      self.dest_content_hashes[model] = {}
      for item in dest_items[model]:
        version = self.extract_version(item)
        if version:
          item['uuid'] = version['uuid']
          self.dest_content_hashes[model][int(item['id'])] = version['content_hash']
        else:
          self.dest_content_hashes[model][int(item['id'])] = None

    return dest_items

  def resolve_with(self, resolve_key, source_map, dest_items):
    '''Use the `resolve_key` property to map the id of items in source_map to those in dest_items,
    when they have the same value for that property.
    Return the subset of source_map that could not be matched.'''

    models = dest_items.keys()
    unmapped = { model: {} for model in models }
    property_to_id = {
      model: { item[resolve_key]: item['id'] for item in dest_items[model] if resolve_key in item }
      for model in models
    }

    for model in models:
      for k, v in source_map[model].items():
        if v[resolve_key] in property_to_id[model]:
          self.mappings[model][int(k)] = property_to_id[model][v[resolve_key]]
        else:
          unmapped[model][k] = v

    return unmapped

  def __setitem__(self, item, mapped_id):
    self.mappings[item['model'] + 's'][item['id']] = mapped_id

  def __getitem__(self, item):
    return self.mappings[item['model'] + 's'][item['id']]

  def __contains__(self, item):
    return item['id'] in self.mappings[item['model'] + 's']

  def has_changed(self, item):
    model = item['model'] + 's'
    source_h = self.source_map[model][str(item['id'])]['content_hash']
    dest_h = self.dest_content_hashes[model].get(self[item], None)
    return dest_h != source_h

  def deref(self, obj, prop, mapping):
    obj[prop] = mapping[obj[prop]]

  def deref_table(self, table_id):
    if str(table_id).startswith('card__'):
      return self.mappings['cards'][int(table_id[6:])]
    else:
      return self.mappings['tables'][table_id]

  def deref_fields(self, expression):
    if isinstance(expression, list):
      if len(expression) == 2 and expression[0] == 'field-id':
        expression[1] = self.mappings['fields'][expression[1]]
      elif len(expression) == 2 and expression[0] == 'segment':
        expression[1] = self.mappings['segments'][expression[1]]
      else:
        for factor in expression:
          self.deref_fields(factor)
    elif isinstance(expression, dict):
      for factor in expression.values():
        self.deref_fields(factor)

  def deref_column_setting_key(self, cs):
    if cs.startswith('["ref",["field-id",'):
      csobj = json.loads(cs)
      try:
        csobj = ["ref", ["field-id", self.mappings['fields'][csobj[1][1]]]]
      except KeyError:
        # There could be stale column_settings that have orphan field-id
        # e.g. referring to archived card
        return cs
      return json.dumps(csobj)
    else:
      return cs

  def deref_column_settings(self, col_settings, for_card):
    '''Check if custom link contains a dashboard URL, and replace its id with the mapped one.
    As column settings may refer to a dashboard and as dashboards are imported after cards,
    the mapping for the referenced dashboard may not be available yet. In such a case,
    the column setting is not deref'ed and the card id (for_card) is queued, to fix the reference after
    dashboards are imported.
    '''
    if col_settings is not None and 'link_url' in col_settings:
      col_settings = col_settings.copy()
      url = col_settings['link_url']
      m = re.search('/dashboard/(\d+)', url)
      if m is not None:
        ref_id = int(m.group(1))
        if ref_id in self.mappings['dashboards']:
          url = url.replace(m.group(1), str(self.mappings['dashboards'][ref_id]))
          col_settings['link_url'] = url
        elif for_card['id'] not in map(lambda c: c['id'], self.missing_mapping_cards):
          self.missing_mapping_cards.append(for_card)

    return col_settings

  def deref_segment(self, segment):
    segment = copy.deepcopy(segment)
    segment['table_id'] = self.deref_table(segment['table_id'])
    if 'definition' in segment:
      defon = segment['definition']
      defon['source-table'] = self.deref_table(defon['source-table'])
      self.deref_fields(defon.get('filter', []))

    return segment

  def deref_card(self, card):
    original_card = card
    card = copy.deepcopy(original_card)

    if 'dataset_query' in card:
      dquery = card['dataset_query']
      if 'database' in dquery:
        dquery['database'] = self.mappings['databases'][dquery['database']]

        if 'query' in dquery:
          query = dquery['query']
          if 'source-table' in query:
            query['source-table'] = self.deref_table(query['source-table'])

            for exp in query.get('expressions', {}).values():
              self.deref_fields(exp)

          for join in query.get('joins', []):
            join['source-table'] = self.deref_table(join['source-table'])
            self.deref_fields(join['condition'])
            self.deref_fields(join.get('fields', []))

          self.deref_fields(query.get('fields', []))
          self.deref_fields(query.get('filter', []))
          self.deref_fields(query.get('breakout', []))
          self.deref_fields(query.get('order-by', []))
          self.deref_fields(query.get('aggregation', []))

        if 'native' in dquery and 'template-tags' in dquery['native']:
          for tag in dquery['native']['template-tags'].values():
            self.deref_fields(tag['dimension'])

    if 'visualization_settings' in card:
      vs = card['visualization_settings']
      if 'column_settings' in vs:
        vs['column_settings'] = {
          self.deref_column_setting_key(k): self.deref_column_settings(v, original_card)
          for k,v in vs['column_settings'].items()
        }

      if 'table.columns' in vs:
        self.deref_fields(vs['table.columns'])

    return card

  def deref_dashboard(self, dashboard):
    dashboard = {k: dashboard[k] for k in dashboard.keys() & ['name', 'description', 'parameters', 'collection_position', 'ordered_cards']}
    for c, card in enumerate(dashboard['ordered_cards']):
      card = {k: card[k] for k in card.keys() & ['card_id', 'parameter_mappings', 'series', 'row', 'col', 'sizeX', 'sizeY', 'visualization_settings']}

      if not is_virtual_card(card):
        card['card_id'] = self.mappings['cards'][card['card_id']]
        card['cardId'] = card['card_id']  # Inconsistency in dashboard API

      if 'series' in card:
        for s, serie in enumerate(card['series']):
          card_id = self.mappings['cards'][serie['id']]
          serie = self.deref_card(serie)
          serie['id'] = card_id
          card['series'][s] = serie

      for pm in card['parameter_mappings']:
        pm['card_id'] = card['card_id']
        for target_spec in pm['target']:
          if isinstance(target_spec, list):
            self.deref_fields(target_spec)

      dashboard['ordered_cards'][c] = card
    return dashboard

def broken_cards(items, datamodel, broken=set()):
  def check_field(card, fld_id, db_id):
    if not datamodel_has_field(datamodel, db_id, fld_id):
      broken.add((card['id'], card['name']))
        
  def check_query(card, values, db_id):
    for v in values:
      if isinstance(v, dict):
        check_query(card, v.values(), db_id)
      elif isinstance(v, list):
        if v[0] == 'field-id':
          check_field(card, v[1], db_id)
        else:
          check_query(card, v, db_id)

  for item in items:
    if item['model'] == 'collection':
      broken_cards(item['items'], datamodel, broken)
    elif item['model'] == 'card':
      if item['query_type'] == 'query':
        dq = item['dataset_query']
        db_id = dq['database']
        dqq = dq['query']
        check_query(item, dqq.values(), db_id)

  return broken

def broken_dashboards(items, broken=set()):
  def find_card(items, card_id):
    for item in items:
      if item['model'] == 'card' and item['id'] == card_id:
        return item
      elif item['model'] == 'collection':
        cf = find_card(item['items'], card_id)
        if cf:
          return cf
    return None

  for dash in filter(lambda i: i["model"] == "dashboard", items):
    for card in dash['ordered_cards']:
      if is_virtual_card(card):
        continue
      if find_card(items, card['card_id']) is None:
        broken.add((dash["id"], dash["name"], card['card_id']))
        
  for col in filter(lambda i: i["model"] == "collection", items):
    broken_dashboards(col["items"], broken)

  return broken

def broken_datamodel(datamodel, broken=set()):
  all_field_ids = set()
  for database in datamodel['databases'].values():
    for table in database["tables"].values():
      for fid in table['fields'].keys():
        all_field_ids.add(int(fid))

  for database in datamodel['databases'].values():
    for table in database["tables"].values():
      for field in table['fields'].values():
        if 'dimentions' in field and 'human_readable_field_id' in field['dimentions']:
          if field['dimentions']['human_readable_field_id'] not in all_field_ids:
            broken.add((field["id"],
                        "{}.{}".format(table['name'], field['name']),
                        "dimension set to nonexistent field id {}".format(field['dimentions']['human_readable_field_id'])))

        if 'fk_target_field_id' in field and field['fk_target_field_id'] is not None:
          if field['fk_target_field_id'] not in all_field_ids:
            broken.add((field["id"], "{}.{}".format(table['name'], field['name']),
                        "FK target does not exist (id {})".format(field['fk_target_field_id'])))
    return broken



def datamodel_has_field(datamodel, db_id, fld_id):
  db = datamodel['databases'][str(db_id)]
  for table in db['tables'].values():
    if str(fld_id) in table['fields']:
      return True
  return False

          


def is_virtual_card(card):
  """
    Tell whether the given card object represents a virtual dashboard card (text cards)
  """
  return 'visualization_settings' in card and 'virtual_card' in card['visualization_settings']

class Trimmer:
  keep_card_keys = [
    'id',
    'model',
    'visualization_settings',
    'description',
    'collection_position',
    'metadata_checksum',
    'collection_id',
    'name',
    'dataset_query',
    'display',
    'query_type',
    'database_id'
  ]

  keep_dashboard_keys = [
    'id',
    'model',
    'name',
    'description',
    'parameters',
    'collection_id',
    'collection_position',
    'dashboard',
    'ordered_cards'
  ]

  keep_collection_keys = [
    'id',
    'model',
    'name',
    'color',
    'description',
    'parent_id'
  ]

  keep_dashboard_card_keys = [
    'card_id',
    'parameter_mappings',
    'series',
    'row',
    'col',
    'sizeX',
    'sizeY',
    'visualization_settings'
  ]

  keep_segment_keys = [
    'id',
    'name',
    'description',
    'table_id',
    'definition'
  ]

  @staticmethod
  def trim_data(item, keep_keys=None):
    if keep_keys is None:
      if item['model'] == 'card':
        keep_keys = Trimmer.keep_card_keys
      elif item['model'] == 'collection':
        keep_keys = Trimmer.keep_collection_keys
      elif item['model'] == 'dashboard':
        keep_keys = Trimmer.keep_dashboard_keys
      else:
        raise Exception('Do not know how to trim_data on hash with no known model key')

    trimmed = { k:  item[k] for k in item if k in keep_keys }

    if 'ordered_cards' in trimmed:
      trimmed['ordered_cards'] = filter(lambda c: c.get('card', {}).get('archived', False) == False, trimmed['ordered_cards'])
      trimmed['ordered_cards'] = list(map(lambda c: Trimmer.trim_data(c, Trimmer.keep_dashboard_card_keys), trimmed['ordered_cards']))

    return trimmed

