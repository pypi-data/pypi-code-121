import os

from pypers.utils import utils as ut
from pypers.core.interfaces.db import get_operation_db
from pypers.core.interfaces import msgbus

from pypers.steps.base.step_generic import EmptyStep
from pypers.utils.utils import clean_folder, delete_files


class Notify(EmptyStep):

    spec = {
        "version": "2.0",
        "descr": [
            "Notifies by email about the update"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "flag",
                    "descr": "flag that index is done",
                },
            ],
            "params": [
                {
                    "name": "recipients",
                    "descr": "list of recipients emails to notify",
                    "value": []
                },
                {
                    "name": "server",
                    "descr": "server from which to send email",
                    "value": "localhost"
                },
                {
                    "name": "reply_to",
                    "descr": "email sender",
                    "value": "gbd@wipo.int"
                }
            ]
        }
    }

    def process(self):
        self.collection_name = self.collection.replace('index_', '')
        print(self.is_operation)
        if self.is_operation:
            get_operation_db().completed(self.run_id, self.collection_name)
        stage_ori_root = os.path.join(os.environ.get('ORIFILES_DIR'),
                                  self.run_id,
                                  self.pipeline_type,
                                  self.collection_name)

        stage_gbd_root = os.path.join(os.environ.get('GBDFILES_DIR'),
                                  self.run_id,
                                  self.pipeline_type,
                                  self.collection_name)

        # TODO find the manifest files in the ORIFILES_DIR (get total #records)
        # create a report from manifests
        # delete manifest files

        # TODO
        # the list of recipients ... where to set the recipients per collection (?)
        # option 1/ structured param
        # option 2/ ...

        # TODO
        # find the failed files in the GBDFILES_DIR
        # send internal email

        # # Notify on sqs
        # tmp = db.get_db().get_run_id_config(self.run_id, self.collection)
        # process_reports = [a for a in tmp.get('process_report', [])
        #                    if a['type'] == 'corrupted' or a.get('error')]
        # if process_reports:
        #     group_by_type = {}
        #     for report in process_reports:
        #         if not group_by_type.get(report['type'], None):
        #             group_by_type[report['type']] = []
        #         group_by_type[report['type']].append(report['appnum'])
        #     subject = "Errors in images or document processing " \
        #               "%s in %s" % (self.collection, self.run_id)
        #     html = ut.template_render(
        #             'notify_errors.html',
        #             collection=self.collection,
        #             reports=group_by_type,
        #             runid=self.run_id)
        #     ut.send_mail(
        #         self.reply_to, [self.reply_to], subject, html=html)
        # if len(self.recipients):
        #     report = db.get_db().get_report(self.run_id, self.collection,
        #                                     'run')
        #     if report and report['marks'] != 0:
        #         collection = self.meta['pipeline']['collection']
        #         collection_type = collection[-2:]


        #         subject = "%s %s data update in WIPO's Global %s Database" % (
        #             collection.upper()[0:2], collection.upper()[2:4],
        #             self.pipeline_type)

        #         deletions = db.get_db().get_report(
        #             self.run_id, self.collection, 'del')

        #         # sending email from localhost
        #         html = ut.template_render(
        #             'notify_%s_update.html' % collection_type,
        #             report=report,
        #             deletions=deletions)
        #         ut.send_mail(
        #             self.reply_to, self.recipients, subject, html=html)

        pipeline_dir = self.meta['pipeline']['output_dir']
        delete_files(pipeline_dir, patterns=['.*json'])
        clean_folder(pipeline_dir)
