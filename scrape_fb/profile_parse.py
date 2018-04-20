from bs4 import BeautifulSoup
from .simplify import simplify, force_structure, create_recursive_dict
from .profile_edu_parse import parse_school


def parse_profile(raw_html):
    profile = {}
    content = BeautifulSoup(raw_html, 'html.parser')
    root = content.find('div', {"id": "root"})
    if root:
        content = root
        if root.find('div', {'id': 'mbasic_inline_feed_composer'}):
            # If you find this element, then the profile url redirected you to
            # the home page, meaning the profile doesn't exist anymore.
            return profile

    simplified = simplify(content)
    for child in simplified[2:-1]:
        if type(child) == unicode:
            continue
        elif type(child[0]) == unicode:
            k, v = parse_section(child)
            if k and len(v):
                profile[k] = v
        else:
            for grandchild in child:
                k, v = parse_section(grandchild)
                if k and len(v):
                    profile[k] = v

    return profile


direct_sections = {'Favorite Quotes': 'quotes'}
join_sections = {'Professional Skills': 'skills',
                 'Name Pronunciation': 'pronunciation'}
map_sections = {'Basic Info': 'basics',
                'Contact Info': 'contact',
                'Other Names': 'names'}
map_array_sections = {'Life Events': 'life_events'}


def parse_section(section):
    # section is an array where the first element is the title and the rest is the data
    name = section[0]
    rest = section[1:]

    if name in direct_sections:
        # Result is an array, so just return the array
        return direct_sections[name], force_structure(rest, unicode)
    elif name in join_sections:
        # Result should be a string, so join the array into one long string
        return join_sections[name], ' '.join(force_structure(rest, unicode))
    elif name in map_sections:
        # Result should be a dictionary mapping strings to strings
        mm = create_recursive_dict(rest, make_array=name != u'Basic Info')
        # Special Handling
        # Just to clean up a couple of values for easier analysis later
        if name == 'Basic Info':
            for field in ['Political Views', 'Religious Views']:
                if field in mm and type(mm[field]) == dict:
                    mm[field] = mm[field]['contents']
            if 'Languages' in mm:
                l_str = mm['Languages']
                langs = []
                for bit in l_str.split(' and '):
                    for lang in bit.split(', '):
                        langs.append(lang.strip())
                mm['Languages'] = langs
        elif name == 'Contact Info' and 'Facebook' in mm:
            # This information is redundant
            del mm['Facebook']

        return map_sections[name], mm
    elif name in map_array_sections:
        # Result should be a dictionary mapping strings to arrays of strings
        if len(rest) != 1:
            print 'Rest error', rest
            exit(0)
        mm = {}
        values = force_structure(rest[0], list)
        for x in values:
            key = x[0]
            if key in mm:
                print 'Error key', key, rest[0]
            else:
                mm[key] = x[1:]
        return map_array_sections[name], mm
    elif name == 'Family Members':
        return 'family', parse_family(rest)
    elif name == 'Work':
        return 'work', parse_work(rest)
    elif name == 'Education':
        return 'education', parse_education(rest)
    elif name == 'Relationship':
        return 'relationship', parse_relationship(rest)

    # Look at just the first word due to variable section names
    word = name.split()[0]
    if word == 'About':
        # Usually "About FIRSTNAME"
        cleaned = force_structure(rest, unicode)
        return 'about', ' '.join(cleaned)
    elif word == 'Places':
        # Usually "Places He/She's Lived"
        return 'places', parse_places(rest)

    raise Exception('Unknown Section %s' % name)


def parse_family(rest):
    fam = {}
    if len(rest) != 1:
        print rest
        exit(0)
    values = force_structure(rest[0], list)
    clean_values = []
    for x in values:
        if type(x) == unicode:
            if x != u'Family member':
                print 'Family', x
            continue
        clean_values.append(x)
    for link, rel in clean_values:
        if type(link) != dict:
            continue
        fam[link['link']] = rel
    return fam


def parse_work(rest):
    if len(rest) != 1:
        print rest
        exit(0)
    D = []
    if type(rest[0]) == unicode:
        D.append({'name': rest[0]})
        return D
    values = force_structure(rest[0], list)
    for el in values:
        key, title, duration, location, description = None, None, None, None, None
        if type(el) == dict:
            key = el
        elif len(el) == 5:
            key, title, duration, location, description = el
        elif len(el) >= 3 and ' - ' in el[2]:
            key, title, duration = el[:3]
            if len(el) == 4:
                location = el[3]
        else:
            key = el[0]
            if len(el) > 1:
                title = el[1]
                if len(el) > 2:
                    location = el[2]

        job = {}
        if type(key) == unicode:
            job['name'] = key
        else:
            job['name'] = key['contents']
            job['link'] = key['link']
        if title:
            job['title'] = title
        if duration:
            job['duration'] = duration
        if location:
            job['location'] = location
        if description:
            job['description'] = description

        D.append(job)
    return D


def parse_education(rest):
    if len(rest) != 1:
        print rest
        exit(0)
    values = force_structure(rest[0], list)
    schools = []
    for el in values:
        schools.append(parse_school(el))
    return schools


def parse_relationship(rest):
    values = force_structure(rest, unicode)
    if len(values) == 3:
        status, link, date = values
    elif len(values) == 2:
        status, link = values
        date = None
    elif len(values) == 1 and type(values[0]) == unicode:
        status = values[0]
        link = None
        date = None
        if 'since' in status:
            status, _, date = status.partition(' since ')
    else:
        print values
        exit(0)
    words = status.split()
    if words[-1] in ['to', 'with']:
        status = ' '.join(words[:-1])

    D = {'status': status}
    if link:
        D['who'] = link['link']
    if date:
        D['since'] = date
    return D


def parse_places(rest):
    if len(rest) != 1:
        print rest
        exit(0)
    values = force_structure(rest[0], list)
    places = []
    for place in values:
        label, link = place
        if type(link) == dict:
            places.append({'name': link['contents'], 'link': link['link'], 'label': label})
        else:
            places.append({'name': link, 'label': label})
    return places
