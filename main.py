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


#정규 표현식

#리다이렉트 문서일 경우 해당 패턴으로 시작함. 해당 문서 전체 삭제가 필요.
# pattern_redirect_00 = "#redirect"
# pattern_redirect_01 = "#넘겨주기"

pattern1 = '<[^>]*>'
pattern2 = '{z[^z}]*z}'                 #'{{{' -> '{z' / '}}}' -> 'z}'
pattern3 = '{x[^x}]*x}'                 #'[['  -> '{x' / ']]'  -> 'x}'

#중간에 추가 글이 들어가지 않는 패턴. 단순 삭제
pattern_sim_00 = '\'\'\' \'\''                  #강조 기울임 시작
pattern_sim_01 = '\'\' \'\'\''                  #강조 기울임 끝
pattern_sim_02 = '\'\'\''                       #'''문장''' : 강조문. '''만 제거하면 될 것이다
pattern_sim_03 = '\'\''                         #기울임. pattern4 이후에 처리
pattern_sim_04 = '\[목차\]'                       #목차 표시 지역
pattern_sim_05 = '\[tableofcontent\]'
pattern_sim_06 = '\[각주\]'                       #각주 표시 지역
pattern_sim_07 = '\[footnote\]'
pattern_sim_08 = '\[br\]'                       #줄바꿈
pattern_sim_09 = '\[\[\.\./\]\]'                #현재 문서의 상위 문서 링크
pattern_sim_10 = '-{4,9}'                       #4개에서 9개의 하이픈 -> 수평줄
pattern_sim_11 = '\[clearfix\]'                 #CSS float 속성 초기화


#중간에 추가 글이 들어가는 패턴. 단순 삭제하기
pattern_del_00 = '\[youtube\([^\)\]]*\)\]'      #youtube 링크
pattern_del_01 = '\[kakaotv\([^\)\]]*\)\]'      #kakaotv 링크
pattern_del_02 = '\[nicovideo\([^\)\]]*\)\]'    #nicovideo 링크
pattern_del_03 = '\{\{\{#!html[^\}\}\}]*\}\}\}' #html 링크
pattern_del_04 = '=[=]+[^=]*=[=]+'              #문단 제목
pattern_del_05 = '~~[^~~]*~~'                   #취소선 문장
pattern_del_06 = '--[^--]*--'                   #취소선 문장
pattern_del_07 = '\[\[파일\:[^\]\]]*\]\]'        #파일 링크
pattern_del_08 = '\[[Ii]nclude\(.*\)\]'         #include
pattern_del_09 = '\[\[분류\:[^\]\]]*\]\]'        #분류
pattern_del_10 = '\[\[https?://[^\|\]\]]*\]\]'  #외부링크로 연결되어 있으며 실제 출력 텍스트가 구별되어있지 않은 링크.
pattern_del_11 = '\[\*[^\]]*\]'                 #각주. 현재는 내용 전체를 삭제하지만 이후에 살려야할수도 있음. *우측에 ' '없이 붙는 단어나 문장은 각주의 제목.

#중간에 추가 글이 들어가는 패턴. 표시된 부분만 삭제
pattern_norm_00 = '__[^__]*__'                          #밑줄
pattern_norm_01 = '\{\{\{#!folding [^\}\}\}]*\}\}\}'    #접기 문서

#별도의 처리방법이 필요함
pattern_ex_link = '\[\[[^\]\]]*\]\]'            #하이퍼링크 [[문장]]과 같은 방식으로 구성되어 있으며, 실제 텍스트와 링크된 문서의 제목이 다른 경우 좌측이 링크된 문서 제목, 우측이 실제 텍스트

#아직 처리방법이 정해지지 않은 패턴
pattern_quote = '>+.*\n'                        #인용문
pattern_age = '\[age\([^\)\]]*\)\]'             #YYYY-MM-DD형식으로 ()내에 입력하면 자동으로 만 나이 출력
pattern_date = '\[date\]'                       #date, datetime : 현재 시각 출력
pattern_datetime = '\[datetime\]'
pattern_dday = '\[dday\([^\)\]]*\)\]'           #잔여일수, 경과일수 출력
patternb = '\^\^[^\^\^]*\^\^'                   #위첨자
patternc = ',,[^,,]*,,'                         #아래첨자

#정규 표현식 패턴 컴파일
p1 = re.compile(pattern1)
p2 = re.compile(pattern2)
p3 = re.compile(pattern3)

