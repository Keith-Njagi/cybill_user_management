import re

def compute_platform_version(user_agent, platform):
    if platform == 'windows':
        if 'Windows Phone' in user_agent:
            name_with_punctuation = re.search(r'Windows Phone .+(?=;)', user_agent)
            name = name_with_punctuation.group()
            if ';' in name:
                name_lst = name.split(';')
                name = name_lst[0]
                print('Platform: ', name)
                return name
            return name
        name = user_agent[user_agent.find('Windows'): user_agent.find(';') or user_agent.find(')')]
        if ';' in name:
            name_lst = name.split(';')
            name = name_lst[0]
            return name
        if ')' in name:
            name_lst = name.split(')')
            name = name_lst[0]
            return name
        return name

    if platform == 'linux':
        try:
            name_with_punctuation = re.search(r'Linux .+(?=;)', user_agent)
            name = name_with_punctuation.group() # [:-1]
            if ';' in name:
                name_lst = name.split(';')
                name = name_lst[0]
                return name
            if ')' in name:
                name_lst = name.split(')')
                name = name_lst[0]
                return name
            return name
        except AttributeError:
            name_with_punctuation = re.search(r'Linux .+(?=\))', user_agent)
            name = name_with_punctuation.group() # [:-1]
            if ';' in name:
                name_lst = name.split(';')
                name = name_lst[0]
                return name
            if ')' in name:
                name_lst = name.split(')')
                name = name_lst[0]
                return name
            return name

    if platform == 'macos':
        try:
            name_with_punctuation = re.search(r'Mac OS .+(?=;)', user_agent)
            name = name_with_punctuation.group() 
            return name
        except AttributeError:
            name_with_punctuation = re.search(r'Mac OS .+(?=\))', user_agent)
            name = name_with_punctuation.group()
            if ')' in name:
                name_lst = name.split(')')
                name = name_lst[0]
                return name
            return name

    if platform ==  'android':
        name_with_punctuation = re.search(r'Android .+(?=;)', user_agent)
        name = name_with_punctuation.group()
        if ';' in name:
            name_lst = name.split(';')
            name = name_lst[0]
            return name
        return name

    if platform == 'iphone':
        name_with_punctuation = re.search(r'iPhone .+(?= like Mac)', user_agent)
        name = name_with_punctuation.group()
        return name

    if platform == 'ipad':
        name_with_punctuation = re.search(r'OS .+(?= like Mac)', user_agent)
        name = name_with_punctuation.group()
        return name

    if platform == '':
        return None