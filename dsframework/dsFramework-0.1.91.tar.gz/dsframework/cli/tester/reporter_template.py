from dsframework.testable.reporter_base import ReporterBase
import pathlib
import os


class generatedClass(ReporterBase):
    @staticmethod
    def get_defaults():
        dir_path = pathlib.Path(__file__).parent.absolute()
        reports_path = dir_path / '../reports'
        cfg = {}
        cfg['reports_path'] = reports_path
        cfg['report_header'] = 'Analysis'
        return cfg

    def __init__(self, name:str="generatedClassName", **kwargs):
        ReporterBase.__init__(self, name, generatedClass.get_defaults(),  **kwargs)

    def init_analysis_dict(self):
        d = {
            'confusion_matrix': [
                'name_prefix',
                'name_first',
                'name_middle',
                'name_last',
                'name_suffix',
                'name_credentials',
                'tc_title',
                'tc_company',
                'connections_phones',
                'connections_mobiles',
                'connections_faxes',
                'connections_urls',
                'connections_emails',
                'location_address',
                'location_city',
                'location_state',
                'location_zip',
                'location_country'
            ],
            'f1_precision_recall': [
                'name_prefix',
                'name_first',
                'name_middle',
                'name_last',
                'name_suffix',
                'name_credentials',
                'tc_title',
                'tc_company',
                'connections_phones',
                'connections_mobiles',
                'connections_faxes',
                'connections_urls',
                'connections_emails',
                'location_address',
                'location_city',
                'location_state',
                'location_zip',
                'location_country'
            ],
            # 'intersection_over_union': [
            #     'name_prefix',
            #     'name_first',
            #     'name_middle',
            #     'name_last',
            #     'name_suffix',
            #     'name_credentials',
            #     'tc_title',
            #     'tc_company',
            #     'connections_phones',
            #     'connections_mobiles',
            #     'connections_faxes',
            #     'connections_urls',
            #     'connections_emails',
            #     'location_address',
            #     'location_city',
            #     'location_state',
            #     'location_zip',
            #     'location_country'
            #     ]
        }
        self.analysis_dict = d
        return NotImplementedError

    def get_report_path(self, path = ''):
        reports_path = ''
        if path:
            reports_path = pathlib.Path(path)
        else:
            reports_path = ReporterBase.get_report_path(self)
        report_name  = 'test_' + self.F.get_date_time(short=True)
        report_path  = reports_path + '/' + report_name
        return report_path

    def get_report_header(self, header = ''):
        return header if header else self.report_header

    def init_report_dirs(self, path=''):
        report_path = self.get_report_path(path)
        image_path = report_path + '/' + 'images'
        self.image_dir = image_path
        if not os.path.exists(report_path):
            os.mkdir(report_path)
        if not os.path.exists(image_path):
            os.mkdir(image_path)
