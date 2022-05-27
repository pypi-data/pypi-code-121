# -*- coding: utf-8 -*-

import os
import datetime
import socket
import time
import psutil
import json
import requests
from influxdb import InfluxDBClient
from loguru import logger

from monitors.monitor_set import Settings as ST
from monitors.monitor_pid import get_process_id

client = InfluxDBClient(host=ST.host, port=ST.port, username=ST.username, password=ST.password, database=ST.database)


def grafana_tools():
    """
    创建 grafana_dashboards
    :return:grafana_dashboards_url
    """
    url = "http://{}:3000/api/dashboards/db".format(ST.host)

    payload = "{\"dashboard\":{\"annotations\":{\"list\":[{\"builtIn\":1,\"datasource\":\"-- Grafana --\",\"enable\":true," \
              "\"hide\":true,\"iconColor\":\"rgba(0, 211, 255, 1)\",\"name\":\"Annotations & Alerts\"," \
              "\"type\":\"dashboard\"}]},\"editable\":true,\"gnetId\":null,\"graphTooltip\":0,\"id\":null,\"links\":[]," \
              "\"panels\":[{\"cacheTimeout\":null,\"colorBackground\":false,\"colorValue\":true,\"colors\":[\"rgba(50, 172, " \
              "45, 0.97)\",\"rgba(237, 129, 40, 0.89)\",\"rgba(245, 54, 54, 0.9)\"],\"datasource\":\"InfluxDB\"," \
              "\"fieldConfig\":{\"defaults\":{\"custom\":{}},\"overrides\":[]},\"format\":\"none\",\"gauge\":{" \
              "\"maxValue\":100,\"minValue\":0,\"show\":true,\"thresholdLabels\":false,\"thresholdMarkers\":false}," \
              "\"gridPos\":{\"h\":8,\"w\":8,\"x\":0,\"y\":0},\"id\":3,\"interval\":null,\"links\":[],\"mappingType\":1," \
              "\"mappingTypes\":[{\"name\":\"value to text\",\"value\":1},{\"name\":\"range to text\",\"value\":2}]," \
              "\"maxDataPoints\":100,\"nullPointMode\":\"connected\",\"nullText\":null,\"postfix\":\"%\"," \
              "\"postfixFontSize\":\"80%\",\"prefix\":\"\",\"prefixFontSize\":\"50%\",\"rangeMaps\":[{\"from\":\"null\"," \
              "\"text\":\"N/A\",\"to\":\"null\"}],\"sparkline\":{\"fillColor\":\"rgba(31, 118, 189, 0.18)\",\"full\":true," \
              "\"lineColor\":\"rgb(31, 120, 193)\",\"show\":false},\"tableColumn\":\"\",\"targets\":[{\"alias\":\"CPU\"," \
              "\"dsType\":\"influxdb\",\"groupBy\":[],\"measurement\":\"cpu_info\",\"policy\":\"default\"," \
              "\"refId\":\"A\",\"resultFormat\":\"time_series\",\"select\":[[{\"params\":[\"percent\"]," \
              "\"type\":\"field\"}]],\"tags\":[]}],\"thresholds\":\"50,80\",\"title\":\"CPU Usage %\"," \
              "\"type\":\"singlestat\",\"valueFontSize\":\"80%\",\"valueMaps\":[{\"op\":\"=\",\"text\":\"N/A\"," \
              "\"value\":\"null\"}],\"valueName\":\"current\"},{\"cacheTimeout\":null,\"colorBackground\":false," \
              "\"colorValue\":true,\"colors\":[\"rgba(50, 172, 45, 0.97)\",\"rgba(237, 129, 40, 0.89)\",\"rgba(245, 54, 54, " \
              "0.9)\"],\"datasource\":\"InfluxDB\",\"fieldConfig\":{\"defaults\":{\"custom\":{}},\"overrides\":[]}," \
              "\"format\":\"none\",\"gauge\":{\"maxValue\":100,\"minValue\":0,\"show\":true,\"thresholdLabels\":false," \
              "\"thresholdMarkers\":false},\"gridPos\":{\"h\":8,\"w\":8,\"x\":8,\"y\":0},\"id\":4,\"interval\":null," \
              "\"links\":[],\"mappingType\":1,\"mappingTypes\":[{\"name\":\"value to text\",\"value\":1},{\"name\":\"range " \
              "to text\",\"value\":2}],\"maxDataPoints\":100,\"nullPointMode\":\"connected\",\"nullText\":null," \
              "\"postfix\":\"%\",\"postfixFontSize\":\"80%\",\"prefix\":\"\",\"prefixFontSize\":\"50%\",\"rangeMaps\":[{" \
              "\"from\":\"null\",\"text\":\"N/A\",\"to\":\"null\"}],\"sparkline\":{\"fillColor\":\"rgba(31, 118, 189, " \
              "0.18)\",\"full\":true,\"lineColor\":\"rgb(31, 120, 193)\",\"show\":false},\"tableColumn\":\"\",\"targets\":[" \
              "{\"alias\":\"CPU\",\"dsType\":\"influxdb\",\"groupBy\":[],\"measurement\":\"memory_info\"," \
              "\"policy\":\"default\",\"refId\":\"A\",\"resultFormat\":\"time_series\",\"select\":[[{\"params\":[" \
              "\"mem_percent\"],\"type\":\"field\"}]],\"tags\":[]}],\"thresholds\":\"50,80\",\"title\":\"Memory Usage %\"," \
              "\"type\":\"singlestat\",\"valueFontSize\":\"80%\",\"valueMaps\":[{\"op\":\"=\",\"text\":\"N/A\"," \
              "\"value\":\"null\"}],\"valueName\":\"current\"},{\"cacheTimeout\":null,\"colorBackground\":false," \
              "\"colorValue\":true,\"colors\":[\"rgba(50, 172, 45, 0.97)\",\"rgba(237, 129, 40, 0.89)\",\"rgba(245, 54, 54, " \
              "0.9)\"],\"datasource\":\"InfluxDB\",\"fieldConfig\":{\"defaults\":{\"custom\":{}},\"overrides\":[]}," \
              "\"format\":\"none\",\"gauge\":{\"maxValue\":100,\"minValue\":0,\"show\":true,\"thresholdLabels\":false," \
              "\"thresholdMarkers\":false},\"gridPos\":{\"h\":8,\"w\":8,\"x\":16,\"y\":0},\"id\":5,\"interval\":null," \
              "\"links\":[],\"mappingType\":1,\"mappingTypes\":[{\"name\":\"value to text\",\"value\":1},{\"name\":\"range " \
              "to text\",\"value\":2}],\"maxDataPoints\":100,\"nullPointMode\":\"connected\",\"nullText\":null," \
              "\"postfix\":\"%\",\"postfixFontSize\":\"80%\",\"prefix\":\"\",\"prefixFontSize\":\"50%\",\"rangeMaps\":[{" \
              "\"from\":\"null\",\"text\":\"N/A\",\"to\":\"null\"}],\"sparkline\":{\"fillColor\":\"rgba(31, 118, 189, " \
              "0.18)\",\"full\":true,\"lineColor\":\"rgb(31, 120, 193)\",\"show\":false},\"tableColumn\":\"\",\"targets\":[" \
              "{\"alias\":\"CPU\",\"dsType\":\"influxdb\",\"groupBy\":[],\"measurement\":\"disk_info\"," \
              "\"policy\":\"default\",\"refId\":\"A\",\"resultFormat\":\"time_series\",\"select\":[[{\"params\":[" \
              "\"disk_percent\"],\"type\":\"field\"}]],\"tags\":[]}],\"thresholds\":\"50,80\",\"title\":\"Disk Usage %\"," \
              "\"type\":\"singlestat\",\"valueFontSize\":\"80%\",\"valueMaps\":[{\"op\":\"=\",\"text\":\"N/A\"," \
              "\"value\":\"null\"}],\"valueName\":\"current\"},{\"aliasColors\":{},\"bars\":false,\"dashLength\":10," \
              "\"dashes\":false,\"datasource\":\"InfluxDB\",\"description\":\"My Computer's CPU/Disk/Memory usage " \
              "percent\",\"fieldConfig\":{\"defaults\":{\"custom\":{}},\"overrides\":[]},\"fill\":1,\"fillGradient\":0," \
              "\"gridPos\":{\"h\":11,\"w\":24,\"x\":0,\"y\":8},\"hiddenSeries\":false,\"id\":2,\"legend\":{\"avg\":false," \
              "\"current\":false,\"max\":false,\"min\":false,\"show\":true,\"total\":false,\"values\":false}," \
              "\"lines\":true,\"linewidth\":1,\"links\":[],\"nullPointMode\":\"null\",\"options\":{" \
              "\"alertThreshold\":true},\"percentage\":false,\"pluginVersion\":\"7.3.2\",\"pointradius\":5," \
              "\"points\":false,\"renderer\":\"flot\",\"seriesOverrides\":[],\"spaceLength\":10,\"stack\":false," \
              "\"steppedLine\":false,\"targets\":[{\"alias\":\"cpu usage\",\"dsType\":\"influxdb\",\"groupBy\":[]," \
              "\"hide\":false,\"measurement\":\"cpu_info\",\"orderByTime\":\"ASC\",\"policy\":\"new_policy\"," \
              "\"query\":\"SELECT \\\"percent\\\" FROM \\\"cpu_info\\\" WHERE $timeFilter\",\"rawQuery\":true," \
              "\"refId\":\"A\",\"resultFormat\":\"time_series\",\"select\":[[{\"params\":[\"percent\"]," \
              "\"type\":\"field\"}]],\"tags\":[]},{\"alias\":\"disk usage\",\"dsType\":\"influxdb\",\"groupBy\":[]," \
              "\"measurement\":\"disk_info\",\"orderByTime\":\"ASC\",\"policy\":\"default\",\"refId\":\"B\"," \
              "\"resultFormat\":\"time_series\",\"select\":[[{\"params\":[\"disk_percent\"],\"type\":\"field\"}]]," \
              "\"tags\":[]},{\"alias\":\"mem usage\",\"dsType\":\"influxdb\",\"groupBy\":[]," \
              "\"measurement\":\"memory_info\",\"orderByTime\":\"ASC\",\"policy\":\"default\",\"refId\":\"C\"," \
              "\"resultFormat\":\"time_series\",\"select\":[[{\"params\":[\"mem_percent\"],\"type\":\"field\"}]]," \
              "\"tags\":[]}],\"thresholds\":[],\"timeFrom\":null,\"timeRegions\":[],\"timeShift\":null,\"title\":\"My " \
              "Computer Info\",\"tooltip\":{\"shared\":true,\"sort\":0,\"value_type\":\"individual\"},\"type\":\"graph\"," \
              "\"xaxis\":{\"buckets\":null,\"mode\":\"time\",\"name\":null,\"show\":true,\"values\":[]},\"yaxes\":[{" \
              "\"format\":\"short\",\"label\":\"Usage %\",\"logBase\":1,\"max\":\"100\",\"min\":\"0\",\"show\":true}," \
              "{\"format\":\"short\",\"label\":null,\"logBase\":1,\"max\":null,\"min\":null,\"show\":false}],\"yaxis\":{" \
              "\"align\":false,\"alignLevel\":null}},{\"columns\":[],\"datasource\":null,\"fieldConfig\":{\"defaults\":{" \
              "\"custom\":{}},\"overrides\":[]},\"filterNull\":false,\"fontSize\":\"100%\",\"gridPos\":{\"h\":7,\"w\":24," \
              "\"x\":0,\"y\":19},\"id\":6,\"links\":[],\"pageSize\":null,\"scroll\":true,\"showHeader\":true," \
              "\"sort\":{\"col\":0,\"desc\":true},\"styles\":[{\"align\":\"auto\",\"dateFormat\":\"YYYY-MM-DD HH:mm:ss\"," \
              "\"pattern\":\"Time\",\"type\":\"date\"},{\"align\":\"auto\",\"colorMode\":null,\"colors\":[\"rgba(245, 54, " \
              "54, 0.9)\",\"rgba(237, 129, 40, 0.89)\",\"rgba(50, 172, 45, 0.97)\"],\"decimals\":2,\"pattern\":\"/.*/\"," \
              "\"thresholds\":[\"\"],\"type\":\"number\",\"unit\":\"short\"}],\"targets\":[{\"dsType\":\"influxdb\"," \
              "\"groupBy\":[],\"measurement\":\"network_info\",\"policy\":\"default\",\"refId\":\"A\"," \
              "\"resultFormat\":\"time_series\",\"select\":[[{\"params\":[\"bytes_sent\"],\"type\":\"field\"},{\"params\":[" \
              "\"Sent\"],\"type\":\"alias\"}],[{\"params\":[\"bytes_recv\"],\"type\":\"field\"},{\"params\":[\"Receive\"]," \
              "\"type\":\"alias\"}]],\"tags\":[]}],\"timeFrom\":\"5m\",\"title\":\"Network Health\"," \
              "\"transform\":\"timeseries_to_columns\",\"type\":\"table-old\"}],\"refresh\":\"5s\",\"schemaVersion\":26," \
              "\"style\":\"dark\",\"tags\":[],\"templating\":{\"list\":[]},\"time\":{\"from\":\"now-15m\",\"to\":\"now\"}," \
              "\"timepicker\":{\"nowDelay\":\"\",\"refresh_intervals\":[\"5s\",\"10s\",\"30s\",\"1m\",\"5m\",\"10m\"]," \
              "\"time_options\":[\"5m\",\"15m\",\"1h\",\"6h\",\"12h\",\"24h\",\"2d\",\"7d\",\"30d\"]}," \
              "\"timezone\":\"browser\",\"title\":\"yts_monitor\",\"version\":2,\"uid\":\"\"},\"overwrite\":true," \
              "\"inputs\":[],\"folderId\":0} ".replace('cpu_info', '{}_cpu_info'.format(ST.table)).replace(
        'memory_info',
        '{}_memory_info'.format(
            ST.table)).replace(
        'disk_info', '{}_disk_info'.format(ST.table)).replace('network_info',
                                                              '{}_network_info'.format(ST.table)).replace(
        'yts_monitor', '{}_yts_monitor'.format(ST.table))

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {}'.format(ST.apikey)}

    response = requests.request("POST", url, headers=headers, data=payload)
    grafana_dashboards_path = json.loads(response.text)['url']
    grafana_dashboards_url = "http://{}:3000{}".format(ST.host, grafana_dashboards_path)
    return grafana_dashboards_url


