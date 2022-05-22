import datetime
import json
import re
import sys

import boto3

def main():
    profile, region, verbose, color_flag, help_flag = parse_args()
    if help_flag:
        print_help()
        return

    session = boto3.session.Session(profile_name = profile, region_name = region)

    ec2_client = session.client("ec2")

    vpcs = fetch_vpc_list(ec2_client)
    subnets = fetch_subnet_list(ec2_client)
    if verbose > 0:
        nics = fetch_nic_list(ec2_client)
    else:
        nics = []
    segments = build_segments(vpcs, subnets, nics)

    if color_flag == 0 and sys.stdout.isatty():
        color_flag = 1
    for vpc_segment in segments:
        lines = build_table(vpc_segment, verbose)
        for line in lines:
            if color_flag > 0:
                line = to_colorful(line)
            print(line)
        print()

def print_help():
    help_str = """
aws-list-subnets [OPTIONS]

OPTION:
    --help
    --profile <AWS_PROFILE_NAME>
    --region <AWS_REGION_NAME>
    -v
    --simple
    --color
""".strip()
    print(help_str)

def parse_args():
    help_flag = False
    profile = None
    region = None
    verbose = 1
    color_flag = 0
    argCount = len(sys.argv)
    i = 1
    while i < argCount:
        a = sys.argv[i]
        i = i + 1
        if a == "--profile":
            if i >= argCount:
                raise Exception(f"Option parameter not found: {a}")
            profile = sys.argv[i]
            i = i + 1
        elif a == "--region":
            if i >= argCount:
                raise Exception(f"Option parameter not found: {a}")
            region = sys.argv[i]
            i = i + 1
        elif a == "--simple":
            verbose = 0
        elif a == "--help":
            help_flag = True
        elif a == "--color":
            color_flag = 1
        elif a == "-v":
            verbose = 2
        else:
            raise Exception(f"Unknown parameter: {a}")
    return (profile, region, verbose, color_flag, help_flag)

class Segment:
    def __init__(self, address, len_prefix, info):
        self.address = address
        self.len_prefix = len_prefix
        self.info = info
        self.nics = None
        self.subsegments = None

    def cidr(self):
        return ip_int_to_str(self.address) + "/" + str(self.len_prefix)

    def includes(self, address):
        segment_size = 1 << (32 - self.len_prefix)
        if address >= self.address and address < self.address + segment_size:
            return True
        else:
            return False

    def max_depth(self):
        if self.subsegments is None:
            return 0
        result = 0
        for sub in self.subsegments:
            if sub is not None:
                d = sub.max_depth() + 1
                result = max(result, d)
        return result

    def add_segment(self, segment):
        if segment.len_prefix <= self.len_prefix:
            raise Exception()
        subsegment_size = 1 << (31 - self.len_prefix)
        if self.subsegments is None:
            self.subsegments = [None, None]
        if segment.len_prefix == self.len_prefix + 1:
            if segment.address == self.address:
                self.subsegments[0] = segment
            elif segment.address == self.address + subsegment_size:
                self.subsegments[1] = segment
            else:
                raise Exception()
            return
        index = (segment.address - self.address) // subsegment_size
        if index < 0:
            raise Exception()
        if index >= 2:
            raise Exception()
        if self.subsegments[index] is None:
            self.subsegments[index] = Segment(self.address + subsegment_size * index, self.len_prefix + 1, None)
        self.subsegments[index].add_segment(segment)

    def get_subsegment(self, index):
        subsegment_size = 1 << (31 - self.len_prefix)
        if self.subsegments is None:
            self.subsegments = [None, None]
        if self.subsegments[index] == None:
            self.subsegments[index] = Segment(self.address + subsegment_size * index, self.len_prefix + 1, None)
        return self.subsegments[index]

    def add_nic(self, ip, info1, info2):
        if self.nics is None:
            self.nics = []
        self.nics.append((ip, info1, info2))

    def sorted_nics(self):
        return sorted(self.nics, key=lambda elem: elem[0])

def cidr_to_address_and_len_prefix(cidr):
    ss = cidr.split("/")
    ips = ss[0].split(".")
    address = int(ips[0]) * (256 ** 3) + int(ips[1]) * (256 ** 2) + int(ips[2]) * 256 + int(ips[3])
    len_prefix = int(ss[1])
    return (address, len_prefix)

