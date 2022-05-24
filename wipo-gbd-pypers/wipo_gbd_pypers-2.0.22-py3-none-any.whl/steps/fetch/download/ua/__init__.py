from os.path import realpath, dirname
from pypers import import_all
import datetime
import json
import time
import os


def get_intervals(obj, changed=False):
    # get the date of the last update
    # expecting names like : 16.03.2020_x.json
    if len(obj.done_archives):
        last_update = obj.done_archives[-1]
        if '_' in last_update:
            last_update = last_update[0:last_update.find('_')]
        # add one day to the last update date
        last_update = datetime.datetime.strptime(
            last_update, '%d.%m.%Y')
        last_update = last_update.strftime('%d.%m.%Y')
    else:
        # if no done file, set last_update to yesterday
        last_update = (datetime.datetime.today() - datetime.timedelta(1)).strftime('%d.%m.%Y')

    today = datetime.datetime.today().strftime('%d.%m.%Y')
    prefix = 'app_date_%s'
    if changed:
        prefix = "last_update_%s"
    # get updates from the last one until today
    interval = {prefix % 'to': today,
                'page': obj.page}
    if last_update != '':
        interval[prefix % 'from'] = last_update
    # get updates f.ortnightly on the 12th and the 27th day of a month
    # Actually ranges should include the 10th and 25th of the month
    # (tested in march 2020)
    # https://sis.ukrpatent.org/api/v0/open-data/?changed=0&date_from=
    # 01.01.2019&date_to=31.12.2019&obj_type=4
    obj.logger.info('range to download %s to %s' % (last_update, today))
    return interval


def ger_per_type(obj, session, changed, marks_all_appnums, marks_file,
                 counter):
    # get updated trademarks
    interval = get_intervals(obj, changed=changed)
    params = ""
    for key in interval:
        params += "%s=%s&" % (key, interval[key])
    params = params[:len(params)-1]
    marks = []
    next_page = obj.api_url + params
    limit = 1000
    total = 0
    while next_page:
        time.sleep(.25)
        obj.logger.info('fetching: %s' % next_page)

        current_page = obj.get_updates(session, next_page,
                                       proxies=obj.proxy_params)

        marks_json = json.loads(current_page)
        for mark in marks_json.get('results', []):
            if mark['app_number'] not in marks_all_appnums:
                total += 1
                if obj.limit != 0 and total == obj.limit:
                    break
                marks_all_appnums.append(mark['app_number'])
                marks.append(mark)
                if len(marks) == limit:
                    f_name = "%s_%s.json" % (marks_file, counter)
                    with open(f_name, 'w') as fh:
                        fh.write(json.dumps(marks))
                    obj.output_files.append(f_name)
                    marks = []
                    counter += 1
        if obj.limit != 0 and total == obj.limit:
            break
        # goto next page if any
        next_page = marks_json.get('next', None)
    f_name = "%s_%s.json" % (marks_file, counter)
    with open(f_name, 'w') as fh:
        fh.write(json.dumps(marks))
    obj.output_files.append(f_name)
    counter += 1
    return counter


def ua_specific_api_process(obj, session):
    obj.output_files = []
    today = datetime.datetime.today().strftime('%d.%m.%Y')
    marks_file = os.path.join(obj.output_dir, '%s' % today)
    obj.last_date = [marks_file]
    # Create file for cleanup
    if not os.path.exists(marks_file):
        with open(marks_file, 'w') as f:
            pass
    # concat updated and new that is not in updated
    marks_all_appnums = []
    # 0 = new, 1 = update
    counter = 0
    for changed in [False, True]:
        counter = ger_per_type(obj, session, changed, marks_all_appnums,
                               marks_file, counter)

# Import all Steps in this directory.
import_all(namespace=globals(), dir=dirname(realpath(__file__)))
