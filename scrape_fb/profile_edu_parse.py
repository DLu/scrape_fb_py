import re

YEAR = re.compile('\d\d\d\d')

DEGREES = ['phd', 'ms', 'md', 'ma', 'ba', 'master', 'masters', 'jd', 'mfa', 'mba', 'dvm', 'mm', 'med', 'msc', 'msw',
           'doctor', 'mph', 'bachelor', 'bs', 'mat', 'msci', 'mme', 'mse', 'od', 'psyd', 'dpt']
MAJORS = ['computer science', 'medicine', 'biology', 'robotics', 'mathematics', 'biochemistry', 'psychology',
          'neuroscience', 'chemistry', 'theatre', 'physics', 'law', 'nursing', 'english language', 'music', 'history',
          'political science', 'music education', 'molecular genetics']


def multi_split(s, splitters):
    parts = [s]
    for splitter in splitters:
        new_parts = []
        for s in parts:
            for sub in s.split(splitter):
                if len(sub) == 0:
                    continue
                new_parts.append(sub)
        parts = new_parts
    return parts


def is_degree(s):
    if type(s) == list:
        return False
    ss = s.lower().replace('.', '')
    if ss in DEGREES:
        return True
    chunks = multi_split(ss, ['/', ', ', ' '])
    first = chunks[0].strip()
    if first in DEGREES:
        return True
    return False


def parse_major(s):
    if type(s) == list:
        return None
    match = None
    chunks = multi_split(s, [' and ', ', '])
    for chunk in chunks:
        ss = chunk.strip().lower()
        if ss in MAJORS or 'engineering' in ss:
            match = ss
    if match:
        return chunks
    else:
        return None


def parse_education_field(el):
    if 'Class of' in el:
        return 'class_of', int(el.replace('Class of ', ''))
    elif type(el) == list and u'\xb7' in el:
        return 'field', [a for a in el if a != u'\xb7']
    elif el in ['High School', 'College', 'Graduate School']:
        return 'type', el
    elif is_degree(el):
        return 'degree', el
    elif ' - ' in el:
        a, _, b = el.partition(' - ')
        if YEAR.search(a) and (YEAR.search(b) or b == 'Present'):
            return 'when', el
    elif type(el) in [str, unicode] and YEAR.search(el):
        return 'when', el
    m = parse_major(el)
    if m is not None:
        return 'field', m
    return None, None


FIELD_BITS = [[None, 'class_of'], [None, 'when'], ['degree', None, 'class_of'], ['degree', None, 'when'],
              ['degree', None], [None]]


def parse_school(line):
    school = {}
    if type(line[0]) == dict:
        school['name'] = line[0]['contents']
        school['link'] = line[0]['link']
    else:
        school['name'] = line[0]
    pattern = []
    for el in line[1:]:
        key, val = parse_education_field(el)
        if key:
            if key in school and school[key] != val:
                if type(val) == list and type(school[key]) == list:
                    school[key] += val
                else:
                    print 'overwrite field', key, val, school[key]
            school[key] = val
            pattern.append(key)
        else:
            if 'unparsed_bits' not in school:
                school['unparsed_bits'] = []
            school['unparsed_bits'].append(el)
            pattern.append(None)
    if pattern == [None, None, 'class_of']:
        school['degree'], school['field'] = school['unparsed_bits']
        del school['unparsed_bits']
    elif pattern == [None, 'class_of', None]:
        school['field'], school['note'] = school['unparsed_bits']
        del school['unparsed_bits']
    elif pattern in FIELD_BITS:
        school['field'] = school['unparsed_bits'][0]
        del school['unparsed_bits']
    elif pattern == [None, 'field', 'class_of']:
        school['degree'] = school['unparsed_bits'][0]
        del school['unparsed_bits']
    elif 'unparsed_bits' in school and len(school['unparsed_bits']) == 1 and pattern[-1] is None:
        school['note'] = school['unparsed_bits'][0]
        del school['unparsed_bits']

    return school
