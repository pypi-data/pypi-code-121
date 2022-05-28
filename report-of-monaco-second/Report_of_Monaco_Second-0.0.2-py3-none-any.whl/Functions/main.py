from datetime import datetime
import argparse
import os.path
from operator import itemgetter

FORMAT_DATE = "%Y-%m-%d_%I:%M:%S.%f"

START_LOG = "/start.log"
END_LOG = "/end.log"
ABBR_TXT = "/abbreviations.txt"


def get_files_paths(dir_path):
    path_files = [START_LOG, END_LOG, ABBR_TXT]
    files_path = ()
    for i in path_files:
        full_path = os.path.join(dir_path + i)
        if not os.path.exists(full_path):
            print(f'File {i} not found.')
            exit()

        files_path += (full_path,)

    return files_path


def open_log_file(path_to_file):
    with open(path_to_file, "r") as report:
        data = report.readlines()
        racer_report = {}
        for i in data:
            i = i.strip()
            racer = i[:3]
            racer_report[racer] = datetime.strptime(i[3:], FORMAT_DATE)
        return racer_report


def open_abbr_file(path_to_file):
    with open(path_to_file, "r") as abbreviations:
        data_abbr = abbreviations.readlines()
        abbr_dict = {}

        for i in data_abbr:
            abbr, name, team = i.strip().split("_")
            abbr_dict[abbr] = (name, team)
        return abbr_dict


def get_time_delta():
    racer_start_report = open_log_file("../Data/start.log")
    racer_end_report = open_log_file("../Data/end.log")
    racer_result = {}
    for key, date in racer_start_report.items():
        racer_time_end = racer_end_report[key]
        racer_time_start = racer_start_report[key]
        if racer_time_end > racer_time_start:
            result = racer_time_end - racer_time_start
        else:
            result = f"{racer_time_end - racer_time_start} -- invalid value"
        racer_result[key] = str(result)
    return racer_result


def build_report():
    racer_result = get_time_delta()
    sorted_racer_time = dict(sorted(racer_result.items(), key=lambda x: x[1]))
    abbr_dict = open_abbr_file("../Data/abbreviations.txt")
    results = []
    for i, k in abbr_dict.items():
        results += [(abbr_dict[i][0], abbr_dict[i][1], sorted_racer_time[i])]
    sorted_results = sorted(results, key=itemgetter(2))
    return sorted_results


def print_report():
    res = ""
    print_results = build_report()
    for k in enumerate(print_results, 1):
        res += f'{k[0]} {k[1][0]}   | {k[1][1]}   | {k[1][2]}\n'
        if k[0] == 15:
            res += ("_" * 80 + "\n")
    print(res)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--files_dir", help="folder_path")
    parser.add_argument("--driver", help="Enter driver's name")
    parser.add_argument("--asc", help="Optional")
    args = parser.parse_args()
    if args.files_dir:
        print(get_files_paths(args.files_dir))
    elif args.driver:
        stat = build_report()
        for k in enumerate(stat, 1):
            place = k[0]
            driver = k[1][0]
            team = k[1][1]
            time = k[1][2]
            if args.driver == driver:
                print(f"Driver: {driver}\nPlace:  {place}\nTeam:   {team}\nTime:   {time}")
    elif args.asc:
        stat = build_report()
        for i in stat:
            print(i[0])


if __name__ == '__main__':
    main()
    print(build_report())
