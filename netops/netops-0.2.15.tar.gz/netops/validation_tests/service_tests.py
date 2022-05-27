import ipaddress
import json

from ..infra.infra import import_infra_data
from ..api.netbox.netbox_manager import NetboxManager
from ..api.netbox.util import get_sot_filter_parameters
from ..utils.utils import convert_txt_to_pdf
from .reachability import reachability_tests
from .traceroute import traceroute_tests
from .junos.tests import junos_ping



def run_tests(infra_file_path, test_type, infra_key, results_file_path, reach_tests_previous_results_path=None, junos_ping_target=None):
    """ TODO translate to english
    
    Executa testes de rede sobre a infraestrutura.
    
    Recebe:
            infra_file_path - nome do arquivo de descrivao de infraestrutura com extensao YAML,
            contendo as informacoes da infraestrutura associada a logica de negocio
            test_type - tipo de testes (reachability, traceroute)
            infra_key - chave da infra que representa o endereco IP ou a rede a ser testada para reachability tests ou o endereco que deve
            deve estar contido no path para traceroute tests
            reach_tests_previous_results_path - path do arquivo JSON de resultados previos que serao utilizados nos testes de traceroute
            results_file_path - path do arquivo JSON em que serao armazenados os resultados
            
    Retorna:
            exit(0) - se testes foram bem sucedidos
            exit(1) - se testes foram mal sucedidos"""
    infra, infra_dicts = import_infra_data(infra_file_path)

    if test_type == 'reachability':
        addresses = infra[infra_key]
        print("Addresses for reachability tests: ", addresses)
        networks = []
        ips_list = []

        if type(addresses) == list:
            for address in addresses:
                network = ipaddress.ip_network(address)
                networks.append(network)
        else:
            network = ipaddress.ip_network(addresses)
            networks.append(network)
            
        for network in networks:
            for ip in network.hosts():
                ips_list.append(str(ip))

        result, ip_results = reachability_tests(ips_list, 4)

        if result:
            print("Reachability tests was SUCCESSFULL")
            # Serializing json 
            json_object = json.dumps(ip_results, indent = 4)
            with open(results_file_path, "w") as outfile:
                outfile.write(json_object)
            convert_txt_to_pdf(results_file_path)
            #Commented to enable rollback on next stage/job 
            exit(0)
        else:
            print("Reachability tests FAILED")
            # Serializing json 
            json_object = json.dumps(ip_results, indent = 4)
            with open(results_file_path, "w") as outfile:
                outfile.write(json_object)
            convert_txt_to_pdf(results_file_path)
            #Commented to enable rollback on next stage/job 
            exit(1)
        #exit(0)
        
    elif test_type == 'traceroute':
        path_ip = infra[infra_key]
        # Opening JSON file
        with open(reach_tests_previous_results_path, 'r') as openfile:
            ips_list = json.load(openfile)["successfull_reach_tests"]
        result, responses = traceroute_tests(ips_list, path_ip)

        if result:
            print("Traceroute tests was SUCCESSFULL")
            with open(results_file_path, "w") as outfile:
                outfile.write("* Traceroute tests was SUCCESSFULL \n")
                outfile.write("\n")
                outfile.write("* Tests responses below: \n")
                for response in responses:
                    outfile.write(response)
                    outfile.write("\n")
                    outfile.write("\n")
            convert_txt_to_pdf(results_file_path)
            #Commented to enable rollback on next stage/job 
            exit(0)
        else:
            print("Traceroute tests FAILED")
            with open(results_file_path, "w") as outfile:
                outfile.write("* Traceroute tests FAILED \n")
                outfile.write("\n")
                outfile.write("* Tests responses below: \n")
                outfile.write("\n")
                for response in responses:
                    outfile.write(response)
                    outfile.write("\n")
                    outfile.write("\n")
            convert_txt_to_pdf(results_file_path)
            #Commented to enable rollback on next stage/job      
            exit(1)
        #exit(0)

    elif test_type == 'junos-reachability':
        device_name = infra[infra_key]
        address = junos_ping_target
        print("Addresses for junos reachability test: ", address)
        filter_params = get_sot_filter_parameters()
        netbox_manager = NetboxManager(filter_params=filter_params)
        host = netbox_manager.get_nornir().filter(name=device_name)
        
        result = junos_ping(host, device_name, address)

        if result['ping-success']:
            print("Reachability tests was SUCCESSFULL")
            # Serializing json 
            json_object = json.dumps(result, indent = 4)
            with open(results_file_path, "w") as outfile:
                outfile.write(json_object)
            convert_txt_to_pdf(results_file_path)
            exit(0)
        else:
            print("Reachability tests FAILED")
            # Serializing json 
            json_object = json.dumps(result, indent = 4)
            with open(results_file_path, "w") as outfile:
                outfile.write(json_object)
            convert_txt_to_pdf(results_file_path)
            exit(1)