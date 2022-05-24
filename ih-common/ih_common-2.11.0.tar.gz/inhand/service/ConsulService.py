import consul
import json
import uuid
import logging


class ConsulService(object):
    def __init__(self, host, port):
        '''初始化，连接consul服务器'''
        self._consul = consul.Consul(host, port)

    def registerAPI(self, local_ip, port, app_name, app_id, prefix, app_group, instance_info, apis, protocol='http',
                    health_entry='/health'):
        tags = []

        tags.append("group={}".format(app_group))
        tags.append("secure=false")
        tags.append("{}.enable=true".format(prefix))
        tags.append("{}.http.services.{}.loadbalancer.server.weight=1".format(prefix, app_name))
        tags.append("{}.http.services.{}.loadbalancer.passHostHeader=true".format(prefix, app_name))
        tags.append("{}.instance={}".format(app_id, json.dumps(instance_info)))

        for api in apis:
            uid = str(uuid.uuid4())
            suid = ''.join(uid.split("-"))
            route_prefix = "{}.http.routers.{}".format(prefix, suid)
            tags.append("{}.rule=Path(`{}`) && Method(`{}`)".format(route_prefix, api['path'], api['method']))
            key = None
            if 'scope' in api.keys():
                key = 'scope'
            elif 'scopes' in api.keys():
                key = 'scopes'
            if key is not None:
                tags.append("{}.middlewares=nezha@internal".format(route_prefix))
                tags.extend(["{}.metadata.nezha.scopes={}".format(route_prefix, scope) for scope in api[key].split(',')])

        logging.info("Tags:" + str(tags))

        self.registerService(app_name, app_id, local_ip, port, tags=tags, protocol=protocol,
                             health_entry=health_entry)

        res = self.getService(app_name)
        logging.info(str(res))

    def registerService(self, name, service_id, host, port, tags=None, protocol='http', health_entry='/health'):
        tags = tags or []
        url = "{}://{}:{}{}".format(protocol, host, port, health_entry)
        logging.debug("Health Url: {}".format(url))
        # 注册服务
        self._consul.agent.service.register(
            name=name,
            service_id=service_id,
            address=host,
            port=port,
            tags=tags,
            # 健康检查ip端口，检查时间：5,超时时间：30，注销时间：30s
            check=consul.Check().http(url, "5s", "30s", "30s", None))

    def check(self, host, port, interval, timeout=None, deregister=None, header=None, health_entry='/health',
              protocol='http'):
        return consul.Check.http("{}}://{}:{}{}".format(protocol, host, port, health_entry), interval, timeout,
                                 deregister, header)

    def getService(self, name):
        services = self._consul.agent.services()
        service = services.get(name)
        if not service:
            return None, None
        addr = "{0}:{1}".format(service['Address'], service['Port'])
        return service, addr


