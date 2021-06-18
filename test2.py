import ijson
import re

capture_values = [
    ("item.namespace", "string"),
    ("item.title", "string"),
    ("item.text", "string")
]


def parse_namuwiki_json(limit=-1, debug=False):
    i = 0
    doc = {}
    with open('docData200302.json') as f:
        for prefix, event, value in ijson.parse(f):

            if debug:
                print(prefix, event, value)

            if (prefix, event) in capture_values:
                doc[prefix[5:]] = value
            if (prefix, event, value) == ("item", "end_map", None):
                yield doc
                doc = {}
                i += 1

                if limit > 0 and i >= limit:
                    break


pattern = '<[^>]*>'
pattern2 = '{z[^z}]*z}'
pattern3 = '{x[^x}]*x}'

p2 = re.compile(pattern2)
p3 = re.compile(pattern3)

#re.sub(pattern=pattern, repl='', string=doc)


def preprocess1(sentence, p):
    tokens = p.findall(sentence)

    for token in tokens:
        tk = token.split(' ')

        new_word = ''
        for j in range(1, len(tk)):
            new_word += tk[j] + ' '
        new_word = new_word.strip().replace('z}', '')

        sentence = sentence.replace(token, new_word)

    return sentence


def preprocess2(sentence, p):
    tokens = p.findall(sentence)
    print(tokens)
    for token in tokens:
        new_word = token.replace('{x', '').replace('x}', '').split('|')[-1]
        sentence = sentence.replace(token, new_word)

    return sentence


for doc in parse_namuwiki_json(1000, debug=False):
    print('Document')

    document_str = str(doc['text']).replace('||\n=', '||\n\n=').replace('||\n *', '||\n\n *')
    paragraphs = document_str.split('\n=')
    for paragraph in paragraphs:
        print(paragraph)
        print('---' * 10)
    print("===" * 10)
    print('title:', doc['title'])
    input()

