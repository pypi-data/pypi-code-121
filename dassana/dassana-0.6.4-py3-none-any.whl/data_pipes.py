import gzip
from .rest import *
from .dassana_env import *
from abc import ABCMeta, abstractmethod
from datetime import datetime
from json import load, loads
from io import BufferedReader, BytesIO


class Pipe(metaclass=ABCMeta):
    def __init__(self):
        self.json_logs = []

    def exclude(self, key):
        return False

    @abstractmethod
    def push(self, content):
        pass

    def flush(self):
        return forward_logs(self.json_logs)


class CloudTrailPipe(Pipe):
    def __init__(self):
        super().__init__()

    def exclude(self, key):
        return "digest" in key.lower()

    def push(self, content):
        with gzip.GzipFile(fileobj=BytesIO(content), mode="rb") as decompress_stream:
            log_data = load(decompress_stream)
            for record in log_data["Records"]:
                self.json_logs.append(record)


class VPCFlowPipe(Pipe):
    def __init__(self):
        super().__init__()

    def cast_field(self, k, v):
        int_fields = {
            "version",
            "srcport",
            "dstport",
            "protocol",
            "packets",
            "bytes",
            "start",
            "end",
            "tcp-flags",
            "traffic-path",
        }
        if k in int_fields:
            return int(v)
        else:
            return v

    def format_log(self, log):
        log = dict(
            (k, self.cast_field(k, v) if v != "-" else v) for k, v in log.items()
        )
        return log

    def push(self, content):
        with gzip.GzipFile(fileobj=BytesIO(content), mode="rb") as decompress_stream:
            log_data = b"".join(BufferedReader(decompress_stream))
            log_data = log_data.decode("utf-8")

            vpc_logs = log_data.splitlines()
            log_fields = vpc_logs[0].split(" ")
            vpc_log_struct = {key: None for key in log_fields}

            for i in range(1, len(vpc_logs)):
                line = 0
                log = vpc_logs[i].split(" ")

                for key in vpc_log_struct.keys():
                    vpc_log_struct[key] = log[line]
                    line += 1

                vpc_log_fmt = self.format_log(vpc_log_struct)
                self.json_logs.append(vpc_log_fmt)


class ALBPipe(Pipe):
    def __init__(self):
        super().__init__()

    def cast_field(self, k, v):
        int_fields = {
            "request_processing_time",
            "target_processing_time",
            "response_processing_time",
            "elb_status_code",
            "target_status_code",
            "received_bytes",
            "sent_bytes",
            "matched_rule_priority",
        }
        if k in int_fields:
            return int(v)
        else:
            return v

    def format_log(self, log_values):
        log_fields = [
            "type",
            "time",
            "elb",
            "client_port",
            "target_port",
            "request_processing_time",
            "target_processing_time",
            "response_processing_time",
            "elb_status_code",
            "target_status_code",
            "received_bytes",
            "sent_bytes",
            "request",
            "user_agent",
            "ssl_cipher",
            "ssl_protocol",
            "target_group_arn",
            "trace_id",
            "domain_name",
            "chosen_cert_name",
            "matched_rule_priority",
            "request_creation_time",
            "actions_executed",
            "redirect_url",
            "error_reason",
            "target_port_list",
            "target_status_code_list",
            "classification",
            "classificaton_reason",
        ]
        log = dict(zip(log_fields, log_values))
        log = dict(
            (k, self.cast_field(k, v) if v != "-" else v) for k, v in log.items()
        )
        return log

    def push(self, content):
        with gzip.GzipFile(fileobj=BytesIO(content), mode="rb") as decompress_stream:
            log_data = b"".join(BufferedReader(decompress_stream))
            log_data = log_data.decode("utf-8")

            access_logs = log_data.splitlines()

            for log in access_logs:
                merged_log = []
                log_fields = log.split(" ")
                i = 0
                while i < len(log_fields):
                    start_index = i
                    merged_string = ""
                    if log_fields[start_index][0] in ('"', "["):
                        if log_fields[start_index][-1] not in ('"', "]"):
                            i += 1
                            while log_fields[i][-1] not in ('"', "]"):
                                i += 1
                            merged_string = " ".join(log_fields[start_index:i])[1:-1]
                            i += 1
                        else:
                            merged_string = log_fields[start_index][1:-1]
                            i += 1
                    else:
                        merged_string = log_fields[start_index]
                        i += 1
                    merged_log.append(merged_string)

                alb_log_struct = self.format_log(merged_log)
                self.json_logs.append(alb_log_struct)


