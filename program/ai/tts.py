import io
import re
import requests


def get_props_split_by_60_chars(prop):
    prop = prop.replace('\n', '')
    prop = prop.replace('"', '.')
    prop = prop.replace('“', '.')
    prop = prop.replace('”', '.')
    prop = prop.replace('\'', '')
    prop = prop.replace(':', '.')
    prop = prop.replace(',', '.')
    list = []

    while len(prop) > 0:
        first_space = prop.find('.', 0, 60)
        if first_space == -1:
            first_space = prop.find(' ', 60)
            if first_space == -1:
                list.append(prop)
                break
        else:
            first_space += 1

        list.append(prop[0:first_space])

        prop = prop[first_space:].strip()
        if prop.find('.') == -1:
            if len(prop) >= 1:
                list.append(prop)
            break

    final_res = []
    for p in list:
        marks = re.findall("[?!.]", p[-1])
        if len(marks) == 0:
            p += '.'

        final_res.append(p)

    print(final_res)

    return final_res


file = io.open('text.txt', 'r', encoding="utf-8")

for p_index, prop in enumerate(file):
    props = get_props_split_by_60_chars(prop)

    for s_index, sentence in enumerate(props):
        payload = {'text': sentence}
        doc = requests.get('http://localhost:5002/api/tts', params=payload)
        with open(f"audio\{p_index}-{s_index}.mp3", 'wb') as f:
            f.write(doc.content)