ps00 = re.compile(pattern_sim_00)
ps01 = re.compile(pattern_sim_01)
ps02 = re.compile(pattern_sim_02)
ps03 = re.compile(pattern_sim_03)
ps04 = re.compile(pattern_sim_04)
ps05 = re.compile(pattern_sim_05)
ps06 = re.compile(pattern_sim_06)
ps07 = re.compile(pattern_sim_07)
ps08 = re.compile(pattern_sim_08)
ps09 = re.compile(pattern_sim_09)
ps10 = re.compile(pattern_sim_10)
ps11 = re.compile(pattern_sim_11)
pattern_sim_list = [ps00, ps01, ps02, ps03, ps04, ps05, ps06, ps07, ps08, ps09, ps10, ps11]

pd00 = re.compile(pattern_del_00)
pd01 = re.compile(pattern_del_01)
pd02 = re.compile(pattern_del_02)
pd03 = re.compile(pattern_del_03)
pd04 = re.compile(pattern_del_04)
pd05 = re.compile(pattern_del_05)
pd06 = re.compile(pattern_del_06)
pd07 = re.compile(pattern_del_07)
pd08 = re.compile(pattern_del_08)
pd09 = re.compile(pattern_del_09)
pd10 = re.compile(pattern_del_10)
pd11 = re.compile(pattern_del_11)
pattern_del_list = [pd00, pd01, pd02, pd03, pd04, pd05, pd06, pd07, pd08, pd09, pd10, pd11]

pn00 = re.compile(pattern_norm_00)
pn01 = re.compile(pattern_norm_01)
#pattern_norm_list = [pn00, pn01]

pex_link = re.compile(pattern_ex_link)

#re.sub(pattern=pattern, repl='', string=doc)

def redirect_check(sentence):               #리다이렉트 문서인지 확인 후 true/false 반환
    eng = sentence.startswith('#redirect')
    kor = sentence.startswith('#넘겨주기')
    result = eng|kor

    return result

def preprocess0(sentence, p):
    tokens = p.findall(sentence)

    for token in tokens:
        emptywords = ''
        sentence = sentence.replace(token, emptywords)

    return sentence

def preprocess1(sentence, p):       #{{{와 }}}로 감싸진 부분 처리
    tokens = p.findall(sentence)

    for token in tokens:
        tk = token.split(' ')

        new_word = ''
        for j in range(1, len(tk)):
            new_word += tk[j] + ' '
        new_word = new_word.strip().replace('z}', '')

        sentence = sentence.replace(token, new_word)

    #print("preprocess1 sentence\n")
    print(sentence)

    return sentence


def preprocess2(sentence, p):
    tokens = p.findall(sentence)
    #print(tokens)
    for token in tokens:
        new_word = token.replace('{x', '').replace('x}', '').split('|')[-1]
        sentence = sentence.replace(token, new_word)

    return sentence

def preprocess4(sentence, p):       #강조문 표시 삭제  (문장, 패턴)순서이며 이후에 한 함수로 변환해도 될 것 같음
    tokens = p.findall(sentence)

    for token in tokens:
        new_word = token.replace('\'\'\'', '')
        sentence = sentence.replace(token, new_word)

    return sentence

# def preprocess5(sentence, p):       #취소선 텍스트 삭제
#     tokens = p.findall(sentence)
#
#     for token in tokens:
#         emptywords = ''
#         sentence = sentence.replace(token, emptywords)
#
#     return sentence
#
# def preprocess6(sentence, p):       #사진 등 파일이 링크돼있는 텍스트. 삭제 수행
#     tokens = p.findall(sentence)
#
#     for token in tokens:
#         emptywords = ''
#         sentence = sentence.replace(token, emptywords)
#
#     return sentence

def preprocess_link(sentence, p):       #하이퍼링크 정리('|'로 나뉘어져 있는 텍스트에서 우측의 원본만을 추출하고 좌측의 링크된 문서 제목은 삭제)
    tokens = p.findall(sentence)

    for token in tokens:
        new_word = token.replace('[[', '').replace(']]', '').split('|')
        new_word = new_word[-1]
        new_word = new_word.replace('\\#', '#').replace('\\\'', '\'')
        sentence = sentence.replace(token, new_word)

    return sentence

# def preprocess8(sentence, p):
#     tokens = p.findall(sentence)
#
#     for token in tokens:
#         emptywords = ''
#         sentence = sentence.replace(token, emptywords)
#
#     return sentence
#
# def preprocess9(sentence, p):
#     tokens = p.findall(sentence)
#
#     for token in tokens:
#         emptywords = ''
#         sentence = sentence.replace(token, emptywords)
#
#     return sentence
#
# def preprocess10(sentence, p):
#     tokens = p.findall(sentence)
#
#     for token in tokens:
#         emptywords = ''
#         sentence = sentence.replace(token, emptywords)
#
#     return sentence
#
# def preprocess11(sentence, p):
#     tokens = p.findall(sentence)
#
#     for token in tokens:
#         emptywords = ''
#         sentence = sentence.replace(token, emptywords)
#
#     return sentence
#
# def preprocess12(sentence, p):
#     tokens = p.findall(sentence)
#
#     for token in tokens:
#         emptywords = ''
#         sentence = sentence.replace(token, emptywords)
#
#     return sentence
#
# def preprocess13(sentence, p):
#     tokens = p.findall(sentence)
#
#     for token in tokens:
#         emptywords = ''
#         sentence = sentence.replace(token, emptywords)
#
#     return sentence

