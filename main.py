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
    #print(tokens)
    for token in tokens:
        new_word = token.replace('{x', '').replace('x}', '').split('|')[-1]
        sentence = sentence.replace(token, new_word)

    return sentence


def printlist(list_2):
    if len(list_2)!=0:
        print(list_2)

def makelist(m,list_t1,list_2d):
    if (m == 0) & (list_t1[m][0:4] == '||||'): #row span인지 아닌지
        pass
    elif list_t1[m][0:6] == '||||||':
        list_t1[m] = list_t1[m][4:]
    elif list_t1[m][0:2] == '||':
        list_t1[m] = list_t1[m][2:]
    if list_t1[m][-2:] == '||':
        list_t1[m] = list_t1[m][:-2]
        # list_t1[m] = list_t1[m][2:-2] # 끝에 ||삭제하는 코드
        # print(list_t1[m])
    if '||||||||||||||||' in list_t1[m]:
        a = 1
    elif '||||||||||||||' in list_t1[m]:
        a = 2
    elif '||||||||||' in list_t1[m]:
        a = 3
    elif '||||||' in list_t1[m]:
        a = 4
    elif '||||' in list_t1[m]:
        a = 5
    else:
        a = 0
        # elif '||||' in list_t1[m]:
        #    a=True

    list_t2 = list_t1[m].split('||')  # 첫번째 나누기 : column에 따라 나누는 것, str -> list, rowspan 처리

    # for l, k in enumerate(list_t2):
    #    if "||||" in k:
    #        list_t2[l] = k.split('|||') #두번째 나누기 : ||||에 따라 나누기, 리스
    # print(list_t2)
    if a != 0:
        # print(a)
        for o, word in enumerate(list_t2):
            if word == '':
                if list_t2[o + 1] != '':
                    list_t2[o] = list_t2[o + 1]
                    # print(list_t2[o])
                elif list_t2[o + 2] != '':
                    list_t2[o] = list_t2[o + 2]
                elif list_t2[o + 3] != '':
                    list_t2[o] = list_t2[o + 3]
                elif list_t2[o + 4] != '':
                    list_t2[o] = list_t2[o + 4]
                elif list_t2[o + 5] != '':
                    list_t2[o] = list_t2[o + 5]
                elif list_t2[o + 6] != '':
                    list_t2[o] = list_t2[o + 6]
    list_2d.append(list_t2)



def colspan(list_2d):
    for o in range(len(list_2d)):
        if (o!=0) and (o!=(len(list_2d)-1)): # 첫째행이 아니고 마지막 행이 아닐떄
            if len(list_2d[o])<len(list_2d[o-1]):
                list_2d[o].append(list_2d[o-1][len(list_2d[o-1])-1])
        elif o == (len(list_2d)-1): #마지막 행일떄
            if len(list_2d[o])<len(list_2d[o-1]):
                k= len(list_2d[o-1])-len(list_2d[o])
                for i in range(k):
                    list_2d[o].append(list_2d[o][len(list_2d[o])-1])
        elif (o==0) and (len(list_2d[o])<len(list_2d[o+1])): #첫째행이고, 첫째행이 둘째행보다 길이가 작을때
            k= len(list_2d[o+1])-len(list_2d[o])
            for i in range(k):
                list_2d[o].append(list_2d[o][len(list_2d[o])-1])




def table2list2d(table_text):
    #print(table_text)
    print('table')
    list_t1 = table_text.split('\n')

    list_2d1 = []
    list_2d2 = []
    list_2d3 = []
    list_2d4 = []
    list_2d5 = []

    nextlistswitch =0
    for m, p in enumerate(list_t1):
        if (list_t1[m][0:2]!='||')and(list_t1[m][-2:]!='||'): #만약에 table_text의 첫번째 줄에 양쪽끝이 둘다 ||로 닫힌 경우가 아닌경우 : 테이블이 아닌경우
            if len(list_2d1)==0: #list_2d의 길이가 0인 경우
                #return list_2d #생각중, return 지우고 다른 list로 바꾸는 방법 생각해야
                continue #생각중, 이거는 아마 가만 놔둬야 할 듯
            elif len(list_2d1)!=0: #list_2d가 0이 아닌 경우
                if len(list_2d2)==0:
                    nextlistswitch=1 # for문 다음 인덱스로 이동
                    continue
                elif len(list_2d2)!=0:
                    if len(list_2d3)==0:
                        nextlistswitch=2
                        continue
                    elif len(list_2d3)!=0:
                        if len(list_2d4) == 0:
                            nextlistswitch = 3
                            continue
                        else:
                             nextlistswitch = 4
                             continue


        if nextlistswitch==0:
            makelist(m, list_t1, list_2d1)
            colspan(list_2d1)
        elif nextlistswitch==1:
            makelist(m, list_t1, list_2d2)
            colspan(list_2d2)
        elif nextlistswitch == 2:
            makelist(m, list_t1, list_2d3)
            colspan(list_2d3)
        elif nextlistswitch == 3:
            makelist(m, list_t1, list_2d4)
            colspan(list_2d4)
        elif nextlistswitch == 4:
            makelist(m, list_t1, list_2d5)
            colspan(list_2d5)





    printlist(list_2d1)
    printlist(list_2d2)
    printlist(list_2d3)
    printlist(list_2d4)
    printlist(list_2d5)




for doc in parse_namuwiki_json(1000, debug=False):
    print('Document')

    document_str = str(doc['text']).replace('||\n=', '||\n\n=').replace('||\n *', '||\n\n *')
    table_list_ = document_str.split('||\n\n') #||\n\n기준으로 문자열 분리 -> 리스트로 반환
    table_list = []
    scores = []

    for i, table_text in enumerate(table_list_):
        new_table_text = ''
        opened = False
        check1 = 1
        check2 = 1

        for j in range(len(table_text)):
            if j > 1:
                if table_text[j - 1] == '|' and table_text[j - 2] == '|':
                    opened = True
                if table_text[j - 1] == '\n' and table_text[j] == '|':
                    check1 += 1
                if table_text[j] == '\n':
                    check2 += 1

            if opened is True:
                new_table_text += table_text[j]
        if opened is True:
            table_list.append(new_table_text)
            scores.append(check1 / check2)

    print('title:', doc['title'])


    for k, table_text in enumerate(table_list):  #dictionary와 비슷, key값과 value값
        table_text = table_text.replace('{{{', '{z').replace('}}}', 'z}').replace('[[', '{x').replace(']]', 'x}')
        table_text = re.sub(pattern=pattern, repl='', string=table_text)  #특수문자 제거
        table_text = preprocess1(table_text, p2) #전처리
        table_text = preprocess2(table_text, p3) #전처리


        #print(table_text) #전처리 된것
        print(scores[k])
        #print(table_list[k]) #전처리 안된 것
        print(table_text)

        if "||||" in table_text:#table일시
            #print(table_text)
            (table2list2d(table_text))
        elif "|| '" in table_text:
            #print(table_text)
            (table2list2d(table_text))
        elif "|| " in table_text:
            (table2list2d(table_text))
        elif "||\n||" in table_text:
            (table2list2d(table_text))
        print("===" * 10)

    input()

