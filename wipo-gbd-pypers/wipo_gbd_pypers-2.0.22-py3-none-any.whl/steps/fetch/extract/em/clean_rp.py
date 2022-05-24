import os
from pypers.core.interfaces import msgbus
from pypers.utils.utils import delete_files, clean_folder
from pypers.steps.fetch.common.cleanup import Cleanup as BaseCleanup


class CleanupRP(BaseCleanup):

    def postprocess(self):
        output_dir = os.path.join(os.environ['WORK_DIR'],
                                  self.run_id,
                                  self.pipeline_type,
                                  self.collection)

        if int(self.chain):
            force_restart = self.meta['pipeline'].get('force_restart', 'False')
            msgbus.get_msg_bus().send_message(self.run_id,
                                              type='brands',
                                              collection="emtm",
                                              custom_config=['pipeline.output_dir=%s' % output_dir,
                                                             'pipeline.forced_restarted=%s' % force_restart,
                                                             'pipeline.is_operation=%s' % self.is_operation,
                                                             'steps.clean.chain=1'])

        pipeline_dir = self.meta['pipeline']['output_dir']
        delete_files(pipeline_dir, patterns=['.*_output.json', '.*_input.json'])
        clean_folder(pipeline_dir)
