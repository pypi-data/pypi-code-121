import gspread


def fetch_from_google_sheet(spreadsheet_id, strings_map):
    gc = gspread.oauth(credentials_filename='credentials.json')
    wks = gc.open_by_key(spreadsheet_id).sheet1
    
    items = wks.get_all_values()
    languages = items.pop(0)
    for item in items:
        key = item[0]
        for index, translation in enumerate(item):
            if translation:
                strings_map.update(key, languages[index], translation)


def upload_to_google_sheet(spreadsheet_id, strings_map, languages):
    gc = gspread.oauth(credentials_filename='credentials.json')
    wks = gc.open_by_key(spreadsheet_id).sheet1
    wks.clear()
    rows = [["en", *languages]]
    for index in strings_map.index.values():
        row = [index.value]
        for language, translation in index.translations.items():
            if language in languages:
                row.append("" if translation == index.value else translation)
        rows.append(row)
    wks.insert_rows(rows)