if __name__ == '__main__':
    import sys

    sys.path.append('../../')
    from inhand.utilities.Utility import Utility
    ip = Utility.getLocalIP(host="consul",port=8500)
    port = 8500
    api_entries = [
    {
        "desc": "获取老化车信息",
        "path": "/api/v1.0/aging_car/info",
        "method": "GET",
        "scope": "mes:aging:get"
    },
    {
        "desc": "获取老化信息",
        "path": "/api/v1.0/aging/query",
        "method": "GET",
        "scope": "mes:aging:get"
    },
    {
        "desc": "序列号绑定老化车",
        "path": "/api/v1.0/aging/sn_bind",
        "method": "POST",
        "scope": "mes:aging:post"
    },
    {
        "desc": "工单绑定老化车",
        "path": "/api/v1.0/aging/order_bind",
        "method": "POST",
        "scope": "mes:aging:post"
    },
    {
        "desc": "解除序列号绑定老化车",
        "path": "/api/v1.0/aging/clear_bind",
        "method": "POST",
        "scope": "mes:aging:post"
    },
    {
        "desc": "开始老化",
        "path": "/api/v1.0/aging/start",
        "method": "POST",
        "scope": "mes:aging:post"
    },
    {
        "desc": "结束老化",
        "path": "/api/v1.0/aging/end",
        "method": "POST",
        "scope": "mes:aging:post"
    },
    {
        "desc": "验证是否老化",
        "path": "/api/v1.0/aging/check",
        "method": "POST",
        "scope": "mes:aging:get"
    },
    {
        "desc": "获取token",
        "path": "/api/v1.0/get_token",
        "method": "GET",
        "scope": "mes:token:get"
    },
    {
        "desc": "获取token",
        "path": "/api/v1.0/get_token",
        "method": "POST",
        "scope": "mes:token:get"
    },
    {
        "desc": "刷新token",
        "path": "/api/v1.0/refresh_token",
        "method": "GET",
        "scope": "mes:token:get"
    },
    {
        "desc": "根据uid获取token",
        "path": "/api/v1.0/get_token_by_uid",
        "method": "GET",
        "scope": "mes:token:get"
    },
    {
        "desc": "通过用户名密码进行认证",
        "path": "/api/odoo/v3.0/auth",
        "method": "POST",
        "scope": "mes:token:post"
    },
    {
        "desc": "创建员工上线信息",
        "path": "/api/v1.0/record_online_time",
        "method": "GET",
        "scope": "mes:employee-online-records:post"
    },
    {
        "desc": "创建 PCBA 上线记录",
        "path": "/api/v1.0/record_online_time_pcba",
        "method": "GET",
        "scope": "mes:employee-online-records:post"
    },
    {
        "desc": "查询上线记录",
        "path": "/api/v1.0/query_employee_online",
        "method": "GET",
        "scope": "mes:employee-online-records:get"
    },
    {
        "desc": "记录下线",
        "path": "/api/v1.0/record_offline_time",
        "method": "POST",
        "scope": "mes:employee-online-records:post"
    },
    {
        "desc": "记录上线",
        "path": "/api/v1.0/record_online_more_time",
        "method": "POST",
        "scope": "mes:employee-online-records:post"
    },
    {
        "desc": "验证FCT工装是否可以使用",
        "path": "/api/mes/v3.0/notes/equipment-checking",
        "method": "PUT",
        "scope": "mes:equipments:put"
    },
    {
        "desc": "获取设备列表",
        "path": "/api/mes/v3.0/notes/equipments",
        "method": "GET",
        "scope": "mes:equipments:get"
    },
    {
        "desc": "根据设备编号，获取设备信息",
        "path": "/api/mes/v3.0/notes/equipments/{no}",
        "method": "GET",
        "scope": "mes:equipments:get"
    },
    {
        "desc": "创建设备记录",
        "path": "/api/mes/v3.0/notes/equipments",
        "method": "POST",
        "scope": "mes:equipments:post"
    },
    {
        "desc": "查询设备种类",
        "path": "/api/mes/v3.0/notes/equipments-category",
        "method": "GET",
        "scope": "mes:equipments-category:get"
    },
    {
        "desc": "查询项目组列表",
        "path": "/api/mes/v3.0/notes/project-team",
        "method": "GET",
        "scope": "mes:project-team:get"
    },
    {
        "desc": "查询设备保养单列表",
        "path": "/api/mes/v3.0/notes/maintenances",
        "method": "GET",
        "scope": "mes:maintenances:get"
    },
    {
        "desc": "查询设备保养单",
        "path": "/api/mes/v3.0/notes/maintenances/{no}",
        "method": "GET",
        "scope": "mes:maintenances:get"
    },
    {
        "desc": "创建设备保养单",
        "path": "/api/mes/v3.0/notes/maintenances",
        "method": "POST",
        "scope": "mes:maintenances:post"
    },
    {
        "desc": "保存设备保养单",
        "path": "/api/mes/v3.0/notes/maintenances",
        "method": "PUT",
        "scope": "mes:maintenances:put"
    },
    {
        "desc": "获取设备校准单列表",
        "path": "/api/mes/v3.0/notes/calibrates",
        "method": "GET",
        "scope": "mes:calibrates:get"
    },
    {
        "desc": "查询设备校准单",
        "path": "/api/mes/v3.0/notes/calibrates/{no}",
        "method": "GET",
        "scope": "mes:calibrates:get"
    },
    {
        "desc": "创建设备校准单",
        "path": "/api/mes/v3.0/notes/calibrates",
        "method": "POST",
        "scope": "mes:calibrates:post"
    },
    {
        "desc": "保存设备校准单",
        "path": "/api/mes/v3.0/notes/calibrates",
        "method": "PUT",
        "scope": "mes:calibrates:put"
    },
    {
        "desc": "获取设备维修单列表",
        "path": "/api/mes/v3.0/notes/repairorders",
        "method": "GET",
        "scope": "mes:repairorders:get"
    },
    {
        "desc": "查询设备维修单",
        "path": "/api/mes/v3.0/notes/repairorders/{no}",
        "method": "GET",
        "scope": "mes:repairorders:get"
    },
    {
        "desc": "创建设备维修单",
        "path": "/api/mes/v3.0/notes/repairorders",
        "method": "POST",
        "scope": "mes:repairorders:post"
    },
    {
        "desc": "保存设备维修单",
        "path": "/api/mes/v3.0/notes/repairorders",
        "method": "PUT",
        "scope": "mes:repairorders:put"
    },
    {
        "desc": "创建设备借用记录",
        "path": "/api/mes/v3.0/notes/equipments-borrow",
        "method": "POST",
        "scope": "mes:equipments-borrow:post"
    },
    {
        "desc": "归还设备",
        "path": "/api/mes/v3.0/notes/equipments-return",
        "method": "PUT",
        "scope": "mes:equipments-borrow:put"
    },
    {
        "desc": "根据日期和设备型号获取销售订单的发货记录",
        "path": "/api/erp/sales/order",
        "method": "GET",
        "scope": "mes:delivery-records:get"
    },
    {
        "desc": "根据SN获取设备型号和物料号",
        "path": "/api/mes/query_products",
        "method": "GET",
        "scope": "mes:products:get"
    },
    {
        "desc": "根据SN获取工单号",
        "path": "/api/mes/v2.0/notes/products/{sn}",
        "method": "GET",
        "scope": "mes:products:get"
    },
    {
        "desc": "根据出厂编号获取成品信息",
        "path": "/api/mes/v2.0/notes/products",
        "method": "GET",
        "scope": "mes:products:get"
    },
    {
        "desc": "获取所有的工厂信息",
        "path": "/api/v1.0/factory/name",
        "method": "GET",
        "scope": "mes:factory:get"
    },
    {
        "desc": "根据工厂ID获取产线信息",
        "path": "/api/v1.0/line/get_name",
        "method": "GET",
        "scope": "mes:product-lines:get"
    },
    {
        "desc": "根据产线ID获取工位信息",
        "path": "/api/v1.0/station/get_name",
        "method": "GET",
        "scope": "mes:product-stations:get"
    },
    {
        "desc": "根据工厂id查询产线信息",
        "path": "/api/mes/v2.0/notes/work-lines",
        "method": "GET",
        "scope": "mes:product-lines:get"
    },
    {
        "desc": "看板页面接口",
        "path": "/api/v1.0/web_resource",
        "method": "GET",
        "scope": "mes:web-resource:get"
    },
    {
        "desc": "物料追溯页面接口",
        "path": "/api/v1.0/web_retrospect",
        "method": "GET",
        "scope": "mes:web-resource:get"
    },
    {
        "desc": "http代理",
        "path": "/api/v1.0/url_proxy",
        "method": "GET",
        "scope": "mes:url-proxy:get"
    },
    {
        "desc": "获取包装看板数据",
        "path": "/api/mes/v2.0/notes/kanban/packing",
        "method": "GET",
        "scope": "mes:kanban-packing:get"
    },
    {
        "desc": "获取产线看板数据",
        "path": "/api/mes/v2.0/notes/kanban/production",
        "method": "GET",
        "scope": "mes:kanban-production:get"
    },
    {
        "desc": "创建OEM测试记录",
        "path": "/api/mes/v2.0/notes/oem-products",
        "method": "POST",
        "scope": "mes:oem-products:post"
    },
    {
        "desc": "查询OEM测试记录",
        "path": "/api/mes/v2.0/notes/oem-products",
        "method": "GET",
        "scope": "mes:oem-products:get"
    },
    {
        "desc": "查询产品名称变量",
        "path": "/api/mes/v2.0/notes/products/env",
        "method": "GET",
        "scope": "mes:product-env:get"
    },
    {
        "desc": "生成一个盒号",
        "path": "/api/v1.0/box/get_number",
        "method": "GET",
        "scope": "mes:box:post"
    },
    {
        "desc": "生成一个箱号",
        "path": "/api/v1.0/carton/get_number",
        "method": "GET",
        "scope": "mes:carton:post"
    },
    {
        "desc": "将序列号绑定盒号",
        "path": "/api/v1.0/box/set_info",
        "method": "POST",
        "scope": "mes:box-bind:post"
    },
    {
        "desc": "将序列号绑定箱号",
        "path": "/api/v1.0/carton/set_info",
        "method": "POST",
        "scope": "mes:carton-bind:post"
    },
    {
        "desc": "盒号箱号发货",
        "path": "/api/v1.0/box_carton/deliver2",
        "method": "POST",
        "scope": "mes:box-delivery:post"
    },
    {
        "desc": "盒号箱号发货(调拨)",
        "path": "/api/v1.0/box_carton/deliver3",
        "method": "POST",
        "scope": "mes:box-delivery:post"
    },
    {
        "desc": "盒号箱号发货(其他出库)",
        "path": "/api/v1.0/box_carton/deliver4",
        "method": "POST",
        "scope": "mes:box-delivery:post"
    },
    {
        "desc": "获取盒内数量",
        "path": "/api/v1.0/box/total_quantity",
        "method": "POST",
        "scope": "mes:box:get"
    },
    {
        "desc": "获取盒内数量(新)",
        "path": "/api/v1.0/box/total_quantity2",
        "method": "POST",
        "scope": "mes:box:get"
    },
    {
        "desc": "根据pcba序列号查询当前序列号的测试记录",
        "path": "/api/v1.0/pcba/test",
        "method": "GET",
        "scope": "mes:pcbas-test:get"
    },
    {
        "desc": "根据pcba序列号校验是否为最小date_code",
        "path": "/api/v1.0/pcba/check_date_code",
        "method": "POST",
        "scope": "mes:pcbas:post"
    },
    {
        "desc": "根据pcba_sn记录date_code,iccid, module_version",
        "path": "/api/v1.0/pcba/record_date_code",
        "method": "POST",
        "scope": "mes:pcbas:post"
    },
    {
        "desc": "根据pcba_sn记录iccid, module_version",
        "path": "/api/v1.0/pcba/query",
        "method": "POST",
        "scope": "mes:pcbas:post"
    },
    {
        "desc": "根据工单id，pid，获取当前工单当前工序的不同状态的数量",
        "path": "/api/v1.0/procedure/number",
        "method": "GET",
        "scope": "mes:product-test:get"
    },
    {
        "desc": "根据PCBA工单id，pid，获取当前工单当前工序的不同状态的数量",
        "path": "/api/v1.0/pcba_procedure/number",
        "method": "GET",
        "scope": "mes:pcba-test:get"
    },
    {
        "desc": "根据测试组的ID和工单类型获取获取工序的名称",
        "path": "/api/v1.0/procedure/get_name",
        "method": "GET",
        "scope": "mes:procedure-group:get"
    },
    {
        "desc": "根据测试组的ID和工单类型获取获取工序的名称",
        "path": "/api/v1.0/procedure/get_name2",
        "method": "POST",
        "scope": "mes:procedure-group:get"
    },
    {
        "desc": "根据测试组的ID和工单类型获取获取工序的名称",
        "path": "/api/v1.0/procedure/get_name3",
        "method": "POST",
        "scope": "mes:procedure-group:get"
    },
    {
        "desc": "根据测试组的ID和工单类型获取其它工序的名称",
        "path": "/api/v1.0/procedure/get_other_name",
        "method": "POST",
        "scope": "mes:procedure-group:get"
    },
    {
        "desc": "根据测试组的ID和工单类型、工序名称获取获取工序的内容",
        "path": "/api/v1.0/procedure/get_procedure",
        "method": "POST",
        "scope": "mes:procedure-group:get"
    },
    {
        "desc": "根据测试组的ID和工单类型、工序名称,、序列号、工单类型、工单ID获取工序执行结果",
        "path": "/api/v1.0/procedure/precondition",
        "method": "POST",
        "scope": "mes:product-test:get"
    },
    {
        "desc": "创建测试记录",
        "path": "/api/v1.0/products/create",
        "method": "POST",
        "scope": "mes:products:post"
    },
    {
        "desc": "判断设备是否终检通过",
        "path": "/api/v1.0/products/check",
        "method": "POST",
        "scope": "mes:products-check:get"
    },
    {
        "desc": "根据成品序列号校验是否为最小date_code",
        "path": "/api/v1.0/product/check_date_code",
        "method": "POST",
        "scope": "mes:products-check:get"
    },
    {
        "desc": "获取成品测试信息列表",
        "path": "/api/mes/v2.0/products",
        "method": "GET",
        "scope": "mes:products:get"
    },
    {
        "desc": "更新成品测试记录的上传信息",
        "path": "/api/mes/v2.0/product/sync_status/{sn}",
        "method": "PUT",
        "scope": "mes:products:put"
    },
    {
        "desc": "更新成品测试记录的上传信息",
        "path": "/api/mes/v3.0/product/sync_status/{sn}",
        "method": "PUT",
        "scope": "mes:products:put"
    },
    {
        "desc": "创建故指 加密信息记录",
        "path": "/api/mes/v1.0/products/create_gzencryption",
        "method": "POST",
        "scope": "mes:gz-encryption-records:post"
    },
    {
        "desc": "创建故指 加密信息记录2",
        "path": "/api/mes/v1.0/products/create_gzencryption2",
        "method": "POST",
        "scope": "mes:gz-encryption-records:post"
    },
    {
        "desc": "创建故指 加密信息记录 用于桌面自动化上传接口",
        "path": "/api/mes/v3.0/JYL-IH-HD-Product/certs",
        "method": "POST",
        "scope": "mes:gz-encryption-records:post"
    },
    {
        "desc": "查询 加密信息记录 用于检验是否已经上传加密信息",
        "path": "/api/mes/v3.0/gz-encryption/certs/{manuid}",
        "method": "GET",
        "scope": "mes:gz-encryption-records:get"
    },
    {
        "desc": "创建 测试详情记录 用于上传 WIFI测试仪 测试结果",
        "path": "/api/mes/v3.0/test-details",
        "method": "POST",
        "scope": "mes:products-test:post"
    },
    {
        "desc": "创建产线维修记录",
        "path": "/api/v1.0/create_rework_log_line",
        "method": "POST",
        "scope": "mes:rework-log:get"
    },
    {
        "desc": "创建线修过站测试记录",
        "path": "/api/v1.0/create_line_over_station_test_info",
        "method": "POST",
        "scope": "mes:rework-test:post"
    },
    {
        "desc": "根据工单id，获取该工单在序列号池中的一条未使用序列号",
        "path": "/api/beta1.0/get_sn",
        "method": "GET",
        "scope": "mes:data-pool:get"
    },
    {
        "desc": "根据工单id和sn，回调一条序列号已打印信息",
        "path": "/api/beta1.0/sn_printed",
        "method": "GET",
        "scope": "mes:data-pool:post"
    },
    {
        "desc": "根据工单id和fid，回调一条序列号已打印信息",
        "path": "/api/beta1.0/fid_printed",
        "method": "GET",
        "scope": "mes:data-pool:post"
    },
    {
        "desc": "根据工单id和sn，获取一条数据对象",
        "path": "/api/beta1.0/data/sn",
        "method": "GET",
        "scope": "mes:data-pool:get"
    },
    {
        "desc": "根据工单id，pid，获取当前工单当前工序的不同状态的数量",
        "path": "/api/beta1.0/procedure/number",
        "method": "GET",
        "scope": "mes:product-test:get"
    },
    {
        "desc": "根据PCBA工单id，pid，获取当前工单当前工序的不同状态的数量",
        "path": "/api/beta1.0/pcba_procedure/number",
        "method": "GET",
        "scope": "mes:pcba-test:get"
    },
    {
        "desc": "根据工单id，获取该工单在序列号池中的未使用序列号个数",
        "path": "/api/beta1.0/get_sn_no_print_num",
        "method": "GET",
        "scope": "mes:data-pool:get"
    },
    {
        "desc": "根据出厂编号获取测试记录中的MAC、SN、IMEI",
        "path": "/api/beta1.0/get_products_sn_for_fid",
        "method": "GET",
        "scope": "mes:products:get"
    },
    {
        "desc": "根据SN获取测试记录中的MAC、SN、IMEI、MANU_ID",
        "path": "/api/beta1.0/get_products_content_for_sn",
        "method": "GET",
        "scope": "mes:products:get"
    },
    {
        "desc": "根据imei获取测试记录中的MAC、SN、IMEI、MANU_ID",
        "path": "/api/beta1.0/get_products_content_for_imei",
        "method": "GET",
        "scope": "mes:products:get"
    },
    {
        "desc": "根据mac获取测试记录中的MAC、SN、IMEI、MANU_ID",
        "path": "/api/beta1.0/get_products_content_for_mac",
        "method": "GET",
        "scope": "mes:products:get"
    },
    {
        "desc": "记录关键组件绑定信息",
        "path": "/api/beta1.0/products/critical_component",
        "method": "POST",
        "scope": "mes:products-component:post"
    },
    {
        "desc": "记录关键组件绑定信息2",
        "path": "/api/beta1.0/products/critical_component2",
        "method": "POST",
        "scope": "mes:products-component:post"
    },
    {
        "desc": "根据工单id，产品id, sn, 获取该工单在客户提供序列号中的一条记录",
        "path": "/api/beta1.0/customer/get_num",
        "method": "GET",
        "scope": "mes:customer-sn:get"
    },
    {
        "desc": "根据工单id，产品id, 字段名称，字段值, 获取该工单在客户提供序列号中的一条记录",
        "path": "/api/beta1.0/customer/get_num2",
        "method": "GET",
        "scope": "mes:customer-sn:get"
    },
    {
        "desc": "根据字段名称，字段值, 获取该客户提供序列号中的一条记录",
        "path": "/api/beta1.0/customer/get_num4",
        "method": "GET",
        "scope": "mes:customer-sn:get"
    },
    {
        "desc": "根据描述信息和产品ID查询对应的关键部件绑定的相关信息",
        "path": "/api/beta1.0/products/get_critical_component",
        "method": "GET",
        "scope": "mes:products-component:get"
    },
    {
        "desc": "获取盒号",
        "path": "/api/beta1.0/box/get_number",
        "method": "GET",
        "scope": "mes:box:get"
    },
    {
        "desc": "获取箱号",
        "path": "/api/beta1.0/carton/get_number",
        "method": "GET",
        "scope": "mes:carton:get"
    },
    {
        "desc": "获取盒内数量",
        "path": "/api/beta1.0/box/total_quantity",
        "method": "POST",
        "scope": "mes:box-info:get"
    },
    {
        "desc": "将序列号绑定盒号",
        "path": "/api/beta1.0/box/set_info",
        "method": "POST",
        "scope": "mes:box-bind:post"
    },
    {
        "desc": "将序列号绑定箱号",
        "path": "/api/beta1.0/carton/set_info",
        "method": "POST",
        "scope": "mes:carton-bind:post"
    },
    {
        "desc": "记录成品绑定关系",
        "path": "/api/beta1.0/product/product_bind_product",
        "method": "GET",
        "scope": "mes:products-bind:post"
    },
    {
        "desc": "根据工单id，获取该工单在序列号池中的一条未使用序列号",
        "path": "/api/v1.0/get_sn",
        "method": "GET",
        "scope": "mes:data-pool:get"
    },
    {
        "desc": "根据工单id和sn，回调一条序列号已打印信息",
        "path": "/api/v1.0/sn_printed",
        "method": "GET",
        "scope": "mes:data-pool:post"
    },
    {
        "desc": "根据工单id和fid，回调一条序列号已打印信息",
        "path": "/api/v1.0/fid_printed",
        "method": "GET",
        "scope": "mes:data-pool:post"
    },
    {
        "desc": "根据工单id和sn，获取一条数据对象",
        "path": "/api/v1.0/data/sn",
        "method": "GET",
        "scope": "mes:data-pool:get"
    },
    {
        "desc": "根据工单id和fid，获取一条数据对象",
        "path": "/api/v1.0/data/fid",
        "method": "GET",
        "scope": "mes:data-pool:get"
    },
    {
        "desc": "根据工单id，获取该工单在序列号池中的未使用序列号个数",
        "path": "/api/v1.0/get_sn_no_print_num",
        "method": "GET",
        "scope": "mes:data-pool:get"
    },
    {
        "desc": "根据工单id，产品id, sn, 获取该工单在客户提供序列号中的一条记录",
        "path": "/api/v1.0/customer/get_num",
        "method": "GET",
        "scope": "mes:customer-sn:get"
    },
    {
        "desc": "根据工单id，产品id, 字段名称，字段值, 获取该工单在客户提供序列号中的一条记录",
        "path": "/api/v1.0/customer/get_num2",
        "method": "GET",
        "scope": "mes:customer-sn:get"
    },
    {
        "desc": "根据 字段名称，字段值, 获取该工单在客户提供序列号中的一条记录",
        "path": "/api/v1.0/customer/get_num3",
        "method": "GET",
        "scope": "mes:customer-sn:get"
    },
    {
        "desc": "根据字段名称，字段值, 获取该客户提供序列号中的一条记录",
        "path": "/api/v1.0/customer/get_num4",
        "method": "GET",
        "scope": "mes:customer-sn:get"
    },
    {
        "desc": "根据字段名称，字段值, 获取该pcba工单在客户提供序列号中的一条记录",
        "path": "/api/v1.0/customer/get_num5",
        "method": "GET",
        "scope": "mes:customer-sn:get"
    },
    {
        "desc": "根据出厂ID查询球和终端的SN",
        "path": "/api/v1.0/getomocsnforfid",
        "method": "POST",
        "scope": "mes:products:get"
    },
    {
        "desc": "创建测试详情",
        "path": "/api/v1.0/create_test_info",
        "method": "POST",
        "scope": "mes:product-group-test:post"
    },
    {
        "desc": "根据出厂编号获取测试记录中的MAC、SN、IMEI",
        "path": "/api/v1.0/get_products_sn_for_fid",
        "method": "GET",
        "scope": "mes:products:get"
    },
    {
        "desc": "根据SN获取测试记录中的MAC、SN、IMEI、MANU_ID",
        "path": "/api/v1.0/get_products_content_for_sn",
        "method": "GET",
        "scope": "mes:products:get"
    },
    {
        "desc": "根据imei获取测试记录中的MAC、SN、IMEI、MANU_ID",
        "path": "/api/v1.0/get_products_content_for_imei",
        "method": "GET",
        "scope": "mes:products:get"
    },
    {
        "desc": "根据mac获取测试记录中的MAC、SN、IMEI、MANU_ID",
        "path": "/api/v1.0/get_products_content_for_mac",
        "method": "GET",
        "scope": "mes:products:get"
    },
    {
        "desc": "记录成品绑定关系",
        "path": "/api/v1.0/product/product_bind_product",
        "method": "GET",
        "scope": "mes:products-bind:post"
    },
    {
        "desc": "加密卡专用api 写入测试记录",
        "path": "/api/v1.0/testlog/pcie",
        "method": "POST",
        "scope": "mes:product-test:post"
    },
    {
        "desc": "校验工单成品date_code是否一致",
        "path": "/api/v1.0/work_order/check_date_code",
        "method": "POST",
        "scope": "mes:work-order-check:post"
    },
    {
        "desc": "校验工单成品老化时间是否足够",
        "path": "/api/v1.0/work_order/check_aging",
        "method": "POST",
        "scope": "mes:products-check:post"
    },
    {
        "desc": "powerbi的测试",
        "path": "/api/v1.0/powerbi",
        "method": "GET",
        "scope": "mes:powerbi:get"
    },
    {
        "desc": "同步物料",
        "path": "/api/v1.0/sync_k3",
        "method": "GET",
        "scope": "mes:sync-material:get"
    },
    {
        "desc": "同步客户组",
        "path": "/api/v1.0/sync_customer",
        "method": "GET",
        "scope": "mes:sync-customer:get"
    },
    {
        "desc": "同步销售出库单明细",
        "path": "/api/v1.0/sync_out_stock_entry",
        "method": "GET",
        "scope": "mes:sync-sale-stock-out:get"
    },
    {
        "desc": "获取用户的所属组",
        "path": "/api/v1.0/user/info",
        "method": "GET",
        "scope": "mes:users:get"
    },
    {
        "desc": "用于认证系统系统调用查询用户",
        "path": "/api/odoo/v2.0/user/emails/{email}",
        "method": "GET",
        "scope": "mes:users:get"
    },
    {
        "desc": "用于认证系统系统调用更改操作只允许更改状态和姓名",
        "path": "/api/odoo/v2.0/users/{email}",
        "method": "PUT",
        "scope": "mes:users:put"
    },
    {
        "desc": "用于认证系统系统调用创建用户",
        "path": "/api/odoo/v2.0/users",
        "method": "POST",
        "scope": "mes:users:post"
    },
    {
        "desc": "获取角色信息",
        "path": "/api/odoo/v2.0/roles",
        "method": "GET",
        "scope": "mes:users:get"
    },
    {
        "desc": "获取工单信息",
        "path": "/api/v1.0/get_order_info",
        "method": "GET",
        "scope": "mes:work-orders:get"
    },
    {
        "desc": "获取erp_api_service",
        "path": "/api/wms/v2.0/erp_api_service",
        "method": "GET",
        "scope": "wms:erp-api-service:get"
    },
    {
        "desc": "创建发货信息",
        "path": "/api/v1.0/delivery_notice/info",
        "method": "GET",
        "scope": "mes:delivery-records:post"
    },
    {
        "desc": "创建发货信息",
        "path": "/api/v1.0/delivery_notice/info",
        "method": "GET",
        "scope": "mes:delivery-records:post"
    },
    {
        "desc": "获取发货通知单明细",
        "path": "/api/v1.0/delivery_notice/get_info",
        "method": "GET",
        "scope": "mes:delivery-notes:get"
    },
    {
        "desc": "删除发货记录",
        "path": "/api/v1.0/delivery_notice/del_record",
        "method": "POST",
        "scope": "mes:delivery-records:delete"
    },
    {
        "desc": "获取符合条件的发货通知单",
        "path": "/api/v1.0/delivery_notice/get_Notice",
        "method": "GET",
        "scope": "mes:delivery-notes:get"
    },
    {
        "desc": "发货通知单 打上标记 用于显示今日发货使用",
        "path": "/api/v1.0/delivery_notice/add_today_shipment",
        "method": "POST",
        "scope": "mes:delivery-notes:put"
    },
    {
        "desc": "获取今日发货的 发货通知单列表",
        "path": "/api/v1.0/delivery_notice/get_today_shipment",
        "method": "GET",
        "scope": "mes:delivery-notes:get"
    },
    {
        "desc": "把发货通知单从今日发货列表中去除",
        "path": "/api/v1.0/delivery_notice/del_today_shipment",
        "method": "POST",
        "scope": "mes:delivery-notes:put"
    },
    {
        "desc": "获取发货记录",
        "path": "/api/v1.0/delivery_notice/query_delivery_record",
        "method": "GET",
        "scope": "mes:delivery-records:get"
    },
    {
        "desc": "上传发货通知单的配件,更新发货通知单表的配件数量",
        "path": "/api/v1.0/delivery_notice/update_deliver_parts",
        "method": "POST",
        "scope": "mes:delivery-records:put"
    },
    {
        "desc": "上传发货通知单的配件,更新发货通知单表的配件数量(调拨)",
        "path": "/api/v1.0/delivery_notice/update_deliver_parts2",
        "method": "POST",
        "scope": "mes:delivery-records:put"
    },
    {
        "desc": "上传发货通知单的配件,更新发货通知单表的配件数量(其他出库)",
        "path": "/api/v1.0/delivery_notice/update_deliver_parts3",
        "method": "POST",
        "scope": "mes:delivery-records:put"
    },
    {
        "desc": "发货结果邮件给销售",
        "path": "/api/v1.0/delivery_notice/send_email",
        "method": "POST",
        "scope": "mes:delivery-email:post"
    },
    {
        "desc": "发货结果邮件给调拨单创建者",
        "path": "/api/v1.0/delivery_notice/send_email2",
        "method": "POST",
        "scope": "mes:delivery-email:post"
    },
    {
        "desc": "手动同步发货通知单",
        "path": "/api/v1.0/delivery_notice/synchronization",
        "method": "POST",
        "scope": "mes:sync-delivery-notes:post"
    },
    {
        "desc": "发货记录导出SN",
        "path": "/api/v1.0/delivery_notice/downSNIMEI",
        "method": "GET",
        "scope": "mes:delivery-records:get"
    },
    {
        "desc": "发货前查询K3是否存在此发货单",
        "path": "/api/v1.0/delivery_notice/check_single_fhtzd",
        "method": "POST",
        "scope": "mes:delivery-notes-check:post"
    },
    {
        "desc": "关闭K3查询不到的发货单",
        "path": "/api/v1.0/delivery_notice/close_bill",
        "method": "POST",
        "scope": "mes:delivery-notes:put"
    },
    {
        "desc": "查询ip",
        "path": "/api/v1.0/delivery_notice/query_ip",
        "method": "GET",
        "scope": "mes:ip:get"
    },
    {
        "desc": "查询调拨单",
        "path": "/api/v1.0/transfer_order/query",
        "method": "GET",
        "scope": "mes:transfer-notes:get"
    },
    {
        "desc": "同步调拨单",
        "path": "/api/v1.0/transfer_order/sync",
        "method": "GET",
        "scope": "mes:sync-transfer-notes:get"
    },
    {
        "desc": "创建调拨记录",
        "path": "/api/v1.0/transfer_order/create_delivery",
        "method": "POST",
        "scope": "mes:transfer-records:post"
    },
    {
        "desc": "查询调拨记录",
        "path": "/api/v1.0/transfer_order/query_delivery",
        "method": "GET",
        "scope": "mes:transfer-records:get"
    },
    {
        "desc": "删除调拨记录",
        "path": "/api/v1.0/transfer_order/remove_delivery",
        "method": "POST",
        "scope": "mes:transfer-records:delete"
    },
    {
        "desc": "查询其他出库单",
        "path": "/api/v1.0/stock_order/query",
        "method": "GET",
        "scope": "mes:misc-stock-out-notes:get"
    },
    {
        "desc": "同步其他出库单",
        "path": "/api/v1.0/stock_order/sync",
        "method": "GET",
        "scope": "mes:sync-misc-stock-out-notes:get"
    },
    {
        "desc": "创建其他出库发货记录",
        "path": "/api/v1.0/stock_order/create_delivery",
        "method": "POST",
        "scope": "mes:misc-stock-out-records:post"
    },
    {
        "desc": "查询其他出库发货记录",
        "path": "/api/v1.0/stock_order/query_delivery",
        "method": "GET",
        "scope": "mes:misc-stock-out-records:get"
    },
    {
        "desc": "删除其他出库发货记录",
        "path": "/api/v1.0/stock_order/remove_delivery",
        "method": "POST",
        "scope": "mes:misc-stock-out-records:delete"
    },
    {
        "desc": "质检单明细扫描ReelID",
        "path": "/api/v1.0/inspection/scan_reel_id",
        "method": "POST",
        "scope": "wms:reelids:post"
    },
    {
        "desc": "记录IQC检验记录",
        "path": "/api/v1.0/inspection/record",
        "method": "POST",
        "scope": "wms:inspection-record:post"
    },
    {
        "desc": "查询质检记录",
        "path": "/api/v1.0/inspection/record",
        "method": "GET",
        "scope": "wms:inspection-record:get"
    },
    {
        "desc": "根据ReelID名称，入库单更新reelid状态及入库单状态",
        "path": "/api/wms/v2.0/notes/instock/{no}",
        "method": "PUT",
        "scope": "wms:reelids:put"
    },
    {
        "desc": "绑定备料车",
        "path": "/api/wms/v2.0/notes/prepare-bind",
        "method": "PUT",
        "scope": "wms:reelids:put"
    },
    {
        "desc": "解除绑定备料车(线长确认收料)",
        "path": "/api/wms/v2.0/notes/prepare-unbind",
        "method": "PUT",
        "scope": "wms:reelids:put"
    },
    {
        "desc": "解除绑定备料车(使用单据编号)",
        "path": "/api/wms/v2.0/notes/prepare-unbind2",
        "method": "PUT",
        "scope": "wms:reelids:put"
    },
    {
        "desc": "强制解除绑定备料车(退回货架)",
        "path": "/api/wms/v2.0/notes/prepare-return",
        "method": "PUT",
        "scope": "wms:reelids:put"
    },
    {
        "desc": "强制解除绑定备料车(使用单据编号)",
        "path": "/api/wms/v2.0/notes/prepare-return2",
        "method": "PUT",
        "scope": "wms:reelids:put"
    },
    {
        "desc": "查询备料记录",
        "path": "/api/wms/v2.0/notes/prepare-records",
        "method": "GET",
        "scope": "wms:prepare-records:get"
    },
    {
        "desc": "重新绑定备料记录",
        "path": "/api/wms/v2.0/notes/prepare-rebind",
        "method": "PUT",
        "scope": "wms:prepare-records:put"
    },
    {
        "desc": "查询 配件领料 记录",
        "path": "/api/wms/v2.0/notes/parts-pick-records",
        "method": "GET",
        "scope": "wms:parts-pick-records:get"
    },
    {
        "desc": "查询领料记录工单",
        "path": "/api/wms/v2.0/notes/prepare-wo",
        "method": "GET",
        "scope": "wms:prepare-records:get"
    },
    {
        "desc": "退料上架",
        "path": "/api/wms/v2.0/notes/product-return-onshelf",
        "method": "PUT",
        "scope": "wms:product-return-onshelf:put"
    },
    {
        "desc": "更改ReelID数量",
        "path": "/api/v1.0/quality/change_reel_id",
        "method": "POST",
        "scope": "wms:reelids:put"
    },
    {
        "desc": "冻结ReelID",
        "path": "/api/v1.0/quality/freeze_reel_id",
        "method": "POST",
        "scope": "wms:reelids:put"
    },
    {
        "desc": "创建来料记录表",
        "path": "/api/v1.0/receive/create_pur_record",
        "method": "POST",
        "scope": "wms:receive-records:post"
    },
    {
        "desc": "查询来料记录表",
        "path": "/api/v1.0/receive/pur_receive_record",
        "method": "GET",
        "scope": "wms:receive-records:get"
    },
    {
        "desc": "创建ReelID",
        "path": "/api/wms/v2.0/notes/reelids",
        "method": "POST",
        "scope": "wms:reelids:post"
    },
    {
        "desc": "修改ReelID状态（送检、入库）",
        "path": "/api/wms/v2.0/notes/reelids/status",
        "method": "PUT",
        "scope": "wms:reelids:put"
    },
    {
        "desc": "根据ReelID名称，获取ReelID记录",
        "path": "/api/wms/v2.0/notes/reelids/{reelid}",
        "method": "GET",
        "scope": "wms:reelids:get"
    },
    {
        "desc": "根据单据编号和明细ID获取获取reelID明细",
        "path": "/api/wms/v2.0/notes/reelids",
        "method": "GET",
        "scope": "wms:reelids:get"
    },
    {
        "desc": "根据单据编号和明细ID获取获取reelID明细",
        "path": "/api/wms/v2.0/notes/reelids/entry_id",
        "method": "GET",
        "scope": "wms:reelids:get"
    },
    {
        "desc": "根据单据编号和明细ID获取获取reelID明细",
        "path": "/api/wms/v2.0/notes/reelids/list",
        "method": "GET",
        "scope": "wms:reelids:get"
    },
    {
        "desc": "根据物料编号或库位获取reelID-Stocks",
        "path": "/api/wms/v2.0/notes/reelids-stocks",
        "method": "GET",
        "scope": "wms:reelids:get"
    },
    {
        "desc": "修改reelID-Stocks",
        "path": "/api/wms/v2.0/notes/reelids-stocks",
        "method": "PUT",
        "scope": "wms:reelids:put"
    },
    {
        "desc": "根据ReelID和仓位名称上架reelID",
        "path": "/api/wms/v2.0/notes/onshelf/{position}",
        "method": "PUT",
        "scope": "wms:onshelf:put"
    },
    {
        "desc": "领料、补料下架",
        "path": "/api/wms/v2.0/notes/unshelf/{position}",
        "method": "PUT",
        "scope": "wms:unshelf:put"
    },
    {
        "desc": "领料、补料下架(使用单据编号)",
        "path": "/api/wms/v2.0/notes/unshelf2",
        "method": "PUT",
        "scope": "wms:unshelf:put"
    },
    {
        "desc": "其他出库单下架",
        "path": "/api/wms/v2.0/notes/misc-stock-out-unshelf",
        "method": "POST",
        "scope": "wms:unshelf:post"
    },
    {
        "desc": "其他入库上架",
        "path": "/api/wms/v2.0/notes/misc-stock-in-onshelf",
        "method": "POST",
        "scope": "wms:onshelf:post"
    },
    {
        "desc": "调拨单下架",
        "path": "/api/wms/v2.0/notes/transfer-stock-out-unshelf",
        "method": "POST",
        "scope": "wms:unshelf:post"
    },
    {
        "desc": "调拨单上架",
        "path": "/api/wms/v2.0/notes/transfer-stock-in-onshelf",
        "method": "POST",
        "scope": "wms:onshelf:post"
    },
    {
        "desc": "ReelID移库",
        "path": "/api/wms/v2.0/notes/reelids-move",
        "method": "PUT",
        "scope": "wms:reelids:put"
    },
    {
        "desc": "生成退货记录",
        "path": "/api/wms/v2.0/notes/return-stock-records",
        "method": "POST",
        "scope": "wms:return-stock-records:post"
    },
    {
        "desc": "查询退货记录",
        "path": "/api/wms/v2.0/notes/return-stock-records/{returnNo}",
        "method": "GET",
        "scope": "wms:return-stock-records:get"
    },
    {
        "desc": "查询退货记录",
        "path": "/api/wms/v2.0/notes/return-stock-records",
        "method": "GET",
        "scope": "wms:return-stock-records:get"
    },
    {
        "desc": "获取库房、仓库、货架的信息",
        "path": "/api/v1.0/storage",
        "method": "GET",
        "scope": "wms:stocks:get"
    },
    {
        "desc": "获取仓位信息",
        "path": "/api/v1.0/positions",
        "method": "GET",
        "scope": "wms:positions:get"
    },
    {
        "desc": "生成仓位编号并返回",
        "path": "/api/v1.0/positions",
        "method": "POST",
        "scope": "wms:positions:post"
    },
    {
        "desc": "推荐ReelID",
        "path": "/api/wms/v2.0/notes/materials/{number}/rule/{rule}/positions",
        "method": "GET",
        "scope": "wms:reelids:get"
    },
    {
        "desc": "推荐SN",
        "path": "/api/wms/v2.0/notes/recommend-products/{number}",
        "method": "GET",
        "scope": "wms:products:get"
    },
    {
        "desc": "根据物料号、单据编号、物料号判断仓位是否正确",
        "path": "/api/wms/v2.0/notes/positions/checked/{no}",
        "method": "GET",
        "scope": "wms:positions:get"
    },
    {
        "desc": "根据物料号获取推荐仓位",
        "path": "/api/wms/v2.0/notes/positions/material/{no}",
        "method": "GET",
        "scope": "wms:positions:get"
    },
    {
        "desc": "根据仓库名称、物料号查询库存数量",
        "path": "/api/wms/v2.0/notes/inventory",
        "method": "GET",
        "scope": "wms:inventory:get"
    },
    {
        "desc": "根据仓库查询盘点记录表",
        "path": "/api/wms/v2.0/notes/inventory-record",
        "method": "GET",
        "scope": "wms:inventory:get"
    },
    {
        "desc": "根据仓库、物料号修改盘点明细数量",
        "path": "/api/wms/v2.0/notes/inventory-record-entry",
        "method": "PUT",
        "scope": "wms:inventory:put"
    },
    {
        "desc": "创建缺料记录表",
        "path": "/api/wms/v2.0/notes/shortage-record",
        "method": "POST",
        "scope": "wms:shortage-record:post"
    },
    {
        "desc": "查询缺料记录表",
        "path": "/api/wms/v2.0/notes/shortage-record",
        "method": "GET",
        "scope": "wms:shortage-record:get"
    },
    {
        "desc": "修改缺料记录表",
        "path": "/api/wms/v2.0/notes/shortage-record",
        "method": "PUT",
        "scope": "wms:shortage-record:put"
    }
]
    consulService = ConsulService("consul", 8500)
    consulService.registerAPI(ip, 5000, 'jx-attandance-api-10-0-0-1','jx-attendance-api', 'traefik', 'inhand-poweris',
                              {'verison':'v1.0.0'}, api_entries, protocol='http',
                    health_entry='/health')


"""
    tags=[]
    tags.append("group=inhand-poweris")
    tags.append("secure=flaes")
    tags.append("traefik.enable=true")

    tags.append("traefik.http.services.jx-attendance-api.loadbalancer.server.weight=1")
    consulService=ConsulService("consul",8500)
    name="jx-attandance-api-10-0-0-1"
    service_id="jx-attendance-api"
    consulService.registerService(name,service_id,"10.5.0.247",5000,tags)

    check=consulService.check("10.5.0.247",5000,"30s")
    print(check)
    res=consulService.getService(service_id)
    print(res)
"""