class WAFPipe(Pipe):
    def __init__(self):
        super().__init__()

    def push(self, content):
        with gzip.GzipFile(fileobj=BytesIO(content), mode="rb") as decompress_stream:
            log_data = b"".join(BufferedReader(decompress_stream))
            log_data = log_data.split(b"\n")
            for i in range(0, len(log_data) - 1):
                log = log_data[i].decode("utf-8")
                self.json_logs.append(log)


class S3AccessPipe(Pipe):
    def __init__(self):
        super().__init__()

    def convert_to_unix_ms(self, ts):
        ts_fmtd = ts.strip("[]").split(" ")[0]  # Remove offset
        ts_unix = datetime.strptime(ts_fmtd, "%d/%b/%Y:%H:%M:%S")
        epoch = datetime.utcfromtimestamp(0)
        return int((ts_unix - epoch).total_seconds() * 1000.0)

    def cast_field(self, k, v):
        int_fields = {
            "http_status",
            "error_code",
            "bytes_sent",
            "object_size",
            "total_time",
            "turn_around_time",
        }
        if k in int_fields:
            return int(v)
        elif k == "time":
            return self.convert_to_unix_ms(v)
        else:
            return v

    def format_log(self, log_values):
        log_fields = [
            "bucket_owner",
            "bucket",
            "time",
            "remote_ip",
            "requestor",
            "request_id",
            "operation",
            "key",
            "request_uri",
            "http_status",
            "error_code",
            "bytes_sent",
            "object_size",
            "total_time",
            "turn_around_time",
            "referer",
            "user_agent",
            "version_id",
            "host_id",
            "signature_version",
            "cipher_suite",
            "authentication_type",
            "host_header",
            "tls_version",
            "access_point_arn",
        ]
        log = dict(zip(log_fields, log_values))
        log = dict(
            (k, self.cast_field(k, v) if v != "-" else v) for k, v in log.items()
        )
        return log

    def push(self, content):
        log_data = content.decode("utf-8")
        access_logs = log_data.splitlines()

        for log in access_logs:
            merged_log = []
            log_fields = log.split(" ")
            i = 0
            while i < len(log_fields):
                start_index = i
                merged_string = ""
                if log_fields[start_index][0] in ('"', "["):
                    if log_fields[start_index][-1] not in ('"', "]"):
                        i += 1
                        while log_fields[i][-1] not in ('"', "]"):
                            i += 1
                        merged_string = " ".join(log_fields[start_index:i])[1:-1]
                        i += 1
                    else:
                        merged_string = log_fields[start_index][1:-1]
                        i += 1
                else:
                    merged_string = log_fields[start_index]
                    i += 1
                merged_log.append(merged_string)

            access_log_struct = self.format_log(merged_log)
            self.json_logs.append(access_log_struct)


class Route53QueryPipe(Pipe):
    def __init__(self):
        super().__init__()

    def push(self, content):
        with gzip.GzipFile(fileobj=BytesIO(content), mode="rb") as decompress_stream:
            log_data = b"".join(BufferedReader(decompress_stream))
            log_data = log_data.decode("utf-8")

            for log in log_data.splitlines():
                self.json_logs.append(loads(log))


class NetworkFirewallPipe(Pipe):
    def __init__(self):
        super().__init__()

    def push(self, content):
        with gzip.GzipFile(fileobj=BytesIO(content), mode="rb") as decompress_stream:
            log_data = b"".join(BufferedReader(decompress_stream))
            log_data = log_data.decode("utf-8")

            for log in log_data.splitlines():
                log = loads(log)
                log["event_timestamp"] = int(log["event_timestamp"])
                self.json_logs.append(log)


class AzureActivityPipe(Pipe):
    def __init__(self):
        super().__init__()

    def push(self, content):
        log_data = loads(content)
        for record in log_data["records"]:
            self.json_logs.append(record)


def DataPipe():

    pipe_selector = {
        "aws_cloudtrail": CloudTrailPipe,
        "aws_vpc_flow": VPCFlowPipe,
        "aws_alb": ALBPipe,
        "aws_waf": WAFPipe,
        "aws_s3_access": S3AccessPipe,
        "aws_route53_query": Route53QueryPipe,
        "aws_network_firewall": NetworkFirewallPipe,
        "azure_test": AzureActivityPipe,
    }

    return pipe_selector[get_app_id()]()
