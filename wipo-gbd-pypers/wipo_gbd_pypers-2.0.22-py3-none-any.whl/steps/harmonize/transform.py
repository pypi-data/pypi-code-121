import os
import json

if os.environ.get('GITHUB_TOKEN'):
    from pypers.test import MockXMLParser as Parser
    from pypers.test import MockRuleEngine as RuleEngine
    from pypers.test import ErrorSeverityMock as ErrorSeverity

else:
    from gbdtransformation.parser import Parser
    from gbdvalidation.engine import RuleEngine
    from gbdvalidation.rules import ErrorSeverity

from pypers.core.interfaces import db
from pypers.utils.utils import rename_file
from pypers.steps.base.step_generic import EmptyStep

class Transform(EmptyStep):
    spec = {
        "version": "2.0",
        "descr": [
            "Transform data files to gbd format and amend the data_files"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "data_files",
                    "descr": "input structured data",
                    "iterable": True
                },
                {
                    "name": "extraction_dir",
                    "descr": "the extraction dir",
                    "iterable": True
                }
            ],
            'outputs': [
                {
                    'name': 'data_files',
                    'descr': 'output processed data'
                }
            ]
        }
    }

    # self.data_files {'123': {'ori': _}, '234': {'ori': _}}
    def process(self):
        if not self.data_files:
            return

        collection_name = self.collection.replace('harmonize_', '')
        parser = Parser(collection_name, type=self.pipeline_type)
        validator = RuleEngine()
        office_extraction_date, archive_name = self.extraction_dir.split(os.sep)[-2:]

        errors = []
        for appnum, data in self.data_files.items():
            ori_file = os.path.join(self.extraction_dir, data['ori'])

            # attempt the transformation to append to data_files
            # {'123': {'ori': _, 'st13': _, 'gbd': _}, '234': {'ori': _, 'st13': _, 'gbd': _}}
            try:
                gbd_str = parser.run(ori_file, raise_errors=True)
                gbd_data = json.loads(gbd_str)
                st13 = gbd_data.get('st13', None)

                # failed transformation
                if not st13:
                    raise Exception('no st13 in gbd file !')
                if not gbd_data.get('statusDate'):
                    gbd_data['statusDate'] = office_extraction_date
            # transformation failed to execute
            except Exception as e:
                print(e)
                errors.append({'type': 'transform',
                              'appnum': appnum,
                              'error': str(e)})
                continue

            # get the QC of the file
            # [ { code: _, severity: _, message: _ } ]
            try:
                qc_errors = validator.validate_with_dict(gbd_data)
            # validation failed to execute
            except Exception as e:
                print(e)
                errors.append({'type': 'validation',
                                'appnum': appnum,
                                'error': str(e)})
                continue

            for error in qc_errors:
                if error.get('severity', None) == ErrorSeverity.CRITICAL:
                    raise Exception("%s : %s" % (appnum, error.get('message')))

            # set the qc in the gbd file
            if qc_errors and len(qc_errors):
                gbd_data['qc'] = qc_errors

            # write the gbd.json file
            gbd_file = ori_file.replace('.xml', '.json')
            with open(gbd_file, 'w') as f:
                json.dump(gbd_data, f, indent=2)

            # rename ori file to st13
            ori_file = rename_file(ori_file, st13)

            # set gbd, qc and st13 in the data_files
            self.data_files[appnum]['st13'] = gbd_data.get('st13')
            self.data_files[appnum]['qc'] = qc_errors or []
            self.data_files[appnum]['gbd'] = os.path.relpath(gbd_file,
                                                             self.extraction_dir)
            # update ori file in the data_files
            self.data_files[appnum]['ori'] = os.path.relpath(ori_file,
                                                             self.extraction_dir)

        # Needs to update to have a line in the reporting even if there are no errors
        db.get_db().update_process_report(self.run_id, self.collection, errors)



    def postprocess(self):
        self.data_files = [self.data_files]
