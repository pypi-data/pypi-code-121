# -*- coding: utf-8 -*-
# @Author	: starview.brotherbaby
# @Date		: 2020-09-08 22:59:41 
# @Last Modified by:   starview.brotherbaby
# @Last Modified time: 2020-09-08 22:59:41
# Thanks for your comments!

from IPy import IP

def reload_white_ip_list(conf):
    whiltelist = {}
    if not conf:
        return whiltelist
    ips = conf.get('whitelist')
    if not ips:
        return whiltelist
    for ip in ips:
        ipx = IP(ip)
        for x in ipx:
            whiltelist[str(x)] = True
    return whiltelist

def is_rejected_by_white_list(whitelist, ip):
    if whitelist and ip in whitelist:
        return False
    return True
