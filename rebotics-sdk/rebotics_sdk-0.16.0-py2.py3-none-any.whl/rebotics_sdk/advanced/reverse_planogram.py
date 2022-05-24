from datetime import datetime

import pandas as pd
import numpy as np


PLANOGRAM_COLUMNS = [
    'planogram_number', 'planogram_title',
    'category_number', 'category_title',
    'bay_report_id',
    'aisle', 'section', 'shelf', 'shelf_position',
    'x', 'y',
    'upc', 'product_name',
]


def make_planogram_df(scan_data, planogram_number=None):
    if planogram_number is None:
        planogram_number = 'reverse_planogram_scan_{}'.format(scan_data['id'])

    products_map = {
        c["upc"]: c for c in scan_data['plu']
    }

    bay_map = {
        sb["id"]: sb for sb in scan_data['shelf_bays']
    }
    store = scan_data['store']

    flattened = []
    for item in scan_data['items']:
        product = products_map.get(item['upc'])
        flattened.append({
            'planogram_number': planogram_number,
            'planogram_title': planogram_number,
            'store_id': store.get('custom_id'),
            'category_number': scan_data.get('category_number'),
            'category_title': scan_data.get('category_title'),
            'bay_report_id': item['shelf_bay_id'],
            'aisle': bay_map[item['shelf_bay_id']]['aisle'],
            'section': bay_map[item['shelf_bay_id']]['section'],
            'shelf': item['display_shelf'],
            'shelf_position': item['position'],
            'x': item['x'],
            'y': item['y'],
            'upc': item['upc'],
            'product_name': product.get('title', "") if product else ""
        })

    df = pd.DataFrame(flattened, columns=PLANOGRAM_COLUMNS, index=None, dtype=np.dtype(object))
    pog_d = dict()

    for i, item in df.iterrows():
        key = "{aisle}|{section}|{shelf}|{x}|{upc}".format(
            aisle=item['aisle'],
            section=item['section'],
            shelf=item['shelf'],
            x=item['x'],
            upc=item['upc'],
        )
        d = pog_d.get(key)
        if d is None:
            item['facings_high'] = 1
            pog_d[key] = item
        else:
            d['facings_high'] = d.get('facings_high', 1) + 1

    df['facings_wide'] = 1
    df['facings_deep'] = 1
    df['facing_type'] = 'item'
    df['section_direction'] = 'left_to_right'
    df['shelf_direction'] = 'top_to_down'
    df['position_direction'] = 'left_to_right'
    df['from_date'] = datetime.now().strftime("%Y-%m-%d")
    df['is_zig_zag'] = 0
    return df
