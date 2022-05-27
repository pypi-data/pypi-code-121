import os.path


class AllureData:

    def __init__(self, report_path):
        self.report_path = report_path

    def get_basic_info(self):
        # 从文件中读取数据
        prometheus_data_path = os.path.join(self.report_path, 'export', 'prometheusData.txt')
        with open(prometheus_data_path, 'r') as f:
            lines = f.readlines()

        # 数据清洗
        summary = {}
        for line in lines:
            line = line.strip('\n')
            data = line.split(' ')
            key = data[0]
            value = data[1]
            summary.update({key: value})

        # 数据结构化
        total = int(summary['launch_retries_run'])
        passed = int(summary['launch_status_passed'])
        fail = total - passed
        rate = int((passed / total) * 100)
        result = {"total": total, "passed": passed, "rate": rate, "fail": fail}

        return result




