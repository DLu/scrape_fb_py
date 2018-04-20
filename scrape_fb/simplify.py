from bs4.element import NavigableString
from .utils import match_friend_link


def force_structure(data, first_element_type):
    if type(data) != list:
        data = [data]
    first_element = data[0]
    if type(first_element) == first_element_type:
        return data
    elif type(first_element) == list:
        if len(data) == 1 and type(first_element[0]) == first_element_type:
            return first_element

    if type(data) == first_element_type:
        return [data]

    print data, first_element_type
    exit(0)


def simplify(content):
    if type(content) == NavigableString:
        return unicode(content).strip()
    href = None
    if content.name == 'a' and 'href' in content.attrs:
        href = match_friend_link(content['href'])
    pieces = []
    for piece in content.children:
        ret = simplify(piece)
        if len(ret) > 0:
            pieces.append(ret)

    if len(pieces) == 1:
        if href:
            return {'link': href, 'contents': pieces[0]}
        return pieces[0]
    else:
        if href and len(pieces):
            print href, pieces, '!'
        return pieces


def create_recursive_dict(a, make_array=False):
    mm = {}
    for k in a:
        if type(k) == unicode:
            continue
        if len(k) == 2 and type(k[0]) == unicode:
            new_dict = {k[0]: k[1]}
        else:
            new_dict = create_recursive_dict(k, make_array)
        for key, value in new_dict.items():
            if key in mm:
                if make_array:
                    if type(mm[key]) != list:
                        mm[key] = [mm[key]]
                    mm[key].append(value)
                else:
                    print key, value, mm[key], '!!'
            else:
                mm[key] = value
    return mm
