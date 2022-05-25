import os
import json
import yaml
import csv
import jmespath
from .logger import Logger
from .exceptions import DSOException
from .cli_constants import *
from functools import reduce



def format_data(data, query, format, compress=True, mainkeys=None):
    def compress_single_element_lists(data):
        if not isinstance(data, list): return data
        if len(data) > 1: return data
        return compress_single_element_lists(data[0])

    if not data: return ''

    if query:
        import jmespath
        result = jmespath.search(query, data)
    else:
        result = data

    if compress: result = compress_single_element_lists(result)

    if not result: return ''

    if format == 'json':
        import json
        return json.dumps(result, sort_keys=False, indent=2)

    elif format == 'yaml':
        import yaml
        return yaml.dump(result, sort_keys=False, indent=2)

    ### expects list(dict), or a dict, otherwise best-effort
    elif format in 'csv':
        import io
        import csv
        output = io.StringIO()
        writer = csv.writer(output)
        if isinstance(result, list) and len(result):
            if isinstance(result[0], dict):
                writer.writerow(result[0].keys())
                for item in result:
                    writer.writerow(item.values())
            else:
                writer.writerow(result)
        elif isinstance(result, dict) and len(result):
            keys = list(result.keys())
            ### if data is dictionary with single key whose value is a list, process the child list instead
            if len(keys) == 1:
                childList = result[keys[0]]
                if isinstance(childList, list) and len(childList):
                    if isinstance(childList[0], dict):
                        writer.writerow(childList[0].keys())
                        for item in childList:
                            writer.writerow(item.values())
                    else:
                        writer.writerow(childList)
                else:
                    writer.writerow(keys)
                    writer.writerow(result.values())
            elif len(keys) > 1:
                writer.writerow(keys)
                writer.writerow(result.values())
        else:
            writer.writerow(result)
        
        return output.getvalue()

    elif format in 'tsv':
        import io
        import csv
        output = io.StringIO()
        writer = csv.writer(output, delimiter='\t')
        if isinstance(result, list) and len(result):
            if isinstance(result[0], dict):
                writer.writerow(result[0].keys())
                for item in result:
                    writer.writerow(item.values())
            else:
                writer.writerow(result)
        elif isinstance(result, dict) and len(result):
            keys = list(result.keys())
            ### if data is dictionary with single key whose value is a list, process the child list instead
            if len(keys) == 1:
                childList = result[keys[0]]
                if isinstance(childList, list) and len(childList):
                    if isinstance(childList[0], dict):
                        writer.writerow(childList[0].keys())
                        for item in childList:
                            writer.writerow(item.values())
                    else:
                        writer.writerow(childList)
                else:
                    writer.writerow(keys)
                    writer.writerow(result.values())
            elif len(keys) > 1:
                writer.writerow(keys)
                writer.writerow(result.values())
        else:
            writer.writerow(result)
        
        return output.getvalue()

    ### tab separated with no headers
    ### expects list(dict), or a dict, otherwise best-effort
    elif format == 'text':
        outputStream = ''
        if isinstance(result, list):
            for i in range(0, len(result)):
                item = result[i]
                if isinstance(item, dict):
                    ### the map also treats None values
                    valuesStr = '\t'.join(map(lambda x: str(x) if not x is None else '', list(item.values())))
                else:
                    valuesStr = str(item) if not item is None else ''
                outputStream += f"{valuesStr}"
                if i < len(result)-1: outputStream += '\n'
        elif isinstance(result, dict):
            keys = list(result.keys())
            ### if data is dictionary with single key whose value is a list, process the child list instead
            if len(keys) == 1:
                childList = result[keys[0]]
                if isinstance(childList, list):
                    for i in range(0, len(childList)):
                        item = childList[i]
                        if isinstance(item, dict):
                            valuesStr = '\t'.join(map(lambda x: str(x) if not x is None else '', list(item.values())))
                        else:
                            valuesStr = str(item) if not item is None else ''
                        outputStream += f"{valuesStr}"
                        if i < len(childList)-1: outputStream += '\n'
                else:
                    outputStream = '\t'.join(map(lambda x: str(x) if not x is None else '', list(result.values())))
            elif len(keys) > 1:
                outputStream = '\t'.join(map(lambda x: str(x) if not x is None else '', list(result.values())))
        else:
            outputStream += str(result) if not result is None else ''
        
        return outputStream


    ### expects list(dict), or a dict
    ### take first key as name and second key as value, or use mainkeys and form name=value
    elif format == 'compact':

        def quote(value):
            if not value: return ''
            import re
            value = str(value)
            ### no quoting numbers
            if re.match(r"^[0-9]$", value) or re.match(r"^[1-9][0-9]*$", value) or re.match(r"^[0-9]*\.[0-9]+$", value):
                return value
            ### double quote if contains single quote
            elif re.match(r"^.*[']+.*$", value):
                return f'"{value}"'
            ### sinlge quote by default
            else:
                return f"'{value}'"

        outputStream = ''
        if isinstance(result, list) and len(result):
            if isinstance(result[0], dict):
                if len(result[0].keys()) < 2:
                    raise DSOException(f"Unable to format data as it is incompatible with the 'compact' format.")
                for item in result:
                    if not mainkeys:
                        mainkeys = list(item.keys())
                    key = item[mainkeys[0]]
                    value = quote(item[mainkeys[1]])
                    outputStream += f"{key}={value}\n"
            else:
                raise DSOException(f"Unable to format data as it is incompatible with the 'compact' format.")
        elif isinstance(result, dict):
            keys = list(result.keys())
            ### if data is dictionary with single key whose value is a list, process the child list instead
            if len(keys) == 1:
                childList = result[keys[0]]
                if isinstance(childList, list):
                    if childList:
                        if len(childList[0].keys()) < 2:
                            raise DSOException(f"Unable to format data as it is incompatible with the 'compact' format.")
                        for item in childList:
                            if not mainkeys:
                                mainkeys = list(item.keys())
                            key = item[mainkeys[0]]
                            value = quote(item[mainkeys[1]])
                            outputStream += f"{key}={value}\n"
                else:
                    raise NotImplementedError()
            elif len(keys) > 1:
                raise NotImplementedError()
        else:
            raise DSOException(f"Unable to format data as it is incompatible with the 'compact' format.")
        return outputStream

    else:
        raise DSOException(f"Output format '{format}' is not supported.")



