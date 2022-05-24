import os
import re
import glob
import shutil
import xmltodict
import pandas as pd
import base64
import yaml
import json
import concurrent.futures
import collections

from gbdtransformation.parser import Parser

from pypers.steps.fetch.extract.jp import models
from pypers.steps.base.extract import ExtractBase
from pypers.utils import utils


class Trademarks(ExtractBase):
    """
    Extract JPTM archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ],
        "args":
        {
            "params": [
                {
                    "name": "ori_ref_dir",
                    "type": "str",
                    "descr": "the directory that contains the original files",
                    "value": "/efs-etl/collections/brands/jptm"
                }
            ]
        }
    }

    # Folders Mapping
    archives_type_mapping = {
        "basic":  "JPWT",
        "registrations": "JPWRT",
        "applications": "JPWAT",
        "image": "JPWDI"
    }

    image_extensions = {"JP": "jpg",
                        "M2": "tiff"}

    # Parser_configuration
    # List is to enforce the order they are produced
    parser_config = [
        {
            'name': 'basic',
            'field': 'basic',
            'model': models.BasicApplicationTM,
            'template': 'jpbase',
            'ref_table':'upd_t_basic_item_art.tsv',
            'id_column':"app_num",
            'div_column': "split_num"
        },
        {
            'name': 'apps',
            'field': 'applications',
            'model': models.ApplicationMasterTM,
            'template': 'jpap',
            'ref_table': 'upd_jiken_c_t.tsv',
            'id_column': "shutugan_no",
            'div_column': None
        },
        {
            'name': 'regs',
            'field': 'registrations',
            'model': models.RegistrationMasterTM,
            'template': 'jprp',
            'ref_table': 'upd_mgt_info_t.tsv',
            'id_column': "reg_num",
            'div_column': "split_num"
        }
    ]
    parsers = {}

    mapping_merge = {
        # 'class': 'code',
        'representatives': 'identifier',
        'applicants': 'identifier'
    }

    def unify_to_str(self, el):
        if isinstance(el, float):
            el = int(el)
        return str(el)

    def list_update(self, l1, l2, key):
        if not self.mapping_merge.get(key):
            return l1
        key = self.mapping_merge[key]
        # List sanitisation:
        for el in l1:
            if(el.get(key)):
                el[key] = self.unify_to_str(el[key])
        for el in l2:
            if(el.get(key)):
                el[key] = self.unify_to_str(el[key])
        l1_keys = set([el.get(key) for el in l1])
        l2_keys = set([el.get(key) for el in l2])
        keys_to_add = l2_keys - l1_keys
        # Update the existing items
        # Generate as list with keeping the position
        l1_keys = [el.get(key) for el in l1]
        for el in l2:
            try:
                pos = l1_keys.index(el[key])
                l1[pos] = self.dict_update(el, l1[pos])
            except ValueError as e:
                pass
            except KeyError as e:
                pass
        # Add missing items
        for el in l2:
            try:
                if el[key] in keys_to_add:
                    l1.append(el)
            except KeyError as e:
                pass
        return l1

    def dict_update(self, d1, d2):
        """
        Recursively update dictionary d1 with d2.
        If replace is false, only sets undefined keys
        """
        for k, v in d2.items():
            if isinstance(v, collections.Mapping):
                r = self.dict_update(d1.get(k, {}), v)
                if k not in d1:
                    d1[k] = r
            elif isinstance(v, list):
                l2 = d1.get(k, [])
                if not isinstance(l2, list):
                    l2 = [l2]
                d1[k] = self.list_update(v, d1.get(k, []), k)
            else:
                d1[k] = d2[k]
        return d1

    def read_archive_tsv(self, extracted_folder, archive_name):
        # Loading
        path = os.path.join(extracted_folder, archive_name)

        tables = {}
        for key in glob.glob('%s/*.tsv' % path):
            # Filter unsefull files to limit memory usage
            file_name = os.path.basename(key)
            if file_name not in models.used_files:
                continue
            self.logger.info('Parsing file %s' % key)
            dataframe = pd.read_csv(key, delimiter='\t')
            tables[file_name] = dataframe
        return tables

    def parse_records(self, config, raw_data_tables):
        prefix = config['name']
        self.logger.info("Preparing %s" % prefix)
        self.map_records(raw_data_tables[config["field"]],
                         config["model"],
                         config["template"],
                         ref_table=config["ref_table"],
                         id_column=config["id_column"],
                         div_column=config["div_column"],
                         prefix=prefix)

    def map_records(self, tables, model, template, ref_table, id_column, div_column, prefix):
        if not self.parsers.get(template, None):
            self.parsers[template] = Parser(template)
        if div_column is None:
            ref_nums = tables[ref_table][id_column].to_list()
            ref_nums = [(num, None) for num in ref_nums]
        else:
            ref_nums = tables[ref_table][[id_column, div_column]].values.tolist()
        self.map_records_parallization(ref_nums, template, model, tables, prefix)

    def _sub_arry_offset(self, max_paralel, length, offset):
        if offset + max_paralel < length:
            return offset + max_paralel
        return length

    def map_records_parallization(self, vector, template, model, tables, prefix):
        max_parallel = 25
        task_counter = 0
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.map_record_model, template, model, tables, tmp[0], tmp[1], prefix): tmp[0]
                for tmp in vector[task_counter:self._sub_arry_offset(max_parallel,
                                                                     len(vector),
                                                                     task_counter)]
            }
            task_counter = len(futures)
            while futures:
                # Wait for the first future to complete.
                done, _ = concurrent.futures.wait(
                    futures, return_when=concurrent.futures.FIRST_COMPLETED
                )
                for fut in done:
                    res = fut.result()
                    num = futures.pop(fut)
                # Schedule the next batch of futures.  At some point we might run out
                # of entries in the queue if we've finished scanning the table, so
                # we need to spot that and not throw.
                for tmp in vector[task_counter:self._sub_arry_offset(len(done),
                                                                     len(vector),
                                                                     task_counter)]:
                    task_counter += 1
                    futures[executor.submit(self.map_record_model, template, model, tables, tmp[0], tmp[1], prefix)] = tmp[0]

    def save_images(self, tables, name):
        app_num = name.split('_')[1]
        os.makedirs(self.merged_dir, exist_ok=True)
        query_app_num = "app_num == %s" % app_num
        images = tables['image']['upd_t_sample.tsv'].query(query_app_num)

        buffer = {}
        types = {}

        for item in images.itertuples():
            if item.page_num not in buffer:
                buffer[item.page_num] = {}
            buffer[item.page_num][item.rec_seq_num] = item.image_data
            types[item.page_num] = item.comp_frmlchk

        names = []
        for page in sorted(buffer.keys()):
            b64 = ""
            for part in sorted(buffer[page].keys()):
                b64 += buffer[page][part]
            tmp_name = os.path.join(self.merged_dir, "%s_%s.%s" % (name, page, self.image_extensions[types[page]]))
            if self.image_extensions[types[page]] != 'jpg':
                continue
            with open(tmp_name, 'wb') as img:
                img.write(base64.b64decode(b64))
                names.append(tmp_name)
        return names

    def map_record_model(self, template, model, tables, num, split, prefix):
        tmp = model(num, split, tables)
        input_data = self.parsers[template].run_with_object(tm=tmp)
        dest_dir = os.path.join(
            self.extraction_dir,
            'yamls',
            prefix
        )
        os.makedirs(dest_dir, exist_ok=True)
        loaded_data = yaml.safe_load(input_data)
        num = None
        if loaded_data.get('applicationNumber', None):
            num = "a_%s" % loaded_data['applicationNumber']
        elif loaded_data.get('registrationNumber', None):
            num = "r_%s" % loaded_data['registrationNumber']
        if num:
            tmp = utils.appnum_to_dirs(dest_dir, num)
            os.makedirs(tmp, exist_ok=True)
            tmp = os.path.join(tmp, "%s.yml" % num)
            with open(tmp, 'w') as yml:
                yml.write(input_data)
        else:
            self.logger.error("Error in parsing %s for %s" % (prefix, num))

    def organize(self, raw_data_tables):
        prefixes = [x['name'] for x in self.parser_config]


        parsed_files_names = {}
        for prefix in prefixes:
            dest_dir = os.path.join(
                self.extraction_dir,
                'yamls',
                prefix
            )
            parsed_files_names[prefix] = {os.path.basename(x).replace('.yml', ''): x for x in glob.glob(os.path.join(dest_dir, '*', '*', '*.yml'))}


        # a union of all found application numbers
        all_keys = set(
                parsed_files_names['basic'].keys()).union(set(
                    parsed_files_names['apps'].keys())).union(set(
                        parsed_files_names['regs'].keys()))


        for key in list(all_keys):
            imgs = self.save_images(raw_data_tables, key)

            xml = self.merge(key,
                             parsed_files_names['basic'].pop(key, None),
                             parsed_files_names['apps'].pop(key, None),
                             parsed_files_names['regs'].pop(key, None))
            appnum =  key.split('_',)[1]
            self.add_xml_file(appnum, xml)
            for img in imgs:
                self.add_img_file(appnum, img)

    def merge(self, num, bs, ap, rg):
        merged_data = {}

        ori_data_file = os.path.join(utils.appnum_to_dirs(self.ori_ref_dir, num[2:]), '%s.xml' % num[2:])
        if os.path.exists(ori_data_file):
            merged_data = self.open_xml(ori_data_file)
            merged_data = merged_data['brand']

        if bs:
            try:
                from_data = self.open_yml(bs)
                merged_data = self.dict_update(merged_data, from_data)
            except: pass

        if ap:
            try:
                from_data = self.open_yml(ap)
                merged_data = self.dict_update(merged_data, from_data)
            except: pass

        if rg:
            try:
                from_data = self.open_yml(rg)
                merged_data = self.dict_update(merged_data, from_data)
            except: pass

        tmp = utils.appnum_to_dirs(self.merged_dir, num[2:])
        os.makedirs(tmp, exist_ok=True)
        tmp = os.path.join(tmp, "%s.xml" % num)

        with open(tmp, 'w') as out:
            out.write(xmltodict.unparse({'brand': merged_data}, pretty=True))
        os.makedirs(os.path.dirname(ori_data_file), exist_ok=True)
        shutil.copy(tmp, ori_data_file)
        if bs: os.remove(bs)
        if ap: os.remove(ap)
        if rg: os.remove(rg)

        return tmp

    def open_xml(self, path):
        with open(path, 'r') as fin:
            xml_string = fin.read()
            xml_dict = xmltodict.parse(xml_string,
                                       process_namespaces=False)

            return json.loads(json.dumps(xml_dict))

    def open_yml(self, path):
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f.read())
        except:
            self.logger.error("Error while opening and loading %s" % path)
            return {}

    def preprocess(self):
        self.data_files = {}
        self.img_files = {}
        self.media_files = {}
        # self.archives is a tuple of (date, {archive_name: xxx, archives[]})

        if not len(self.archives):
            return

        extraction_date = self.archives[0]
        archive_name = self.archives[1]['name']
        archives = self.archives[1]['archives']
        # prepare destination dir under pipeline scratch dir
        self.extraction_dir = os.path.join(
            self.meta['pipeline']['output_dir'],
            '__scratch',
            extraction_date,
            archive_name
        )

        # deletes the directory if prev exists
        utils.mkdir_force(self.extraction_dir)

        self.manifest = {'archive_name': archive_name,
                         'archive_file': archive_name,
                         'archive_date': extraction_date,
                         'extraction_dir': self.extraction_dir,
                         'data_files': {},
                         'img_files': {},
                         'media_files': {}}

        self.merged_dir = os.path.join(
            self.extraction_dir,
            "merged"
        )
        for archive in archives:
            archive_name, archive_ext = os.path.splitext(
                os.path.basename(archive))
            self.logger.info('%s\n%s\n' % (
                archive, re.sub(r'.', '-', archive)))
            self.logger.info('extracting into %s\n' % (self.extraction_dir))
            try:
                utils.tarextract(archive, self.extraction_dir)
            except Exception as e:
                self.logger.error("Cannot extract archive %s to %s" % (archive_name, self.extraction_dir))

        raw_data_tables = {}
        for archive_type in self.archives_type_mapping.keys():
            raw_data_tables[archive_type] = self.read_archive_tsv(self.extraction_dir, self.archives_type_mapping[archive_type])
        for config in self.parser_config:
            self.parse_records(config, raw_data_tables)
        os.makedirs(self.merged_dir, exist_ok=True)
        self.organize(raw_data_tables)


    def process(self):
        #cleanup
        for key in glob.glob('%s/*.tsv' % self.extraction_dir):
            os.remove(key)




