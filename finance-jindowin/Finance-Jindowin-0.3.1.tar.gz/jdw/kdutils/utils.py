import dateutil.parser as dt_parser
import pdb
def convert_date(date, format='%Y-%m-%d'):
    try:
        unicode
    except:
        unicode = str
    try:
        if isinstance(date, (str, unicode)):
            date = dt_parser.parse(date)
    except Exception as e:
        raise Exception('date:{}格式不能识别。'%date)
    return date.strftime(format)