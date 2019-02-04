# benchmark:
# python3 -m timeit -s "from django.utils.dateparse import parse_datetime" "parse_datetime('2019-02-03T17:27:58.645194')"
# 10000 loops, best of 3: 32.7 usec per loop

# python3 -m timeit -s "import datetime" "datetime.datetime.strptime('2019-02-03T17:27:58.645194', '%Y-%m-%dT%H:%M:%S.%f')"
# 10000 loops, best of 3: 53.5 usec per loop

# python3 -m timeit -s   "import sys, os; sys.path.append(os.getcwd()); from datetime_heuristic_parser import datetime_heuristic_parser" "print(datetime_heuristic_parser('04/12/2018 09:7:4Z'))"
# 10000 loops, best of 3: 38.8 usec per loop
import datetime
import re
import pytz

DATE_FORMATS = ['%Y-%m-%d', 
                '%d/%m/%Y', 
                '%d/%m/%y']
DATETIME_FORMATS = ['%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%dT%H:%M:%S.%f', 
                    '%d/%m/%Y %H:%M:%S', 
                    '%d/%m/%y %H:%M:%S',
                    '%Y%m%d%H%M%SZ',
                    '%Y%m%d%H%M%S.%fZ',
                    '%Y-%m-%d-%H-%M-%S-%z',
                    '%d/%m/%Y %H:%M:%S%z']
# to be extended with all the matching patterns.
# get them from https://docs.python.org/3/library/time.html#time.strftime
DATETIME_ELEMENTS_REGEXP = {'%Y': '(?P<year>\d{4})',
                            '%y': '(?P<year>\d{2})',
                            '%m': '(?P<month>\d{1,2})',
                            '%d': '(?P<day>\d{1,2})',
                            '%H': '(?P<hour>\d{1,2})',
                            '%M': '(?P<minute>\d{1,2})',
                            '%S': '(?P<second>\d{1,2})',
                            '%f': '(?P<microsecond>\d{6})',
                            '%z': '(?P<tzinfo>(Z)|([\sz\+\-]*)?[\d:]+)',
                            # '%Z': EST, UTC... many others to do,
                            } # ...


def datetime_regexp_builder(formats):
    """
    formats = DATE_FORMAT of DATETIME_FORMAT
    """
    regexp_dict = {}
    for df in formats:
        df_regexp = df
        for k,v in DATETIME_ELEMENTS_REGEXP.items():
            df_regexp = df_regexp.replace(k,v)
        regvalue = df_regexp+'$' 
        regexp_dict[df] = regvalue
    return regexp_dict

DATE_FORMATS_REGEXP = datetime_regexp_builder(DATE_FORMATS)
DATETIME_FORMATS_REGEXP = datetime_regexp_builder(DATETIME_FORMATS)


class FixedOffset(datetime.tzinfo):
    """
    Fixed offset in minutes east from UTC. Taken from Python's docs.

    Kept as close as possible to the reference version. __init__ was changed
    to make its arguments optional, according to Python's requirement that
    tzinfo subclasses can be instantiated without arguments.
    """

    def __init__(self, offset=None, name=None):
        if offset is not None:
            self.__offset = datetime.timedelta(minutes=offset)
        if name is not None:
            self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO

    @classmethod
    def get_fixed_timezone(cls, offset):
        """Return a tzinfo instance with a fixed offset from UTC."""
        if isinstance(offset, datetime.timedelta):
            offset = offset.total_seconds() // 60
        sign = '-' if offset < 0 else '+'
        hhmm = '%02d%02d' % divmod(abs(offset), 60)
        name = sign + hhmm
        return cls(offset, name)

def dformat_insp(date_str, format_regexp_dict, debug=False):
    """
    Takes a date string and returns a matching date regexp. 
    """
    insp_formats = []
    for f,p in format_regexp_dict.items():
        if debug: print(date_str, f, p)
        match = re.match(p, date_str)
        if match:
            res = (f, p, {k:v for k,v in match.groupdict().items()})
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
    if not res: raise Exception(ValueError)
    res_dicts_list = []
    for i in res:
        dt_dict = i[-1]
        # timezone extraction
        tzinfo = None
        if dt_dict.get('tzinfo'):
            tzinfo = dt_dict.pop('tzinfo')
            if tzinfo == 'Z':
                tzinfo = datetime.timezone.utc
            elif tzinfo is not None:
                offset_mins = int(tzinfo[-2:]) if len(tzinfo) > 3 else 0
                offset = 60 * int(tzinfo[1:3]) + offset_mins
                if tzinfo[0] == '-':
                    offset = -offset
                tzinfo = FixedOffset.get_fixed_timezone(offset)
        dt_dict = {k: int(v) for k, v in dt_dict.items()}
        res_dicts_list.append(dt_dict)
        if tzinfo: dt_dict['tzinfo'] = tzinfo
    return [datetime.datetime(**i) for i in res_dicts_list]

# example
if __name__ == '__main__':
    tests = ['04/12/2018',
             '04/12/2018 3:2:1',
             '2018-03-4 09:7:4',
             '2018-03-04T09:7:4.645194',
             '20180304121940.948000Z',
             '2018-04-18-17-04-30-+01:00',
             '04/12/2018 09:7:4Z']
    
    for i in tests: 
        res = dateformat_insp(i) or datetimeformat_insp(i)
        if res:
            print('Parsing succesfull on "{}": {}'.format(i, res))
            print(datetime_heuristic_parser(i))
        else:
            print('Parsing failed on "{}"'.format(i))
            print(DATETIME_ELEMENTS_REGEXP['%z'])
            raise Exception('Not a date or datetime')
        print()
