from test.integration.base_intergration_test import BaseIntegrationTest


class TestDirectProviders(BaseIntegrationTest):

    @classmethod
    def setUpClass(cls) -> None:

        super().setUpClass()

        def make_test_file(file_type, destination, path):
            cls.client.query_and_fetch(f'''
                @x = select distinct TableName, FieldName from Sys.Field order by 1,2;

                @save = use {destination}.SaveAs with @x
                    --path={path}/
                    --type:{file_type}
                    --fileNames:lumipy_test
                enduse;

                select * from @save
            ''')

        s3_path = 'eu-west-2:fbn-ci-honeycomb-webapi-cache/s3-provider-test'
        drive_path = '/honeycomb/testing/'
        make_test_file('Csv', 'AwsS3', s3_path)
        make_test_file('Excel', 'AwsS3', s3_path)
        make_test_file('Sqlite', 'AwsS3', s3_path)
        make_test_file('Csv', 'Drive', drive_path)
        make_test_file('Excel', 'Drive', drive_path)
        make_test_file('Sqlite', 'Drive', drive_path)

    def test_awss3_csv(self):
        s3_file_path = 'eu-west-2:fbn-ci-honeycomb-webapi-cache/s3-provider-test/lumipy_test.csv'
        csv = self.atlas.awss3_csv(file=s3_file_path)
        n_cols = len(csv.get_columns())
        self.assertGreater(n_cols, 0)
        df = csv.select('*').limit(10).go()
        self.assertEqual(df.shape[1], n_cols)

    def test_awss3_excel(self):
        s3_file_path = 'eu-west-2:fbn-ci-honeycomb-webapi-cache/s3-provider-test/lumipy_test.xlsx'
        xlsx = self.atlas.awss3_excel(file=s3_file_path)
        n_cols = len(xlsx.get_columns())
        self.assertGreater(n_cols, 0)
        df = xlsx.select('*').limit(10).go()
        self.assertEqual(df.shape[1], n_cols)

    def test_awss3_rawtext(self):
        raw = self.atlas.awss3_rawtext(file='eu-west-2:fbn-ci-honeycomb-webapi-cache/s3-provider-test/lumipy_test.xlsx')
        df = raw.select('*').go()
        self.assertEqual(df.shape[0], 1)
        self.assertEqual(df.shape[1], 1)

    def test_awss3_saveas(self):
        ar = self.atlas.lusid_logs_apprequest()

        lusid_tv = ar.select('*').where(ar.application == 'lusid').limit(10).to_table_var()
        drive_tv = ar.select('*').where(ar.application == 'drive').limit(10).to_table_var()

        save = self.atlas.awss3_saveas(
            lusid_tv, drive_tv,
            type='CSV',
            path='eu-west-2:fbn-ci-honeycomb-webapi-cache/s3-provider-test/',
            file_names='''
                testing_ar_lusid
                testing_ar_drive
            '''
        )

        self.assertEqual(len(save.get_columns()), 4)
        df = save.select('*').go()
        self.assertEqual(df.shape[0], 2)
        self.assertEqual(df.shape[1], 4)

    def test_awss3_sqlite(self):
        s3_file_path = 'eu-west-2:fbn-ci-honeycomb-webapi-cache/s3-provider-test/lumipy_test.sqlite'
        sqlite = self.atlas.awss3_sqlite(file=s3_file_path)
        n_cols = len(sqlite.get_columns())
        self.assertGreater(n_cols, 0)
        df = sqlite.select('*').limit(10).go()
        self.assertEqual(df.shape[1], n_cols)

    def test_awss3_xml(self):
        xml = self.atlas.awss3_xml(
            file='eu-west-2:fbn-ci-honeycomb-webapi-cache/s3-provider-test/noNamespace.xml',
            node_path='/books/book',
            columns='''
                Title=title
                Price=price
                Language=title/@lang
                Colour=title/@colour
            '''
        )
        n_cols = len(xml.get_columns())
        self.assertGreater(n_cols, 0)
        df = xml.select('*').go()
        self.assertEqual(df.shape[1], n_cols)

    def test_dev_slack_send(self):
        tv = self.atlas.lusid_logs_apprequest().select('^').limit(10).to_table_var()

        slack = self.atlas.dev_slack_send(
            tv,
            attach_as='CSV',
            channel='@jack.wright',
            text='This is the lumipy slack integration test...'
        )
        df = slack.select('*').go()
        self.assertEqual(df.shape[0], 1)
        self.assertEqual(df.shape[1], 3)

    def test_drive_csv(self):
        csv = self.atlas.drive_csv(file='/honeycomb/testing/aapl_tsla.csv')
        n_cols = len(csv.get_columns())
        self.assertGreater(n_cols, 0)
        df = csv.select('*').limit(10).go()
        self.assertEqual(df.shape[1], n_cols)

    def test_drive_excel(self):
        file_path = '/honeycomb/testing/lumipy_test.xlsx'
        xlsx = self.atlas.drive_excel(file=file_path)
        n_cols = len(xlsx.get_columns())
        self.assertGreater(n_cols, 0)
        df = xlsx.select('*').limit(10).go()
        self.assertEqual(df.shape[1], n_cols)

    def test_drive_rawtext(self):
        raw = self.atlas.drive_rawtext(file='/testing/testing_lm.csv')
        df = raw.select('*').go()
        self.assertEqual(df.shape[0], 1)
        self.assertEqual(df.shape[1], 1)

    def test_drive_saveas(self):
        ar = self.atlas.lusid_logs_apprequest()
        lusid_tv = ar.select('*').where(ar.application == 'lusid').limit(10).to_table_var()
        drive_tv = ar.select('*').where(ar.application == 'drive').limit(10).to_table_var()

        save = self.atlas.drive_saveas(
            lusid_tv, drive_tv,
            type='CSV',
            path='/testing/',
            file_names='''
                testing_ar_lusid
                testing_ar_drive
            '''
        )

        self.assertEqual(len(save.get_columns()), 4)
        df = save.select('*').go()
        self.assertEqual(df.shape[0], 2)
        self.assertEqual(df.shape[1], 4)

    def test_drive_sqlite(self):
        file_path = '/honeycomb/testing/lumipy_test.sqlite'
        sqlite = self.atlas.drive_sqlite(file=file_path)
        n_cols = len(sqlite.get_columns())
        self.assertGreater(n_cols, 0)
        df = sqlite.select('*').limit(10).go()
        self.assertEqual(df.shape[1], n_cols)

    def test_email_send(self):
        email = self.atlas.email_send()
        self.assertEqual(len(email.get_columns()), 3)

    def test_sys_admin_file_saveas(self):
        tv = self.atlas.lusid_logs_apprequest().select('^').limit(10).to_table_var()
        admin_save = self.atlas.sys_admin_file_saveas(
            tv,
            type='CSV',
            path='/honeycomb/testing/',
            file_names='lumipy_test'
        )
        qry = admin_save.select('*')
        df = qry.go()
        self.assertEqual(df.shape[0], 1)
        self.assertEqual(df.shape[1], 4)

    def test_sys_grafanaloki_logdata(self):
        falco = self.atlas.sys_grafanaloki_logdata(log_ql='{app="falco"}')
        qry = falco.select('*').limit(100)
        df = qry.go()
        self.assertEqual(df.shape[0], 100)
        self.assertGreaterEqual(df.shape[1], 3)

    def test_sys_prometheus_series_data(self):
        cpu = self.atlas.sys_prometheus_series_data(
            prom_ql='instance:node_cpu:rate:sum'
        )
        df = cpu.select('*').limit(100).go()
        self.assertEqual(df.shape[0], 100)
        self.assertGreaterEqual(df.shape[1], 3)

    def test_sys_prometheus_series_metadata(self):
        cpu_meta = self.atlas.sys_prometheus_series_metadata(metric_name='instance:node_cpu:rate:sum')
        qry = cpu_meta.select('*').limit(10)
        df = qry.go()
        self.assertEqual(df.shape[0], 10)
        self.assertGreaterEqual(df.shape[1], 3)

    def test_tools_ml_inference_sklearn(self):
        csv = self.atlas.drive_csv(file='/test-ml-data/iris.csv')
        csv = csv.select(
            csv.sepal_length_cm_,
            csv.sepal_width_cm_,
            csv.petal_length_cm_,
            csv.petal_width_cm_
        ).to_table_var()

        model = self.atlas.tools_ml_inference_sklearn(
            csv,
            onnx_file_path='/test-ml-models/iris_pca_rfc2.onnx'
        )

        qry = model.select('*')
        df = qry.go()
        self.assertEqual(df.shape[0], 150)
        self.assertEqual(df.shape[1], 4)