def ip_str_to_int(ip):
    ips = ip.split(".")
    return int(ips[0]) * (256 ** 3) + int(ips[1]) * (256 ** 2) + int(ips[2]) * 256 + int(ips[3])

def ip_int_to_str(ip):
    ips = []
    ips.append(ip // (256 ** 3))
    ips.append(ip // (256 ** 2) % 256)
    ips.append(ip // 256 % 256)
    ips.append(ip % 256)
    return ".".join([str(i) for i in ips])

def fetch_vpc_list(ec2_client):
    res = ec2_client.describe_vpcs()
    vpcs = []
    while True:
        for elem in res["Vpcs"]:
            cidr = elem["CidrBlock"]
            vpcid = elem["VpcId"]
            name = "-"
            if "Tags" in elem:
                for tag in elem["Tags"]:
                    if tag["Key"] == "Name":
                        name = tag["Value"]
            vpcs.append({"cidr": cidr, "vpcId": vpcid, "name": name})
        if "NextToken" not in res:
            break
        res = ec2_client.describe_vpcs(NextToken=res["NextToken"])
    return vpcs

def fetch_subnet_list(ec2_client):
    res = ec2_client.describe_subnets()
    vpcs = []
    while True:
        for elem in res["Subnets"]:
            cidr = elem["CidrBlock"]
            az = elem["AvailabilityZone"]
            vpcid = elem["VpcId"]
            subnetid = elem["SubnetId"]
            name = "-"
            if "Tags" in elem:
                for tag in elem["Tags"]:
                    if tag["Key"] == "Name":
                        name = tag["Value"]
            vpcs.append({"cidr": cidr, "vpcId": vpcid, "subnetId": subnetid, "az": az, "name": name})
        if "NextToken" not in res:
            break
        res = ec2_client.describe_subnets(NextToken=res["NextToken"])
    return vpcs

def fetch_nic_list(ec2_client):
    res = ec2_client.describe_network_interfaces()
    nics = []
    while True:
        for elem in res["NetworkInterfaces"]:
            subnetid = elem["SubnetId"]
            ip = elem["PrivateIpAddress"]
            elem2 = elem.copy()
            del elem2["AvailabilityZone"]
            del elem2["PrivateIpAddress"]
            del elem2["SubnetId"]
            del elem2["VpcId"]
            info1 = nic_info_to_str(elem2)
            info2 = json.dumps(to_json_safe(elem2))
            nics.append({"subnetId": subnetid, "ip": ip, "info1": info1, "info2": info2})
        if "NextToken" not in res:
            break
        res = ec2_client.describe_network_interfaces(NextToken=res["NextToken"])
    return nics

def nic_info_to_str(nic):
    info = ""
    if "Attachment" in nic and "InstanceId" in nic["Attachment"]:
        instanceId = nic["Attachment"]["InstanceId"]
        info = info + instanceId + " "
    if "RequesterId" in nic:
        requester = nic["RequesterId"]
        if requester.startswith("amazon-"):
            info = info + requester + " "
    if info == "" and "Description" in nic:
        info = info + nic["Description"] + " "
    return info

def build_segments(vpcs, subnets, nics):
    segments = []
    subnet_map = {}

    for vpc in vpcs:
        vpc_address, vpc_len_prefix = cidr_to_address_and_len_prefix(vpc["cidr"])
        vpc_info = f"{vpc['cidr']} {vpc['vpcId']} {vpc['name']}"
        vpc_segment = Segment(vpc_address, vpc_len_prefix, vpc_info)
        segments.append(vpc_segment)
        for subnet in subnets:
            if subnet["vpcId"] != vpc["vpcId"]:
                continue
            subnet_address, subnet_len_prefix = cidr_to_address_and_len_prefix(subnet["cidr"])
            subnet_info = f"{subnet['cidr']} {subnet['subnetId']} {subnet['az']} {subnet['name']}"
            subnet_segment = Segment(subnet_address, subnet_len_prefix, subnet_info)
            vpc_segment.add_segment(subnet_segment)
            subnet_map[subnet["subnetId"]] = subnet_segment

    for nic in nics:
        subnet_map[nic["subnetId"]].add_nic(ip_str_to_int(nic["ip"]), nic["info1"], nic["info2"])

    return segments

def build_table(vpc_segment, verbose):
    lines = []
    max_depth = vpc_segment.max_depth()
    lines.extend(build_segment_table(vpc_segment, verbose, max_depth))
    return lines

def build_segment_table(segment, verbose, rest_depth):
    lines = []

    separator = "----------------------------------------"

    border1 = "+"
    for i in range(rest_depth + 1):
        border1 = border1 + "----"
    border1 = border1 + separator

    border2 = " "
    for i in range(1):
        border2 = border2 + "   +"
    for i in range(rest_depth):
        border2 = border2 + "----"
    border2 = border2 + separator

    border3 = "+"
    for i in range(1):
        border3 = border3 + "---+"
    for i in range(rest_depth):
        border3 = border3 + "----"
    border3 = border3 + separator

    if segment.info:
        lines.append(border1)
        lines.append("| " + segment.info)
        sub_prefix1 = "|   "
        sub_prefix2 = "|   "
        sub_prefix3 = "+---"
        if segment.nics:
            for line in build_nics_list(segment, verbose):
                lines.append("|   " + line)
    else:
        sub_prefix1 = "+---"
        sub_prefix2 = "|   "
        sub_prefix3 = "+---"
    if segment.subsegments:
        sub_lines = merge_lines2(
            build_segment_table(segment.get_subsegment(0), verbose, rest_depth - 1),
            build_segment_table(segment.get_subsegment(1), verbose, rest_depth - 1))
        lines.append(sub_prefix1 + sub_lines[0])
        for i in range(len(sub_lines) - 2):
            lines.append(sub_prefix2 + sub_lines[i + 1])
        lines.append(sub_prefix3 + sub_lines[len(sub_lines) - 1])
    else:
        lines.append(border1)

    if segment.info is None and segment.subsegments is None:
        cidr = segment.cidr()
        lines.append(f"| {cidr} NotAllocated")
        lines.append(border1)

    return lines

def build_nics_list(segment, verbose):
    lines = []
    for nic in segment.sorted_nics():
        ip = ip_int_to_str(nic[0])
        info1 = nic[1]
        info2 = nic[2]
        if verbose >= 2:
            lines.append(f"{ip} {info1} {info2}")
        elif verbose >= 1:
            lines.append(f"{ip} {info1}")
    return lines

def merge_lines(lines_list):
    if len(lines_list) == 1:
        return lines_list[0]
    result = merge_lines2(lines_list[0], lines_list[1])
    for i in range(len(lines_list) - 2):
        result = merge_lines2(result, lines_list[i + 2])
    return result

def merge_lines2(lines1, lines2):
    len1 = len(lines1)
    s1 = lines1[len1 - 1]
    s2 = lines2[0]
    result = ""
    for i in range(len(s1)):
        if s1[i] == '+' or s2[i] == '+':
            result = result + '+'
        elif s1[i] == '-' or s2[i] == '-':
            result = result + '-'
        else:
            result = result + ' '
    lines = []
    lines.extend(lines1[0:len1 - 1])
    lines.append(result)
    lines.extend(lines2[1:])
    return lines

def to_json_safe(obj):
    if isinstance(obj, dict):
        obj2 = {}
        for key, value in obj.items():
            obj2[key] = to_json_safe(value)
    elif isinstance(obj, list):
        obj2 = []
        for value in obj:
            obj2.append(to_json_safe(value))
    elif isinstance(obj, datetime.datetime):
        obj2 = obj.isoformat()
    else:
        obj2 = obj
    return obj2

def to_colorful(line):
    ip_start = '\x1b[32m'
    line_start = '\x1b[90m'
    reset = '\x1b[0m'
    line = re.sub(r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}(/[0-9]{0,2})?)', ip_start + r'\1' + reset, line)
    if line.find('--') >= 0:
        line = line_start + line + reset
    else:
        line = re.sub(r'\A(|[ |]+)', line_start + r'\1' + reset, line)
    return line

if __name__ == "__main__":
    main()

