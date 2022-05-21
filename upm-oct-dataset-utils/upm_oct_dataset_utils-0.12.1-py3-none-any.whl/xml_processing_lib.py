
import json
from .dataset_classes import RawDataset, StudyDate
import pandas_read_xml as pdx

class XMLError(Exception):
    pass

def process_xmlscans(xml_path, study_date:StudyDate, scans_to_process:list) -> dict:
    std_date = study_date.as_str(sep='-', year_first=True)
    xml_df = pdx.read_xml(xml_path)
    json_str = xml_df.to_json(indent=4)
    xml_dict = json.loads(json_str)
    studies = xml_dict["ExportSchema"]["0"].pop("PATIENT")["VISITS"]["STUDY"]
    if type(studies) is dict:
        studies = [studies]
    processed_scans = {}; pdates = {}
    for scan in scans_to_process:
        for study in studies:
            if std_date != study['VISIT_DATE']: continue 
            series = study["SERIES"]
            if series is None: continue
            scans = series["SCAN"]
            if type(scans) is dict:
                scans = [scans]
            oct_type, zone, eye = scan.split("_")
            protocol = RawDataset.zones[zone]["adquisitions_name"][oct_type]
            for sc in scans:
                raw_scan_date = sc['DATE_TIME']; splitted_date = raw_scan_date.split("T")
                scan_date = splitted_date[0]+"-"+splitted_date[1].replace(":", "-")
                add_flag = True
                try:
                    date1 = pdates[scan]
                except: pass
                else:
                    if date1 > scan_date:
                        add_flag = False
                if sc['PROTOCOL'] == protocol and sc["SITE"] == eye and add_flag:
                    if "TRACKINGDETAILS" in sc:
                        sc.pop("TRACKINGDETAILS")
                    processed_scans[scan] = sc
                    pdates[scan] = scan_date
    # xml_dict.update(processed_scans)
    return processed_scans