def read_data(input, parent_key, keys, format):
    result = []
    if format == 'json':
        try:
            if parent_key:
                data = json.load(input)[parent_key]
            else:
                data = json.load(input)
        # except json.JSONDecodeError as e:
        except:
            raise DSOException(CLI_MESSAGES['InvalidFileFormat'].format(format))

        if not data: return []

        if keys == ['*']: 
            keys = data[0].keys()
        else:
            for key in keys:
                if not key in data[0].keys():
                    raise DSOException(CLI_MESSAGES['MissingField'].format(key))

        for row in data:
            record = {}
            for key in keys:
                record[key] = row[key]
            result.append(record)

    elif format == 'yaml':
        try:
            if parent_key:
                data = yaml.load(input, yaml.SafeLoader)[parent_key]
            else:
                data = yaml.load(input, yaml.SafeLoader)
        # except yaml.YAMLError as e:
        except:
            raise DSOException(CLI_MESSAGES['InvalidFileFormat'].format(format))

        if not data: return []

        if keys == ['*']: 
            keys = data[0].keys()
        else:
            for key in keys:
                if not key in data[0].keys():
                    raise DSOException(CLI_MESSAGES['MissingField'].format(key))

        for row in data:
            record = {}
            for key in keys:
                record[key] = row[key]
            result.append(record)
            
    elif format == 'csv':
        if parent_key: 
            raise NotImplementedError()

        try:
            data = list(csv.reader(input))
        except:
            raise DSOException(CLI_MESSAGES['InvalidFileFormat'].format(format))

        if not data: return []

        if keys == ['*']: 
            keys = data[0]
        else:
            header = data[0]
            if len(header) < len(keys):
                raise DSOException(CLI_MESSAGES['InvalidFileFormat'].format(format))

            for i in range(0, len(keys)):
                key = keys[i]
                if not key == header[i]:
                    raise DSOException(CLI_MESSAGES['MissingField'].format(key))

        for row in data[1:]:
            record = {}
            for i in range(0, len(keys)):
                record[keys[i]] = row[i]
            result.append(record)

    elif format == 'tsv':
        if parent_key: 
            raise NotImplementedError()

        try:
            data = list(csv.reader(input, delimiter='\t'))
        except:
            raise DSOException(CLI_MESSAGES['InvalidFileFormat'].format(format))

        if not data: return []

        if keys == ['*']: 
            keys = data[0]
        else:
            header = data[0]
            if len(header) < len(keys):
                raise DSOException(CLI_MESSAGES['InvalidFileFormat'].format(format))

            for i in range(0, len(keys)):
                key = keys[i]
                if not key == header[i]:
                    raise DSOException(CLI_MESSAGES['MissingField'].format(key))

        for row in data[1:]:
            record = {}
            for i in range(0, len(keys)):
                record[keys[i]] = row[i]
            result.append(record)

    elif format == 'text':
        if parent_key: 
            raise NotImplementedError()

        if keys == ['*']: 
            raise NotImplementedError()

        data = input.readlines()
        try:
            for row in data:
                record = {}
                for i in range(0, len(keys)):
                    record[keys[i]] = row.split('\t')[i].strip()
                result.append(record)
        except:
            raise DSOException(CLI_MESSAGES['InvalidFileFormat'].format(format))

    elif format == 'compact':
        if keys == ['*']: 
            raise NotImplementedError()

        data = input.readlines()
        try:
            for row in data:
                record = {}
                for i in range(0, len(keys)):
                    if not '=' in row:
                        raise DSOException(CLI_MESSAGES['InvalidFileFormat'].format(format))
                    record[keys[i]] = row.split('=')[i].strip()
                result.append(record)
        except:
            raise DSOException(CLI_MESSAGES['InvalidFileFormat'].format(format))

    
    return result



