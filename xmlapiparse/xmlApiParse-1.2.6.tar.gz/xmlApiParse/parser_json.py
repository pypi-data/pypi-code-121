from time import strftime
from typing import List
from abc import ABC, abstractclassmethod
import lxml.etree as Etree
import requests
from urllib3.exceptions import InsecureRequestWarning
from xmlApiParse.enums import SpecificCollectionsEnum, AllCollectionsEnum
from xmlApiParse.repository import (
    ParseError, ConnectionErrors, BadRequestError,
    WaiterListDTO, OrderListDTO, RestaurantsDTO,
    MenuDTO, MenuItemsDTO, EmployeeDTO, WaiterDTO
)


class XMLRequest(ABC):

    @abstractclassmethod
    def check_connection(self):
        pass

    @abstractclassmethod
    def send_request(self):
        pass

    @abstractclassmethod
    def all_collections_request(self):
        pass

    @abstractclassmethod
    def specific_collections_request(self):
        pass

    @abstractclassmethod
    def employees_list_request(self):
        pass

    @abstractclassmethod
    def waiter_list_request(self):
        pass

    @abstractclassmethod
    def order_list_request(self):
        pass

    @abstractclassmethod
    def restaurants_request(self):
        pass

    @abstractclassmethod
    def menu_request(self):
        pass

    @abstractclassmethod
    def menu_items_request(self):
        pass