def monitor(process_id):
    """
    设定监控时间  默认1天
    :param process_id:
    :return:
    """

    try:
        CYCLE_TIME = datetime.timedelta(weeks=0, days=ST.monitor_duration, hours=00, minutes=0, seconds=5,
                                        microseconds=0,
                                        milliseconds=0)
        start_time = datetime.datetime.today()
        title = '时间' + "\t			  " + '运行状态' + "\t" + 'CPU百分比' + " " + '内存利用率' + "\t" + '虚拟内存' + "\t" + '实际使用内存' + "\t" + '网络发送包' + " " + '网络接受包' + "\n"
        logger.info(title)
        if psutil.pid_exists(process_id):
            p = psutil.Process(process_id)
            pName = p.name()
            logName = pName + "_" + str(process_id) + "_stress_monitoring_record.log"
            logger.info(logName + '\n')
            if not os.path.exists(ST.monitor_log_path):
                os.mkdir(ST.monitor_log_path)
            logfile = open(ST.monitor_log_path + '/' + logName, "a")
        else:
            logger.warning("pid is not exists please enter true pid!!!")
            return
        wTime = ST.refresh_interval

        while True:
            if datetime.datetime.today() - start_time > CYCLE_TIME:
                break
            recTime = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))

            if psutil.pid_exists(process_id):
                try:
                    status = p.status()
                    pCpu = u'%.2f' % (p.cpu_percent(interval=1))
                    mem = u'%.4f' % (p.memory_percent())
                    vmm = p.memory_info().vms
                    mm = p.memory_info().rss
                    net_sent = psutil.net_io_counters().packets_sent
                    net_recv = psutil.net_io_counters().packets_recv
                    monitor_content = str(recTime) + "\t" + str(status) + "\t" + str(pCpu) + '%' + "\t" + str(
                        mem) + '%' + "\t" + str(
                        vmm) + "\t" + str(mm) + "\t" + str(net_sent) + "\t" + str(net_recv) + "\n"
                    logger.info(monitor_content)
                    logfile.flush()
                    logfile.write(monitor_content)
                except Exception as e:
                    logger.error('监控结束：{}'.format(e))
                    pass
            else:
                monitor_content = str(datetime.datetime.today()) + "\t" + str(
                    process_id) + "  is not running!!!!!!!!!\n"
                logger.info(monitor_content)
                logfile.flush()
                logfile.write(monitor_content)
                break

            time.sleep(wTime)

        logfile.close()
    except ProcessLookupError as e:
        logger.info('监控结束：{}'.format(e))
        pass


