from pydoc import html
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd

def convert(rqmsFile, outputFile='result'):
    try:
        with zipfile.ZipFile(rqmsFile, 'r') as ref:
            with ref.open('ter.properties') as f1, ref.open('ExecutionResult.xml') as f2:
                
                name = ''
                data = []
                ter = {}
                ns16 = '{http://jazz.net/xmlns/alm/qm/v0.1/executionresult/v0.1}'
                xhtml = '{http://www.w3.org/1999/xhtml}'

                for l in f1:
                    k,v = l.decode('utf8').partition("=")[::2]
                    ter[k.strip()] = v.strip()
                
                name = ter['execution.testscript.name']
                root = ET.XML(f2.read())
                el = root.findall(".//{}stepResult".format(ns16))
                for i, stepResult in enumerate(el):            
                    _description = stepResult.find(".//{}description/{}div".format(ns16, xhtml))
                    _expectedResult = stepResult.find(".//{}expectedResult/{}div".format(ns16, xhtml))
                    descriptionStr = ET.tostring(_description, encoding='unicode', method='text')
                    expectedResultStr = ET.tostring(_expectedResult, encoding='unicode', method='text')
                    data.append(((i + 1), descriptionStr, expectedResultStr))

                df = pd.DataFrame(data, columns=['Order', 'Description', 'ExpectedResult'])
                print("Converting...", "\n", name)
                df.to_excel(outputFile + '.xlsx')

    except FileNotFoundError:
        print('---> No such file or directory!')

    except KeyError:
        print('---> RQMS File not recognized!')

    except Exception as error:
        print('---> Exception Error!', error)
        raise error
