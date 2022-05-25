import math


def calculate_start_page(total_records, tail, records_per_page):
    if tail > total_records or total_records <= records_per_page:
        return 1
    total_pages_num = math.ceil(total_records / records_per_page)
    tail_pages_num = math.ceil((tail - total_records % records_per_page) / records_per_page)
    return total_pages_num - tail_pages_num


def calculate_start_index(total_records, tail, records_per_page):
    if tail > total_records:
        return 0
    offset_total = total_records % records_per_page
    offset_tail = tail % records_per_page
    return offset_total - offset_tail


def fetch_logs(api, params, tail):
    records_per_page = 30
    count = 0
    current_page = 1
    start_page = None

    params['sort'] = 'occurred_at'

    while True:
        params['page[number]'] = current_page
        result = api.access_logs.list(params=params)
        page_data = result.body['data']

        if tail:
            if not start_page:
                start_page = calculate_start_page(result.body['meta']['count'], tail, records_per_page)
                current_page = start_page
                if start_page != 1:
                    continue

            if current_page == start_page:
                start_index = calculate_start_index(result.body['meta']['count'], tail, records_per_page)
                page_data = page_data[start_index:]
            elif tail - count < records_per_page:
                page_data = page_data[:(tail - count)]

        yield page_data

        count += len(page_data)
        current_page += 1

        if not result.body['links'].get('next') or (tail and tail <= count):
            break


def prepare_filter(filter_options):
    result = {}
    for pair in filter_options.items():
        result['filter[{}]'.format(pair[0])] = pair[1]
    return result