def monitor_start(name):
    try:
        pid = int(get_process_id(process_name=name))
        monitor(pid)

    except TypeError as E:
        logger.error('应用未启动 或 无此进程：{}'.format(E))


def get_host_ip():
    """
    获取本机ip
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(('8.8.8.8', 80))
        host_ip = s.getsockname()[0]
    finally:
        s.close()

    return host_ip


def monitor_view():
    """
    设定监控时间  默认1天
    :return:
    """

    try:
        CYCLE_TIME = datetime.timedelta(weeks=0, days=ST.monitor_duration, hours=00, minutes=0, seconds=5,
                                        microseconds=0,
                                        milliseconds=0)
        start_time = datetime.datetime.today()
        ip = get_host_ip()

        wTime = ST.refresh_interval

        while True:
            if datetime.datetime.today() - start_time > CYCLE_TIME:
                break

            try:
                cpu_info = [
                    {
                        "measurement": "{}_cpu_info".format(ST.table),
                        "tags": {
                            "host": ip
                        },
                        "fields": {
                            "percent": psutil.cpu_percent(0)
                        }
                    }
                ]
                memory_info = [
                    {
                        "measurement": "{}_memory_info".format(ST.table),
                        "tags": {
                            "host": ip
                        },
                        "fields": {
                            "mem_percent": psutil.virtual_memory().percent,
                            "mem_used": psutil.virtual_memory().used,
                            "mem_free": psutil.virtual_memory().free,
                        }
                    }
                ]
                disk_info = [
                    {
                        "measurement": "{}_disk_info".format(ST.table),
                        "tags": {
                            "host": ip
                        },
                        "fields": {
                            "disk_used": psutil.disk_usage('/').used,
                            "disk_free": psutil.disk_usage('/').free,
                            "disk_percent": psutil.disk_usage('/').percent,
                        }
                    }
                ]
                network_info = [
                    {
                        "measurement": "{}_network_info".format(ST.table),
                        "tags": {
                            "host": ip
                        },
                        "fields": {
                            "bytes_sent": psutil.net_io_counters().packets_sent,
                            "bytes_recv": psutil.net_io_counters().packets_recv,
                        }
                    }
                ]
                client.write_points(cpu_info)
                client.write_points(memory_info)
                client.write_points(disk_info)
                client.write_points(network_info)

            except Exception as e:
                logger.info('End of monitoring：{}'.format(e))
                pass

            time.sleep(wTime)

    except KeyboardInterrupt:
        logger.warning('------------------ 监控服务已停止！-----------------')
        pass


def monitor_on():
    try:
        logger.info('Grafana url：{}'.format(grafana_tools()))
        logger.info('-------------- 监控服务运行中，请勿关闭！--------------')
        monitor_view()

    except Exception as E:
        logger.error('监控服务运行异常：{}'.format(E))