class RKXMLRequest(XMLRequest):
    media_type = "text/xml"
    connected = False

    def log(self, log_info):
        print(log_info) if self.logging else None

    def __init__(self, host: str, user_name: str, password: str, logging: bool = False):
        self.host = host
        self.user_name = user_name
        self.password = password
        self.logging = logging
        self.auth = (user_name, password)

    def check_connection(self):
        try:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            response = requests.get(self.host, auth=self.auth, verify=False)
            if response.status_code != 200:
                raise ConnectionErrors('Conection error')
            self.connected = True
        except Exception as error:
            raise ConnectionErrors('Conection error') from error
        return self.connected

    def send_request(self, body: str = None):
        if self.check_connection() is True:
            try:
                response = requests.get(self.host, data=body, auth=self.auth, verify=False)
            except Exception as error:
                raise BadRequestError('Bad Request') from error
        return response

    def parse(self, content: str):
        """Parses the incoming bytestream as XML and returns the resulting data."""

        try:
            response = self.send_request(body=content)
            root: list = Etree.fromstring(response.content)
        except (ParseError, ValueError) as error:
            raise ParseError(f"XML parse error - {str(error)}")
        data = self._xml_convert(elements=root)
        return data

    def _xml_convert(self, elements):
        """convert the xml `element` into the corresponding python object"""

        data: dict = {}
        for num, child in enumerate(elements, 1):
            data[f"{num}-{child.tag}"] = {
                "attrib": child.attrib,
                "child":  self._xml_convert(elements=child)}
        return data

    def all_collections_request(self, collection: AllCollectionsEnum):
        """request to get all collections"""

        body = f'<RK7Query><RK7CMD CMD="{collection}"/></RK7Query>'
        response = self.send_request(body=body)
        element_list = []
        try:
            parsed_collection = Etree.fromstring(response.content)
            for item in parsed_collection:
                collection_node = list(item.iter())
                for collections in collection_node:
                    element_list.append(collections.attrib)
        except Exception as error:
            raise ParseError(f"XML parse error - {str(error)}")
        return element_list

    def specific_collections_request(self, collection: SpecificCollectionsEnum):
        """request a specific collection"""

        body = f'<RK7Query><RK7CMD CMD="GetRefData" RefName = "{collection}"/></RK7Query>'
        element = []
        response = self.send_request(body=body)
        try:
            parsed_element = Etree.fromstring(response.content)
            for item in parsed_element.findall("./RK7Reference/Items/Item"):
                attr_of_item_node = item.attrib
                element.append(attr_of_item_node)
        except Exception as error:
            raise ParseError(f"XML parse error - {str(error)}")
        return element

    def employees_list_request(self, name_filter: str = None) -> List[EmployeeDTO]:
        """request to get all employees filtered by name"""

        body = ('<RK7Query><RK7CMD CMD="GetRefData" RefName="Restaurants" IgnoreEnums="1" '
                              'WithChildItems="3" WithMacroProp="1" OnlyActive = "1" '
                              'PropMask="RIChildItems.(Ident,Name,genRestIP,genprnStation,genDefDlvCurrency,AltName,'
                              'RIChildItems.TRole(ItemIdent,passdata,Name,AltName,gen*,'
                              'RIChildItems.(Ident,Name,AltName,gen*)))"/></RK7Query>')
        response = self.send_request(body=body)
        element = []
        try:
            tree = Etree.fromstring(response.content)
            for item in tree.findall("./RK7Reference/RIChildItems/TRK7Restaurant"):
                restaurant = item.attrib['Name']
                for item in tree.findall(
                        "./RK7Reference/RIChildItems/TRK7Restaurant/RIChildItems/TRole"):
                    role = item.attrib['Name']
                    for item in tree.findall(
                        "./RK7Reference/RIChildItems/TRK7Restaurant/RIChildItems/TRole/RIChildItems/TEmployee"
                    ):
                        if item.attrib["Name"] == name_filter:
                            return item.attrib
                        if name_filter is None:
                            name = item.attrib['Name']
                            altname = item.attrib['AltName']
                            gen_san_date = item.attrib['genSanDate']
                            gen_tax_payer_id_num = item.attrib['genTaxPayerIdNum']
                            ident = item.attrib['Ident']
                            employee_dto = EmployeeDTO(restaurant=restaurant, name=name, role=role, altname=altname,
                                                    gen_san_date=gen_san_date, ident=ident,
                                                    gen_tax_payer_id_num=gen_tax_payer_id_num)
                            element.append(employee_dto)
        except (ParseError, ValueError) as error:
            raise ParseError(f"XML parse error - {str(error)}")
        return element

    def waiter_list_request(self) -> List[WaiterListDTO]:
        """request for a list of waiters"""

        body = '<RK7Query><RK7CMD CMD="GetWaiterList"/></RK7Query>'
        response = self.send_request(body=body)
        elements = []
        try:
            parsed_element = Etree.fromstring(response.content)
            for item in parsed_element:
                for element in item:
                    waiter_id = (element.attrib['ID'])
                    code = (element.attrib['Code'])
                    waiter_dto = WaiterListDTO(id=waiter_id, code=code)
                    elements.append(waiter_dto)
        except (ParseError, ValueError) as error:
            raise ParseError(f"XML parse error - {str(error)}")
        return elements

    def order_list_request(self) -> List[OrderListDTO]:
        """requests to receive the entire order"""

        body = '<RK7Query><RK7CMD CMD="GetOrderList"/></RK7Query>'
        response = self.send_request(body=body)
        element_list = []
        try:
            parsed_element = Etree.fromstring(response.content)
            for item in parsed_element.findall("./Visit"):
                elements = item.iter()
                for element in elements:
                    order_dto = OrderListDTO(order_id=(element.attrib.get('OrderID')),
                    order_name=(element.attrib.get('OrderName')), url=(element.attrib.get('Url')),
                    version=(element.attrib.get('Version')), crc32=(element.attrib.get('Crc32')),
                    guid=(element.attrib.get('Guid')), table_id=(element.attrib.get('TableId')),
                    table_code=(element.attrib.get('TableCode')), order_categ_id=(element.attrib.get('OrderCategId')),
                    order_categ_code=(element.attrib.get('OrderCategCode')), bill=(element.attrib.get('Bill')),
                    waiter_id=(element.attrib.get('WaiterId')), order_type_code=(element.attrib.get('OrderTypeCode')),
                    order_type_id=(element.attrib.get('OrderTypeId')), to_pay_sum=(element.attrib.get('ToPaySum')),
                    waiter_code=(element.attrib.get('WaiterCode')), order_sum=(element.attrib.get('OrderSum')),
                    total_pieces=(element.attrib.get('TotalPieces')), finished=(element.attrib.get('Finished')),
                    price_list_sum=(element.attrib.get('PriceListSum')), dessert=(element.attrib.get('Dessert')))
                    element_list.append(order_dto)
        except (ParseError, ValueError) as error:
            raise ParseError(f"XML parse error - {str(error)}")
        return element_list

    def restaurants_request(self) -> List[RestaurantsDTO]:
        """requests for restaurant and roles and employees"""

        body = '<RK7Query> <RK7CMD CMD="GetRefData" RefName="Restaurants" ' \
                             'IgnoreEnums="1" WithChildItems="3" WithMacroProp="1" ' \
                             'OnlyActive = "1" PropMask="RIChildItems.(Ident,Name,genRestIP,genprnStation,' \
                             'genDefDlvCurrency,AltName,RIChildItems.TRole(ItemIdent,passdata,Name,AltName,gen*,' \
                             'RIChildItems.(Code,Ident,Name,AltName,gen*)))" /></RK7Query>'
        response = self.send_request(body=body)
        restaurants = []
        parsed_element = Etree.fromstring(response.content)
        try:
            for item in parsed_element.findall("./RK7Reference/RIChildItems/TRK7Restaurant"):
                restaurant_dto = RestaurantsDTO(name=item.attrib['Name'], alt_name=item.attrib['AltName'],
                                                ident=item.attrib['Ident'])
                restaurants.append(restaurant_dto)
        except Exception as error:
            raise ParseError(f"XML parse error - {str(error)}")
        return restaurants

    def menu_request(self, code: int) -> List[MenuDTO]:
        """getting dishes available for sale"""

        body = f'<RK7Query><RK7CMD CMD="GetOrderMenu" StationCode="{code}" DateTime="{strftime("%Y-%m-%d %H:%M:%S")}" /></RK7Query>'
        response = self.send_request(body=body)
        elements = []
        try:
            parsed_element = Etree.fromstring(response.content)
            for item in parsed_element.findall("./Dishes/Item"):
                attr_of_item_node = (item.attrib)
                ident = (attr_of_item_node['Ident'])
                price = (attr_of_item_node['Price'])
                menudto = MenuDTO(ident=ident, price=price)
                elements.append(menudto)
        except Exception as error:
            raise ParseError(f"XML parse error - {str(error)}")
        return elements

    def menu_items_request(self, name_filter: str = None) -> List[MenuItemsDTO]:
        """For a complete list of dishes or a specific dish"""

        body = '<RK7Query><RK7CMD CMD="GetRefData" RefName = "MENUITEMS"/></RK7Query>'
        response = self.send_request(body=body)
        element = []
        try:
            parsed_element = Etree.fromstring(response.content)
            for item in parsed_element.findall("./RK7Reference/Items/Item"):
                if item.attrib['Status'] == 'rsActive' and item.attrib['ActiveHierarchy'] == 'true':
                    if item.attrib.get('Name') == name_filter:
                        return item.attrib
                    menu_items_dto = MenuItemsDTO(
                        ident=(item.attrib['Ident']), item_ident=(item.attrib['ItemIdent']),
                        source_ident=(item.attrib['SourceIdent']), guid_string=(item.attrib['GUIDString']),
                        assign_childs_on_server=(item.attrib['AssignChildsOnServer']),
                        active_hierarchy=(item.attrib['ActiveHierarchy']), code=(item.attrib['Code']),
                        name=(item.attrib['Name']), alt_name=(item.attrib['AltName']),
                        main_parent_ident=(item.attrib['MainParentIdent']), status=(item.attrib['Status']),
                        sales_terms_start_sale=(item.attrib['SalesTerms_StartSale']),
                        sales_terms_stop_sale=(item.attrib['SalesTerms_StopSale']),
                        future_tax_dish_type=(item.attrib['FutureTaxDishType']),  parent=(item.attrib['Parent']),
                        cook_mins=(item.attrib['CookMins']), modi_weight=(item.attrib['ModiWeight']),
                        min_rest_qnt=(item.attrib['MinRestQnt']), categ_path=(item.attrib['CategPath']),
                        price_mode=(item.attrib['PriceMode']), modi_scheme=(item.attrib['ModiScheme']),
                        combo_scheme=(item.attrib['ComboScheme']), kurs=(item.attrib['Kurs']),
                        qnt_dec_digits=(item.attrib['QntDecDigits']), comment=(item.attrib['Comment']),
                        instruct=(item.attrib['Instruct']), flags=(item.attrib['Flags']),
                        tara_weight=(item.attrib['TaraWeight']), confirm_qnt=(item.attrib['ConfirmQnt']),
                        bar_codes=(item.attrib['BarCodes']), open_price=(item.attrib['OpenPrice']),
                        change_qnt_once=(item.attrib['ChangeQntOnce']),
                        use_rest_control=(item.attrib['UseRestControl']),
                        use_confirm_qnt=(item.attrib['UseConfirmQnt']),
                        bar_codes_full_info=(item.attrib['BarcodesFullInfo']),
                        item_kind=(item.attrib['ItemKind']),
                        tariff_round_rule=(item.attrib['TariffRoundRule']),
                        combo_discount=(item.attrib['ComboDiscount']),
                        money_round_rule=(item.attrib['MoneyRoundRule']), round_time=(item.attrib['RoundTime']),
                        guests_dish_rating=(item.attrib['GuestsDishRating']), rate_type=(item.attrib['RateType']),
                        right_lvl=(item.attrib['RightLvl']),
                        minimum_tarif_time=(item.attrib['MinimumTarifTime']),
                        maximum_tarif_time=(item.attrib['MaximumTarifTime']),
                        ignored_tarif_time=(item.attrib['IgnoredTarifTime']),
                        min_tarif_amount=(item.attrib['MinTarifAmount']),
                        max_tarif_amount=(item.attrib['MaxTarifAmount']),
                        availability_schedule=(item.attrib['AvailabilitySchedule']),
                        dont_pack=(item.attrib['DontPack'])
                    )
                    element.append(menu_items_dto)
        except Exception as error:
            raise ParseError(f"XML parse error - {str(error)}")
        return element

    def get_waiter(self) -> List[WaiterDTO]:
        body = '<RK7Query> <RK7CMD CMD="GetRefData" RefName="Restaurants" ' \
                             'IgnoreEnums="1" WithChildItems="3" WithMacroProp="1" ' \
                             'OnlyActive = "1" PropMask="RIChildItems.(Ident,Name,genRestIP,genprnStation,' \
                             'genDefDlvCurrency,AltName,RIChildItems.TRole(ItemIdent,passdata,Name,AltName,gen*,' \
                             'RIChildItems.(Code,Ident,Name,AltName,gen*)))" /></RK7Query>'

        response = self.send_request(body=body)
        parsed_waiter_nodes = Etree.fromstring(response.content)
        data = []
        for item in parsed_waiter_nodes.findall("./RK7Reference/RIChildItems/TRK7Restaurant"):
            restaurant = item.attrib['Name']
            for item in parsed_waiter_nodes.findall(
                    "./RK7Reference/RIChildItems/TRK7Restaurant/RIChildItems/TRole"):
                if item.attrib['Name'] == "Официанты":
                    for item in parsed_waiter_nodes.findall(
                        "./RK7Reference/RIChildItems/TRK7Restaurant/RIChildItems/TRole/RIChildItems/TEmployee"
                    ):
                        waiter_dto = WaiterDTO(
                            restaurant=(restaurant),
                            name=(item.attrib['Name']), ident=(item.attrib['Ident']),
                            code=item.attrib['Code'])
                        data.append(waiter_dto)
        return data
