# benchmark:
# python -m timeit -s "from django.utils.dateparse import parse_datetime" "parse_datetime('2019-02-03T17:27:58.645194')"
# 10000 loops, best of 3: 32.7 usec per loop

# python -m timeit -s "import datetime" "datetime.datetime.strptime('2019-02-03T17:27:58.645194', '%Y-%m-%dT%H:%M:%S.%f')"
# 10000 loops, best of 3: 53.5 usec per loop

# python -m timeit -s "from datetime_euristic_parser. import datetime_heuristic_parser; datetime_heuristic_parser('2019-02-03T17:27:58.645194')"
# 10000000 loops, best of 3: 0.0241 usec per loop
import re
import datetime

DATE_FORMATS = ['%Y-%m-%d', 
                '%d/%m/%Y', 
                '%d/%m/%y']
DATETIME_FORMATS = ['%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%dT%H:%M:%S.%f', 
                    '%d/%m/%Y %H:%M:%S', 
                    '%d/%m/%y %H:%M:%S',
                    '%Y%m%d%H%M%SZ',
                    '%Y%m%d%H%M%S.%fZ']
# to be extended with all the matching patterns.
DATETIME_ELEMENTS_REGEXP = {'%Y': '(?P<year>\d{4})',
                            '%y': '(?P<year>\d{2})',
                            '%m': '(?P<month>\d{1,2})',
                            '%d': '(?P<day>\d{1,2})',
                            '%H': '(?P<hour>\d{1,2})',
                            '%M': '(?P<minute>\d{1,2})',
                            '%S': '(?P<second>\d{1,2})',
                            '%f': '(?P<microsecond>\d{6})'} # ...
                     
def datetime_regexp_builder(formats):
    """
    formats = DATE_FORMAT of DATETIME_FORMAT
    """
    regexp_dict = {}
    for df in formats:
        df_regexp = df
        for k,v in DATETIME_ELEMENTS_REGEXP.items():
            df_regexp = df_regexp.replace(k,v)
        regexp_dict[df] = df_regexp+'$'
    return regexp_dict

DATE_FORMATS_REGEXP = datetime_regexp_builder(DATE_FORMATS)
DATETIME_FORMATS_REGEXP = datetime_regexp_builder(DATETIME_FORMATS)

def dformat_insp(date_str, format_regexp_dict, debug=False):
    """
    Takes a date string and returns a matching date regexp. 
    """
    insp_formats = []
    for f,p in format_regexp_dict.items():
        if debug: print(date_str, f, p)
        match = re.match(p, date_str)
        if match:
            res = (f, p, {k:int(v) for k,v in match.groupdict().items()})
            insp_formats.append(res)
    return insp_formats

def dateformat_insp(date_str):
    return dformat_insp(date_str, DATE_FORMATS_REGEXP)

def datetimeformat_insp(date_str):
    return dformat_insp(date_str, DATETIME_FORMATS_REGEXP)

def datetime_heuristic_parser(value):
    """
    value can be a datestring or a datetimestring
    returns all the parsed date or datetime object
    """
    res = dateformat_insp(value) or \
          datetimeformat_insp(value)
    return [datetime.datetime(**i[-1]) for i in res]

# example
if __name__ == '__main__':
    tests = ['04/12/2018',
             '04/12/2018 3:2:1',
             '2018-03-4 09:7:4',
             '2018-03-04T09:7:4.645194',
             '20180304121940.948000Z']
    
    for i in tests: 
        res = dateformat_insp(i) or datetimeformat_insp(i)
        if res:
            print('Parsing succesfull on "{}": {}'.format(i, res))
            #print(datetime_heuristic_parser(i))
        else:
            print('Parsing failed on "{}"'.format(i))
            raise Exception('Not a date or datetime')
        print()
