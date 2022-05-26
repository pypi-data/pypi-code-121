import json
import click
from tinybird.client import TinyB
from tinybird.tb_cli_modules.tinyunit.tinyunit_lib import DataUnitTest, customDataUnitTestDecoder, MyJSONEncoder
from os.path import exists
import requests
import glob
import urllib.parse


def test_load_file(test_file):
    existingDataList = []
    click.echo(f"Loading file {test_file}")
    if (not exists(test_file)):
        click.echo("Test file not found, creating...")
    else:
        with open(test_file) as fi:
            existingData = json.load(fi)
            for unit_data in existingData:
                unitDataTest = json.loads(unit_data, object_hook=customDataUnitTestDecoder)
                addedDataUnitTest = DataUnitTest(unitDataTest.id, unitDataTest.description, unitDataTest.enabled, unitDataTest.endpoint, unitDataTest.result, unitDataTest.time, unitDataTest.sql)
                existingDataList.append(addedDataUnitTest)

    return existingDataList


def test_write_file(test_file, inDataList):
    click.echo("Writing to file...")
    with open(test_file, 'w') as of:
        of.write(json.dumps(inDataList, cls=MyJSONEncoder, indent=4))


def test_file_add_test(tb_client: TinyB, file, endpoint, time, d, enabled, sql='', response=''):
    existingDataList = test_load_file(file)

    headers = {'Authorization': f'Bearer {tb_client.token}'}

    if(endpoint and len(endpoint) > 0):
        response = requests.get(endpoint, headers=headers)

    existingDataList.append(DataUnitTest(
        len(existingDataList),
        d,
        enabled,
        endpoint,
        response.text if endpoint else '',
        time,
        sql))

    test_write_file(file, existingDataList)
    return 0


def test_file_remove_test(file, testId):
    existingDataList = test_load_file(file)

    del existingDataList[testId]
    tmpList = []
    i = 0
    for tmp_unit_data in existingDataList:
        tmpDataUnitTest = DataUnitTest(i, tmp_unit_data.description, tmp_unit_data.enabled, tmp_unit_data.endpoint, tmp_unit_data.result, tmp_unit_data.time, tmp_unit_data.sql)
        tmpList.append(tmpDataUnitTest)
        i += 1
    existingDataList = tmpList

    test_write_file(file, existingDataList)
    return 0


def test_file_set_test_state(file, testId=None, newState=True):
    existingDataList = test_load_file(file)

    if(testId is None):
        for unitTest in existingDataList:
            unitTest.enabled = newState
    else:
        existingDataList[testId].enabled = newState

    test_write_file(file, existingDataList)
    return 0


def test_file_show_test(file, testId=None):
    existingDataList = test_load_file(file)

    if (testId is None):
        for unitTest in existingDataList:
            printDataUnitTest(unitTest)
    else:
        printDataUnitTest(existingDataList[testId])

    return 0


def test_file_reload_test(tb_client: TinyB, file, testId=None):
    existingDataList = test_load_file(file)

    headers = {'Authorization': f'Bearer {tb_client.token}'}

    if (testId is None):
        for unitTest in existingDataList:
            if(unitTest.endpoint):
                unitTest.result = requests.get(unitTest.endpoint, headers=headers).text
    else:
        existingDataList[testId].result = requests.get(existingDataList[testId].endpoint, headers=headers).text

    test_write_file(file, existingDataList)
    return 0


def printDataUnitTest(dataUnitTest):
    click.secho('Description:', fg='green', bold=True)
    click.echo(dataUnitTest.description)
    click.secho('Enabled:', fg='green', bold=True)
    click.echo(dataUnitTest.enabled)
    click.secho('Time:', fg='green', bold=True)
    click.echo(dataUnitTest.time)
    click.secho('SQL:', fg='green', bold=True)
    click.echo(dataUnitTest.sql)
    click.secho('Endpoint:', fg='green', bold=True)
    click.echo(dataUnitTest.endpoint)
    click.secho('Result:', fg='green', bold=True)
    click.echo(dataUnitTest.result)


def tinyUnitRunner(tb_client: TinyB):
    QUERY_API = f"{tb_client.host}/v0/sql?q="

    headers = {'Authorization': f'Bearer {tb_client.token}'}

    for file in glob.glob("./tests/*.json"):
        with open(glob.glob(file)[0]) as inputfile:
            data = json.load(inputfile)
            click.echo(f"->Running test from file {inputfile.name}")
            for unit_data in data:
                unitDataTest = json.loads(unit_data, object_hook=customDataUnitTestDecoder)
                if unitDataTest.enabled:
                    click.echo(f"\t->Running test: {unitDataTest.id} , {unitDataTest.description}")
                    if(unitDataTest.endpoint):
                        parsed = urllib.parse.urlparse(unitDataTest.endpoint)
                        replacedUrl = parsed._replace(netloc=getBareUrl(tb_client.host)).geturl()
                        response = requests.get(replacedUrl, headers=headers)
                        storedResponseJSON = json.loads(unitDataTest.result)
                        if response.status_code == 200:
                            click.echo("\t\t-->HTTP Response OK")
                        else:
                            click.echo("\t\t-->HTTP Response FAIL")
                            continue
                        requestedJson = json.loads(response.text)
                        if str(requestedJson["meta"]) == str(storedResponseJSON["meta"]):
                            click.echo("\t\t-->Meta Test OK")
                        else:
                            click.echo("\t\t-->Meta Test FAIL")

                        if str(requestedJson["data"]) == str(storedResponseJSON["data"]):
                            click.echo("\t\t-->Data Test OK")
                        else:
                            click.echo("\t\t-->Data Test FAIL")

                        if float(requestedJson["statistics"]["elapsed"]) * 1000 < unitDataTest.time:
                            click.echo("\t\t-->Time Test OK")
                        else:
                            click.echo("\t\t-->Time Test FAIL")
                    elif(unitDataTest.sql):
                        response = requests.get(QUERY_API + unitDataTest.sql, headers=headers)
                        if response.status_code == 200:
                            click.echo("\t\t-->HTTP Response OK")
                        else:
                            click.echo("\t\t-->HTTP Response FAIL")
                            continue
                        if(len(response.text) == 0):
                            click.echo("\t\t-->SQL Test OK")
                        else:
                            click.echo("\t\t-->SQL Test FAIL")


def getBareUrl(url):
    if url.startswith("http://"):
        return url[7:]
    elif url.startswith("https://"):
        return url[8:]
    else:
        return url
