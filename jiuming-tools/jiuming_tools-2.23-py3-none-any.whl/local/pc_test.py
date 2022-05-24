import subprocess

import click
import speedtest


def testDisk(data_gb_size=2):
    """
     测试磁盘性能
    """
    # 块数量 =  data_size / 4k
    count = (data_gb_size * 1024 * 1024) / 4
    click.echo("测试写入速度中。。。。。。")
    click.echo(subprocess.getoutput('time dd if=/dev/zero of=./disk.test bs=4k count=%d' % count))
    click.echo("测试读取速度中。。。。。。")
    click.echo(subprocess.getoutput('time dd if=./disk.test of=/dev/null bs=4k'))
    click.echo(subprocess.getoutput('rm -rf ./disk.test'))
    click.echo("清理测试文件!完毕")


def testNetwork(threads=None):
    """
    测试网络速度
     参考地址: https://github.com/sivel/speedtest-cli/wiki
     results:格式{'download': 232349170.81585404, 'upload': 259741471.54632077, 'ping': 6.161, 'server': {'url': 'http://speedtest1.online.sh.cn:8080/speedtest/upload.php', 'lat': '31.2000', 'lon': '121.5000', 'name': 'Shanghai', 'country': 'China', 'cc': 'CN', 'sponsor': 'China Telecom', 'id': '3633', 'host': 'speedtest1.online.sh.cn:8080', 'd': 19.64397374170924, 'latency': 6.161}, 'timestamp': '2020-09-09T07:38:45.106069Z', 'bytes_sent': 151519232, 'bytes_received': 290975976, 'share': None, 'client': {'ip': '116.228.238.186', 'lat': '31.0449', 'lon': '121.4012', 'isp': 'China Telecom Shanghai', 'isprating': '3.7', 'rating': '0', 'ispdlavg': '0', 'ispulavg': '0', 'loggedin': '0', 'country': 'CN'}}
    """
    click.echo("speedtest测试网速中。。。。。。")
    servers = []
    s = speedtest.Speedtest()
    s.get_servers(servers)
    s.get_best_server()
    s.download(threads=threads)
    s.upload(threads=threads)
    results = s.results
    downloadMbits = float(results.download / 1000.0 / 1000.0)
    uploadMbits = float(results.upload / 1000.0 / 1000.0)
    click.echo('服务器名称: %(sponsor)s (%(name)s)\n距离:%(d)0.2f km\n延迟:%(latency)s ms' % results.server)
    click.echo('下载带宽: %0.2f Mbit/s\n下载速度: %0.2f MB/s' % (downloadMbits, downloadMbits / 8))
    click.echo('上传带宽: %0.2f Mbit/s\n上传速度: %0.2f MB/s' % (uploadMbits, uploadMbits / 8))
    click.echo('测速结果图片地址: %s' % results.share())
