import zeep
from zeep import Client
from zeep.helpers import serialize_object
import json


class PlanningNl(object):
    def __init__(self, username, password):
        """
        This package is meant to get from or push data to planning.nl. An timeschedule tool. The requests are all made with soap.
        See for documentation of the SOAP API the following link: https://wiki.visibox.nl/display/VIS/Algemene+informatie
        :param username: The username for planning.nl
        :param password: The corresponding password
        """
        client = Client('https://api.visibox.nl/v1/authentication?wsdl')
        request_body = {'username': username, 'password': password}
        response = client.service.login(request_body)
        self.token = response['authenticationToken']

    def get_human_resources(self, employee_id=None):
        """
        Get all the employees with their basic information (like personal details).
        :param employee_id: An optional filter to receive data from only 1 employee
        :return: the data returned from the SOAP request
        """
        # Determine the client for the resources
        client = Client('https://api.visibox.nl/v1/resource?wsdl')
        # Get all the employee resources without filters
        if employee_id == None:
            request_body = {
                'authentication': {
                    'token': self.token
                },
                'humanResource': {
                    'resourceClass': 'PERSONNEL',
                    'humanResourceMatcher': {
                        'allowMultiple': 'true'
                    }
                }
            }
        else:
            request_body = {
                'authentication': {
                    'token': self.token
                },
                'humanResource': {
                    'resourceClass': 'PERSONNEL',
                    'humanResourceMatcher': {
                        'allowMultiple': 'true',
                        'number': employee_id
                    }
                }
            }
        response = client.service.getHumanResources(**request_body)['matcherResults']['matcherResult'][0]['entities']['entity']
        data = serialize_object(response)
        return data

    def get_departments(self):
        """
        Get all the departments from planning.nl. Only the departments, no employees etc.
        :return: the data returned from the SOAP request
        """
        client = Client('https://api.visibox.nl/v1/department?wsdl')
        request_body = {
            'authentication': {
                'token': self.token
            },
            'departmentMatcher': {
                'allowMultiple': 'true'
            }
        }
        response = client.service.getDepartments(**request_body)['matcherResults']['matcherResult'][0]['entities']['entity']
        data = serialize_object(response)
        return data

    def get_resource_sorts(self):
        """
        Get all the resource sorts which are used in the planning.nl environment. This could be the job descriptions for example
        :return: the data returned from the SOAP request
        """
        client = Client('https://api.visibox.nl/v1/resource?wsdl')
        request_body = {
            'authentication': {
                'token': self.token
            },
            'resourceSort': {
                'resourceClass': 'PERSONNEL',
                'resourceSortMatcher': {
                    'allowMultiple': 'true'
                }
            }
        }
        response = client.service.getResourceSorts(**request_body)['matcherResults']['matcherResult'][0]['entities']['entity']
        data = serialize_object(response)
        return data

    def get_resource_types(self):
        """
        Get all the resource types which are used in the planning.nl environment. This could be the departments for example
        :return: the data returned from the SOAP request
        """
        client = Client('https://api.visibox.nl/v1/resource?wsdl')
        request_body = {
            'authentication': {
                'token': self.token
            },
            'resourceType': {
                'resourceClass': 'PERSONNEL',
                'resourceTypeMatcher': {
                    'allowMultiple': 'true'
                }
            }
        }
        response = client.service.getResourceTypes(**request_body)['matcherResults']['matcherResult'][0]['entities']['entity']
        data = serialize_object(response)
        return data

    def get_human_departments(self):
        """
        Get the ID's of employees with their department ID's
        :return: the data returned from the SOAP request
        """
        client = Client('https://api.visibox.nl/v1/resource?wsdl')
        request_body = {
            'authentication': {
                'token': self.token
            },
            'resourceDepartment': {
                'resourceClass': 'PERSONNEL',
                'resourceDepartmentMatcher': {
                    'allowMultiple': 'true',
                    'humanResourceMatcher': {
                        'allowMultiple': 'true'
                    },
                    'departmentMatcher': {
                        'allowMultiple': 'true'
                    }
                }
            }
        }
        response = client.service.getResourceDepartments(**request_body)['matcherResults']['matcherResult'][0]['entities']['entity']
        data = serialize_object(response)
        return data

    def push_resource_sorts(self, resource_sort_number, resource_sort_description):
        """
        Push resource sorts to planning.nl
        :param resource_sort_number: The number of the resource. Watch out, this is not the ID of the resource sort. The ID is not needed
        :param resource_sort_description: The description of the resource sort
        :return: the data returned from the SOAP request
        """
        client = Client('https://api.visibox.nl/v1/resource?wsdl')
        request_body = {
            'authentication': {
                'token': self.token
            },
            'resourceSort': {
                'resourceClass': 'PERSONNEL',
                'resourceSortMatcher': {
                    'allowMultiple': 'true',
                    'number': resource_sort_number
                },
                'resourceSortValues': {
                    'number': resource_sort_number,
                    'description': resource_sort_description
                }
            }
        }
        response = client.service.pushResourceSorts(**request_body)
        data = serialize_object(response)
        return data

    def push_resource_types(self, resource_type_number, resource_type_description):
        """
        Push resource types to planning.nl
        :param resource_type_number: The number of the resource. Watch out, this is not the ID of the resource type. The ID is not needed
        :param resource_type_description: The description of the resource sort
        :return: the data returned from the SOAP request
        """
        client = Client('https://api.visibox.nl/v1/resource?wsdl')
        request_body = {
            'authentication': {
                'token': self.token
            },
            'resourceType': {
                'resourceClass': 'PERSONNEL',
                'resourceTypeMatcher': {
                    'allowMultiple': 'true',
                    'number': resource_type_number
                },
                'resourceTypeValues': {
                    'number': resource_type_number,
                    'description': resource_type_description
                }
            }
        }
        response = client.service.pushResourceTypes(**request_body)
        data = serialize_object(response)
        return data

    def push_human_recources(self, employee_id, job, department_number, department, first_name, last_name_prefix, last_name, phone_mobile, phone_fixed, street, zip_code, city, email, birth_date):
        client = Client('https://api.visibox.nl/v1/resource?wsdl')
        request_body = {
            'authentication': {
                'token': self.token
            },
            'humanResource': {
                'resourceClass': 'PERSONNEL',
                'humanResourceMatcher': {
                    'allowMultiple': 'true',
                    'number': employee_id
                },
                'humanResourceValues': {
                    'resourceType': {
                        'allowMultiple': 'true',
                        'description': job
                    },
                    'resourceSort': {
                        'allowMultiple': 'true',
                        'number': department_number,
                        'description': department
                    },
                    'number': employee_id,
                    'firstname': first_name,
                    'lastnamePrefix': last_name_prefix,
                    'lastname': last_name,
                    'phoneMobile': phone_mobile,
                    'phoneFixed': phone_fixed,
                    'streetName': street,
                    'postalCode': zip_code,
                    'city': city,
                    'email': email,
                    'birthDate': birth_date,
                    'doNotShowAsProjectLeader': 'true',
                    'doNotShowAsPhaseLeader': 'true'
                }
            }
        }
        response = client.service.pushHumanResource(**request_body)
        data = serialize_object(response)
        return data

    def logout(self):
        client = Client('https://api.visibox.nl/v1/authentication?wsdl')
        # Logout so that the token is destroyed. The logoutRequest key is mandatory but because there is no available value set a zeep.xsd.SkipValue
        request_body = {
            'authentication': {
                'token': self.token
            },
            'logoutRequest': zeep.xsd.SkipValue
        }
        response = client.service.logout(**request_body)
        return response