def preprocess_delete(sentence, p):
    tokens = p.findall(sentence)

    for token in tokens:
        emptywords = ''
        sentence = sentence.replace(token, emptywords)

    return sentence

def preprocess_norm_00(sentence):
    tokens = pn00.findall(sentence)

    for token in tokens:
        new_word = token.replace('__', '')
        sentence = sentence.replace(token, new_word)

    return sentence

def preprocess_norm_01(sentence):
    tokens = pn01.findall(sentence)

    for token in tokens:
        new_word = token.replace('{{{#!folding ', '').replace('}}}', '')
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
        elif o == (len(list_2d)-1): # 마지막 행일떄
            if len(list_2d[o])<len(list_2d[o-1]):
                k = len(list_2d[o-1])-len(list_2d[o])
                for i in range(k):
                    list_2d[o].append(list_2d[o][len(list_2d[o])-1])
        elif (o == 0) and (len(list_2d[o])<len(list_2d[o+1])): # 첫째행이고, 첫째행이 둘째행보다 길이가 작을 때
            k = len(list_2d[o+1])-len(list_2d[o])
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


#main code
for doc in parse_namuwiki_json(1000, debug=False):
    document_title = str(doc['title'])
    document_str = str(doc['text'])

    isRedirect = redirect_check(document_str)   #doc가 리다이렉트 문서인지 여부를 저장
    #print("redirect : ", isRedirect)
    if(isRedirect == True):                     #doc가 리다이렉트 문서일 경우
        continue                                #이하의 처리 코드를 모두 건너뛰고 다음 문서로 이동

    print('\n---------------------------------------\n')
    print('Document')
    print('title:', document_title)  # title 출력
    print('\n--------text--------\n')

    document_str = preprocess0(document_str, p1)

    for pat in pattern_sim_list:
        document_str = preprocess_delete(document_str, pat)

    for pat in pattern_del_list:
        document_str = preprocess_delete(document_str, pat)

    document_str = preprocess_norm_00(document_str)
    document_str = preprocess_norm_01(document_str)

    document_str = preprocess_link(document_str, pex_link)

    # print("document_str_start")
    # print(document_str)
    # print("document_str_done\n")

    document_str.replace('||\n=', '||\n\n=').replace('||\n *', '||\n\n *') #왼쪽 문자열을 오른쪽으로 변환        ???
    table_list_ = document_str.split('||\n\n') #||\n\n기준으로 문자열 분리 -> 리스트로 반환
    print("table list\n")
    print(table_list_)
    print("--------done-------\n")
    table_list = []
    scores = []

    #table
    for i, table_text in enumerate(table_list_):    #분리된 문자열을 하나씩 가져옴
        new_table_text = ''
        opened = False
        check1 = 1                                  #???
        check2 = 1                                  #???

        for j in range(len(table_text)):
            if j > 1:
                if table_text[j - 1] == '|' and table_text[j - 2] == '|':   #표의 행 시작
                    opened = True
                if table_text[j - 1] == '\n' and table_text[j] == '|':      #표 개행
                    check1 += 1
                if table_text[j] == '\n':
                    check2 += 1

            if opened is True:                                              #표의 행이 시작됐을 때
                new_table_text += table_text[j]                             #테이블 텍스트에 삽입하기 시작함

        if opened is True:
            table_list.append(new_table_text)
            scores.append(check1 / check2)

    #print('title:', doc['title']) #title 출력

    for k, table_text in enumerate(table_list):  #dictionary와 비슷, key값과 value값
        table_text = table_text.replace('{{{', '{z').replace('}}}', 'z}').replace('[[', '{x').replace(']]', 'x}')   #[[]] : 하이퍼링크 단어
        table_text = re.sub(pattern=pattern1, repl='', string=table_text)  #특수문자 제거
        table_text = preprocess1(table_text, p2) #전처리1 {{{}}}
        table_text = preprocess2(table_text, p3) #전처리2 [[]]
        #print(table_text)

        #print(table_text) #전처리 된것
        print(scores[k])
        #print(table_list[k]) #전처리 안된 것
        print(table_text)       #전처리 된 테이블 텍스트

        if "||||" in table_text:
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