# def validate_multiple_argument(ctx, param, value):
#     if len(value) > 1:
#         raise DSOException(f"Multiple '{param.name}' {type(param)} is not allowd.")


def validate_provided(value, name, causes=[]):

    test = not bool(value)
    if test:
        print(CLI_MESSAGES['TryHelp'])
        if causes:
            raise DSOException(CLI_MESSAGES['ArgumentsProvidedBecause'].format(', '.join(causes), name))
        else:
            raise DSOException(CLI_MESSAGES['MissingArgument'].format(name))
    
    return value



### opposite validate_not_all_provided
def validate_all_provided(values, names, causes=[]):

    test = not reduce(lambda x, y: bool(x) and bool(y), values)
    if test:
        print(CLI_MESSAGES['TryHelp'])
        if causes:
            raise DSOException(CLI_MESSAGES['ArgumentsAllProvidedBecause'].format(', '.join(causes), ', '.join(names)))
        else:
            raise DSOException(CLI_MESSAGES['ArgumentsAllProvided'].format(', '.join(names)))
    
    # return list(filter(lambda i: not bool(values[i]), range(len(values))))



### opposite validate_all_provided
def validate_not_all_provided(values, names, causes=[]):

    test = reduce(lambda x, y: bool(x) and bool(y), values)
    if test:
        print(CLI_MESSAGES['TryHelp'])
        if causes:
            raise DSOException(CLI_MESSAGES['ArgumentsNotAllProvidedBecause'].format(', '.join(causes), ', '.join(names)))
        else:
            raise DSOException(CLI_MESSAGES['ArgumentsNotAllProvided'].format(', '.join(names)))
    
    # return list(filter(lambda i: bool(values[i]), range(len(values))))
    return reduce(lambda x, y: x or y, values)



### opposite validate_at_least_one_provided
def validate_none_provided(values, names, causes=[]):

    test = reduce(lambda x, y: bool(x) or bool(y), values)
    if test:
        print(CLI_MESSAGES['TryHelp'])
        if causes:
            raise DSOException(CLI_MESSAGES['ArgumentsNoneProvidedBecause'].format(', '.join(causes), ', '.join(names)))
        else:
            raise DSOException(CLI_MESSAGES['ArgumentsNoneProvided'].format(', '.join(names)))
    
    # return list(filter(lambda i: bool(values[i]), range(len(values))))



### opposite validate_none_provided
def validate_at_least_one_provided(values, names, causes=[]):

    test = not reduce(lambda x, y: bool(x) or bool(y), values)
    if test:
        print(CLI_MESSAGES['TryHelp'])
        if causes:
            raise DSOException(CLI_MESSAGES['ArgumentsAtLeastOneProvidedBecause'].format(', '.join(causes), ', '.join(names)))
        else:
            raise DSOException(CLI_MESSAGES['ArgumentsAtLeastOneProvided'].format(', '.join(names)))


    return reduce(lambda x, y: x or y, values)



def validate_only_one_provided(values, names, causes=[]):
    validate_not_all_provided(values, names, causes)
    return validate_at_least_one_provided(values, names, causes)



def validate_query_argument(query, query_all, default_query):
    
    validate_not_all_provided([query, query_all], ["'-q' / '--query'", "'-a' / '--query-all'"])
    # if query and query_all:
    #     print(CLI_MESSAGES['TryHelp'])
    #     raise DSOException((CLI_MESSAGES['ArgumentsMutualExclusive'].format(""'-q' / '--query' + casue)", '-a' / '--query-all'"))

    if query_all:
        _query = ''
    elif not query:
        _query = default_query
    else:
        _query = query

    if _query:
        try:
            jmespath.compile(_query)
        except jmespath.exceptions.ParseError as e:
            raise DSOException(f"Invalid JMESPath query '{_query}': {e.msg}")
    
    return _query



def transform_context_overrides(namespace, application):
    result = ''
    if namespace: 
        result += f"namespace={namespace},"
    elif 'DSO_NAMESPACE' in os.environ:
        Logger.debug("Environment variable 'DSO_NAMESPACE' found.")
        result += f"namespace={os.getenv('DSO_NAMESPACE')},"
    if application: 
        result += f"application={application},"
    elif 'DSO_APPLICATION' in os.environ:
        Logger.debug("Environment variable 'DSO_APPLICATION' found.")
        result += f"application={os.getenv('DSO_APPLICATION')},"
    
    return result
