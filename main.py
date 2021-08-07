import ijson
import json
import re
import os

capture_values = [
    ("item.namespace", "string"),
    ("item.title", "string"),
    ("item.text", "string")
]

#wiki_group = dict()



def parse_namuwiki_json(limit=-1, debug=False):             #나무위키 json dump file parsing
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

expFileName = 'processedWiki'
expFileExt = '.json'
docNum = 0                                          #docSet에 저장된 문서의 양을 저장하는 변수
jsonNum = 0                                         #분할된 processedWiki.json의 개수
docSet = []                                         #전처리 된 문서를 임시로 저장하는 리스트
#jsonFileName = 'processedWiki.json'
def savePreprocessedJson(title, text, table):       #전처리 된 문서를 json에 붙여넣는 함수
    document = dict()
    document["title"] = title
    document["text"] = text
    table_json = json.dumps(table, ensure_ascii=False)
    document["table"] = table_json
    global docNum
    global docSet
    global jsonNum
    docNum = docNum + 1
    docSet.append(document)
    if docNum > 10000:                                      #docSet내의 문서 수가 일정량 이상 넘으면 다음의 처리를 한다.
        expFileNum = format(jsonNum, '03')
        jsonFileName = expFileName + expFileNum + expFileExt    #처리 후 문서를 저장하는 json의 파일 이름 만들기
        if os.path.isfile(jsonFileName)==False :                #저장할 json이 존재하지 않는 경우 :
            initializeJson(jsonFileName)                            #json파일 생성 및 초기화 후
            saveJson(jsonFileName, docSet)                          #docSet 저장
        elif os.path.getsize(jsonFileName) >= 524288000 :       #처리 후 문서의 크기가 500MB이상일 경우 :
            saveJson(jsonFileName, docSet)                          #docSet 저장
            jsonNum += 1                                            #jsonNum 1 증가, 다음 문서 저장부터는 새 문서 생성
        else :                                                  #문서가 존재하며 문서의 크기가 500MB 미만일 경우:
            saveJson(jsonFileName, docSet)                          #docSet 저장
        docNum = 0                                              #docNum 초기화
        docSet = []                                             #docSet 초기화

def initializeJson(jsonFileName):
    print("\n\n================")
    print("initialized \n", jsonFileName)
    print("================\n\n")
    initialList = [{"title":"", "text":"", "table":""}]
    with open(jsonFileName, 'w', encoding = 'utf-8') as initial:
        json.dump(initialList, initial)

def saveJson(jsonFileName, docSet):
    with open(jsonFileName, 'r+', encoding='utf-8') as wiki:
        print("\n----------------")
        print("saving wiki data on\n", jsonFileName)
        print("----------------\n")
        wikiData = json.load(wiki)
        for i in range(len(docSet)):
            wikiData.append(docSet[i])
        wiki.seek(0)
        json.dump(wikiData, wiki, ensure_ascii=False)


def saveLeftoverPreprocessedJson():     #docNum이 상한선을 달성하지 못하고 문서처리가 완전히 끝날 경우
    global docNum                       #docSet에 남은 처리완료문서를 json에 넣는 함수
    global docSet
    expFileNum = format(jsonNum, '03')
    jsonFileName = expFileName + expFileNum + expFileExt
    with open(jsonFileName, 'r+', encoding='utf-8') as wiki:
        print("\n----------------")
        print("saving wiki data on\n", jsonFileName)
        print("----------------\n")
        wikiData = json.load(wiki)
        for i in range(len(docSet)):
            wikiData.append(docSet[i])
        wiki.seek(0)
        json.dump(wikiData, wiki, ensure_ascii=False)
    docNum = 0
    docSet = []

#정규 표현식

#리다이렉트 문서일 경우 해당 패턴으로 시작함. 해당 문서 전체 삭제가 필요.
# pattern_redirect_00 = "#redirect"
# pattern_redirect_01 = "#넘겨주기"             #정규식이 없어도 .startswith()로 처리 가능. redirect_check 함수 참조

pattern1 = '<[^>]*>'
pattern2 = '{z[^z}]*z}'                 #'{{{' -> '{z' / '}}}' -> 'z}'
pattern3 = '{x[^x}]*x}'                 #'[['  -> '{x' / ']]'  -> 'x}'

#중간에 추가 글이 들어가지 않는 패턴. 단순 삭제
pattern_sim_00 = '\'\'\' \'\''                  #강조 기울임 시작
pattern_sim_01 = '\'\' \'\'\''                  #강조 기울임 끝
pattern_sim_02 = '\'\'\''                       #'''문장''' : 강조문. '''만 제거하면 될 것이다
pattern_sim_03 = '\'\''                         #기울임
pattern_sim_04 = '\[목차\]'                      #[목차] : 목차 표시 지역
pattern_sim_05 = '\[tableofcontent\]'
pattern_sim_06 = '\[각주\]'                      #[각주] : 각주 표시 지역
pattern_sim_07 = '\[footnote\]'
pattern_sim_08 = '\[br\]'                       #[br] : 줄바꿈
pattern_sim_09 = '\[\[\.\./\]\]'                #[..\] : 현재 문서의 상위 문서 링크
pattern_sim_10 = '-{4,9}'                       #---- : 4개에서 9개의 하이픈 -> 수평줄
pattern_sim_11 = '\[clearfix\]'                 #[clearfix] : CSS float 속성 초기화


#중간에 추가 글이 들어가는 패턴. 단순 삭제하기
pattern_del_00 = '~~[^~~]*~~'                   #~~sentence~~ : 취소선 문장
pattern_del_01 = '--[^--]*--'                   #--sentence-- : 취소선 문장
pattern_del_02 = '=[=]+[^=]*=[=]+'              #== title == : 문단 제목
pattern_del_03 = '\[\[파일\:[^\[\]]*\]\]'        #[[파일:link]] : 파일 링크
pattern_del_04 = '\[\[분류\:[^\[\]]*\]\]'        #[[분류:link]] : 분류
pattern_del_05 = '\[\[https?://[^\|\[\]]*\]\]'  #[[https?://link]] : 외부링크로 연결되어 있으며 실제 출력 텍스트가 구별되어있지 않은 링크.
pattern_del_06 = '\^\^[^\^\^]*\^\^'             #위첨자
pattern_del_07 = ',,[^,,]*,,'                   #아래첨자
#pattern_del_08 = '\{\{\{#!html [^\{\}]*\}\}\}' #{{{#!html link }}} :  링크

#중간에 추가 글이 들어가는 패턴. 표시된 부분만 삭제
pattern_norm_00 = '__[^__]*__'                                      #밑줄
pattern_norm_01 = '\{\{\{[#\+\-][^!\{\}][^\{\}]*\}\}\}'             #+,- : 글의 크기 변경 / # : 글의 색 변경
pattern_norm_02 = '\{\{\{#!folding [\[【][^\]】]*[\]】][^\{\}]*\}\}\}'        #접기 문서
pattern_norm_02_01 = '[\[【][^\]】]*[\]】]'                                   #접기 상태에서 펼치는 버튼 역할을 하는 텍스트
pattern_norm_03 = '\{\{\{#!html [^\{\}]*\}\}\}'                     #html문법을 따르는 텍스트. 앞 뒤로 삭제 필요

#별도의 처리방법이 필요함
pattern_ex_link = '\[\[[^\[\]]*\]\]'            #하이퍼링크 [[문장]]과 같은 방식으로 구성되어 있으며, 실제 텍스트와 링크된 문서의 제목이 다른 경우 좌측이 링크된 문서 제목, 우측이 실제 텍스트

#링크 처리 이후로 처리하는 단순 삭제 패턴
pattern_delal_00 = '\[[Ii]nclude\(.*\)\]'         #[include(sentence)] : include
pattern_delal_01 = '\[youtube\([^\)\]]*\)\]'      #[youtube(link)] : youtube 링크
pattern_delal_02 = '\[kakaotv\([^\)\]]*\)\]'      #[kakaotv(link)] : kakaotv 링크
pattern_delal_03 = '\[nicovideo\([^\)\]]*\)\]'    #[nicovideo(link)] : nicovideo 링크
pattern_delal_04 = '\[\*[^\]]*\]'                 #[* sentence] : 각주. 현재는 내용 전체를 삭제하지만 이후에 살려야할수도 있음. *우측에 ' '없이 붙는 단어나 문장은 각주의 제목.

#표의 시작과 끝 패턴
pattern_tableend = '\|\|\n+[^\|]'               #표의 마지막 부분. 이후에 preprocess_chartend함수에서 |[{end}]|로 변경
pattern_tablenl = '\|\|\n\|\|'                  #표의 마지막 부분이 아니며 개행문자가 있음. 이후에 preprocess_chartnl함수에서 || [{nl}] ||로 변경
pattern_table = '\|\|.*\|\[\{end\}\]\|'         #preprocess_chartend함수에서 변경된 부분을 포함한 한 표의 전체를 인지하는 패턴

#아직 처리방법이 정해지지 않은 패턴
pattern_quote = '>+.*\n'                        #인용문
pattern_age = '\[age\([^\)\]]*\)\]'             #YYYY-MM-DD형식으로 ()내에 입력하면 자동으로 만 나이 출력
pattern_date = '\[date\]'                       #date, datetime : 현재 시각 출력
pattern_datetime = '\[datetime\]'
pattern_dday = '\[dday\([^\)\]]*\)\]'           #잔여일수, 경과일수 출력 : 우리 모델에서 의미가 있는가?

#표 분리 후 table패턴 원상복귀 시키는 패턴
pattern_return_nl = '\|\| \[\{nl\}\] \|\|'
pattern_return_end = '\|\[\{end\}\]\|'

#표 분리 후 남는 residue 처리하기 위한 패턴
pattern_residue_00 = '\|\|'
pattern_residue_01 = '\|\[\{end\}\]\|'
pattern_residue_nl = '\n\n\n'                   #개행문자가 너무 많을 경우

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
#ps12 = re.compile(pattern_sim_12)
pattern_sim_list = [ps00, ps01, ps02, ps03, ps04, ps05, ps06, ps07, ps08, ps09, ps10, ps11]

pd00 = re.compile(pattern_del_00)
pd01 = re.compile(pattern_del_01)
pd02 = re.compile(pattern_del_02)
pd03 = re.compile(pattern_del_03)
pd04 = re.compile(pattern_del_04)
pd05 = re.compile(pattern_del_05)
pd06 = re.compile(pattern_del_06)
pd07 = re.compile(pattern_del_07)
#pd08 = re.compile(pattern_del_08, re.DOTALL.I)
pattern_del_list = [pd00, pd01, pd02, pd03, pd04, pd05, pd06, pd07] #08은 임시로 지운 상태

pn00 = re.compile(pattern_norm_00)
pn01 = re.compile(pattern_norm_01)
#pn02 = re.compile(pattern_norm_02)
pn02 = re.compile(pattern_norm_02, re.DOTALL)
pn02_01 = re.compile(pattern_norm_02_01)
pn03 = re.compile(pattern_norm_03, re.DOTALL.I)
#pattern_norm_list = [pn00, pn01]       #각각 처리방법이 달라서 리스트로 묶지 않았음

pex_link = re.compile(pattern_ex_link)

pda00 = re.compile(pattern_delal_00)
pda01 = re.compile(pattern_delal_01)
pda02 = re.compile(pattern_delal_02)
pda03 = re.compile(pattern_delal_03)
pda04 = re.compile(pattern_delal_04)
pattern_delal_list = [pda00, pda01, pda02, pda03, pda04]

p_tableend = re.compile(pattern_tableend)
p_tablenl = re.compile(pattern_tablenl)
p_table = re.compile(pattern_table)

p_return_nl = re.compile(pattern_return_nl)
p_return_end = re.compile(pattern_return_end)

p_re_00 = re.compile(pattern_residue_00)
p_re_01 = re.compile(pattern_residue_01)
pattern_residue_list = [p_re_00, p_re_01]
p_re_nl = re.compile(pattern_residue_nl, re.DOTALL)

#re.sub(pattern=pattern, repl='', string=doc)

def redirect_check(sentence):               #리다이렉트 문서인지 확인 후 true/false 반환
    eng = sentence.startswith('#redirect')
    kor = sentence.startswith('#넘겨주기')
    result = eng|kor

    return result

def translation_list_initialization():
    initial = open('translationList.py', 'w', encoding='utf-8')
    initial.write("translationList = [")
    initial.write("\n")
    initial.close()

def return_translation_result(sentence):
    wholeSentence = sentence.split(' ')
    newSentence = ''
    for i in range(1, len(wholeSentence)):
        newSentence += wholeSentence[i] + ' '
    newSentence = newSentence[:-2]
    return newSentence

def translation_list_write(title, text):
    file = open('translationList.py', 'a', encoding='utf-8')
    file.write('["')
    file.write(title)
    file.write('" , "')
    file.write(text)
    file.write('"],\n')
    file.close()

def translation_list_finalization():
    final = open('translationList.py', 'a', encoding='utf-8')
    final.write("[,]\n]")
    final.close()

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

    return sentence


def preprocess2(sentence, p):
    tokens = p.findall(sentence)
    for token in tokens:
        new_word = token.replace('{x', '').replace('x}', '').split('|')[-1]
        sentence = sentence.replace(token, new_word)

    return sentence

def preprocess_link(sentence, p):       #하이퍼링크 정리
    tokens = p.findall(sentence)        #('|'로 나뉘어져 있는 텍스트에서 우측의 원본만을 추출하고 좌측의 링크된 문서 제목은 삭제)

    for token in tokens:
        new_word = token.replace('[[', '').replace(']]', '').split('|')
        new_word = new_word[-1]
        new_word = new_word.replace('\\#', '#').replace('\\\'', '\'')
        sentence = sentence.replace(token, new_word)

    return sentence

def preprocess_delete(sentence, p):
    tokens = p.findall(sentence)

    for token in tokens:
        emptywords = ''
        sentence = sentence.replace(token, emptywords)

    return sentence

def preprocess_norm_00(sentence):       #밑줄 제거
    tokens = pn00.findall(sentence)

    for token in tokens:
        new_word = token.replace('__', '')
        sentence = sentence.replace(token, new_word)

    return sentence

def preprocess_norm_01(sentence):       #글 크기 및 색 변경 패턴 제거
    temp = sentence
    tokens = pn01.findall(temp)

    while(tokens!=[]):
        for token in tokens:
            tk = token.split(' ')
            new_word = ''

            for j in range(1, len(tk)):
                new_word += tk[j] + ' '
            new_word = new_word.replace('}}}', '')
            temp = temp.replace(token, new_word)

        tokens = pn01.findall(temp)

    sentence = temp
    return sentence

def preprocess_norm_02(sentence):       #접기기능 제거
    tokens = pn02.findall(sentence)

    for token in tokens:
        squareBracket = pn02_01.findall(token)
        new_word = token.replace('{{{#!folding ', '').replace('}}}', '').replace(squareBracket[0], '')
        sentence = sentence.replace(token, new_word)

    return sentence

def preprocess_norm_03(sentence):       #html문법을 따르는 텍스트를 일반 텍스트로 바꾸기
    tokens = pn03.findall(sentence)

    for token in tokens:
        new_word = token.replace('{{{#!html ', '').replace('}}}', '')
        sentence = sentence.replace(token, new_word)

    return sentence


def preprocess_tablenl(sentence):       #표에서 개행 문자(\n)를 다른 텍스트로 변경
    tokens = p_tablenl.findall(sentence)

    for token in tokens:
        new_word = token.replace('||\n||', '|| [{nl}] ||')
        sentence = sentence.replace(token, new_word)

    return sentence

def preprocess_tableend(sentence):      #표에서 맨 마지막 부분을 다른 개행 문자와 구분짓기
    tokens = p_tableend.findall(sentence)

    for token in tokens:
        new_word = token.replace('||\n', '|[{end}]|\n')
        sentence = sentence.replace(token, new_word)

    return sentence

def preprocess_table(sentence):         #표와 일반 텍스트를 분리시킴
    tokens = p_table.findall(sentence)

    table = []
    for token in tokens:
        table.append(token)
        emptyword = ''
        sentence = sentence.replace(token, emptyword)

    return sentence, table

def preprocess_initial_nl_delete(sentence):         #문서 시작부분의 개행문자를 없애줌
    newSentence = sentence
    while(newSentence.startswith('\n')):
        newSentence = newSentence[1:]

    return newSentence

def preprocess_return_nl(sentence):
    tokens = p_return_nl.findall(sentence)

    for token in tokens:
        new_word = token.replace('|| [{nl}] ||', '||\n||')
        sentence = sentence.replace(token, new_word)

    return sentence

def preprocess_return_end(sentence):
    tokens = p_return_end.findall(sentence)

    for token in tokens:
        new_word = token.replace('|[{end}]|', '||\n\n')
        sentence = sentence.replace(token, new_word)

    return sentence

def preprocess_residue_nl(sentence):            #지나치게 많은 개행문자를 줄여줌
    temp = sentence
    tokens = p_re_nl.findall(temp)
    while(tokens!=[]):
        temp = temp.replace("\n\n\n", "\n\n")
        tokens = p_re_nl.findall(temp)

    sentence = temp
    return sentence

def printlist(list_2):
    if len(list_2)!=0:
        print(list_2)


def makelist(m,list_t1,list_2d):                #표 텍스트를 이용해서 리스트 생성
    # print('--------\nmakelist function')
    # print("1\n", list_t1)
    # print("m\n", list_t1[m])

    if (m == 0) & (list_t1[m][0:4] == '||||'):  #row span인지 아닌지
        pass
    elif list_t1[m][0:6] == '||||||':           #|||||| -> ||||
        list_t1[m] = list_t1[m][4:]
    elif list_t1[m][0:2] == '||':               #row span이 아니며 ||로 시작하는 경우 -> ||삭제
        list_t1[m] = list_t1[m][2:]

    if list_t1[m][-2:] == '||':                 #끝부분의 || 삭제
        list_t1[m] = list_t1[m][:-2]

    if '||||||||||||||||' in list_t1[m]:        #|*16
        a = 1
    elif '||||||||||||||' in list_t1[m]:        #|*14
        a = 2
    elif '||||||||||' in list_t1[m]:            #|*10
        a = 3
    elif '||||||' in list_t1[m]:                #|*6
        a = 4
    elif '||||' in list_t1[m]:                  #|*4
        a = 5
    else:
        a = 0
        # elif '||||' in list_t1[m]:
        #    a=True
    # print("2\n", list_t1)
    list_t2 = list_t1[m].split('||')  # 첫번째 나누기 : column에 따라 나누는 것, str -> list, rowspan 처리
    # print("3\n",list_t2)
    # for l, k in enumerate(list_t2):
    #    if "||||" in k:
    #        list_t2[l] = k.split('|||') #두번째 나누기 : ||||에 따라 나누기, 리스
    # print(list_t2)
    if a != 0:                                              #a가 0이 아닌 경우 : 빈 칸('||||')이 하나 이상 있는 경우
        for o, word in enumerate(list_t2):
            if word == '':                                  #빈 칸일 경우
                place = 1
                while(place + o < len(list_t2)):            #현재 칸에서 한 칸씩 뒤로가면서
                    if list_t2[o + place] != '':            #내용이 있을 경우
                        list_t2[o] = list_t2[o + place]     #현재 칸에 같은 내용 복사
                        break
                    place += 1
            if list_t2[o] == '':                            #위의 코드 실행 후에도 빈 칸일경우
                place = 1
                while(place <= o):                          #현재 칸에서 한 칸씩 앞으로 가면서
                    if list_t2[o - place] != '':            #내용이 있을경우
                        list_t2[o] = list_t2[o - place]     #현재 칸에 같은 내용 복사
                        break
                    place += 1

                # if list_t2[o + 1] != '':
                #     list_t2[o] = list_t2[o + 1]
                #     # print(list_t2[o])
                # elif list_t2[o + 2] != '':
                #     list_t2[o] = list_t2[o + 2]
                # elif list_t2[o + 3] != '':
                #     list_t2[o] = list_t2[o + 3]
                # elif list_t2[o + 4] != '':
                #     list_t2[o] = list_t2[o + 4]
                # elif list_t2[o + 5] != '':
                #     list_t2[o] = list_t2[o + 5]
                # elif list_t2[o + 6] != '':
                #     list_t2[o] = list_t2[o + 6]

    # print("list_t2\n", list_t2)
    # print("-------\n")
    list_2d.append(list_t2)

def colspan(list_2d):
    # print('========\ncolspan function')
    # print('before\n', list_2d)
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
    # print('after\n', list_2d)
    # print('========\n')


def table2list2d(table_text):       #표를 2차원 리스트로 변경
    #print(table_text)
    #print('table')
    list_t1 = table_text.split('\n')

    list_2d1 = []                   #한 문서 내에 있는 여러 표를 리스트로 저장하기 위해서
    list_2d2 = []                   #여러 개의 빈 리스트를 생성함
    list_2d3 = []
    list_2d4 = []
    list_2d5 = []

    nextlistswitch = 0              #한 문서 내에 여러 리스트가 있는 경우 다음
    listIndex = 0
    for m, p in enumerate(list_t1):
        if (list_t1[m][0:2]!='||')and(list_t1[m][-2:]!='||'): #만약에 table_text의 첫번째 줄에 양쪽끝이 둘다 ||로 닫힌 경우가 아닌경우 : 테이블이 아닌경우
            if len(list_2d1)==0: #list_2d의 길이가 0인 경우
                #print("list_2d1 length : ", len(list_2d1))
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

    # makelist(m, list_t1, list_2d)
    # colspan(list_2d)
    # print("list_2d\n", list_2d)
    #
    # return list_2d

    # print("========\nlist_2d1 : \n")
    # printlist(list_2d1)
    # print("\nlist_2d1\n========\n")
    #
    # print("========\nlist_2d2 : \n")
    # printlist(list_2d2)
    # print("\nlist_2d2\n========\n")
    #
    # print("========\nlist_2d3 : \n")
    # printlist(list_2d3)
    # print("\nlist_2d3\n========\n")
    #
    # print("========\nlist_2d4 : \n")
    # printlist(list_2d4)
    # print("\nlist_2d4\n========\n")
    #
    # print("========\nlist_2d5 : \n")
    # printlist(list_2d5)
    # print("\nlist_2d5\n========\n")

    return list_2d1


count = 0

translation_list_initialization()
#main code
for doc in parse_namuwiki_json(debug=False):
    document_title = str(doc['title'])
    document_str = str(doc['text'])

    isRedirect = redirect_check(document_str)   #doc가 리다이렉트 문서인지 여부를 저장
    if(isRedirect == True):                     #doc가 리다이렉트 문서일 경우
        before = document_title
        after = return_translation_result(document_str)
        print("### redirect document ###")
        print("before : ", before)
        print("after  : ", after)
        print("#########################")
        translation_list_write(before, after)
        continue                                #이하의 처리 코드를 모두 건너뛰고 다음 doc으로 이동

    #전처리 진행
    document_str = preprocess0(document_str, p1)

    for pat in pattern_sim_list:
        document_str = preprocess_delete(document_str, pat)

    for pat in pattern_del_list:
        document_str = preprocess_delete(document_str, pat)

    document_str = preprocess_norm_00(document_str)
    document_str = preprocess_norm_01(document_str)
    document_str = preprocess_norm_02(document_str)
    document_str = preprocess_norm_03(document_str)

    document_str = preprocess_link(document_str, pex_link)

    for pat in pattern_delal_list:
        document_str = preprocess_delete(document_str, pat)

    #document_str = document_str.replace('{{{', '{z').replace('}}}', 'z}')
    #document_str = preprocess1(document_str, p2) #전처리1 {{{}}}

    document_str = preprocess_tableend(document_str)
    document_str = preprocess_tablenl(document_str)

    document_str, table = preprocess_table(document_str)

    document_str = preprocess_initial_nl_delete(document_str)


    for i in range(len(table)):
        table[i] = preprocess_return_nl(table[i])
        table[i] = preprocess_return_end(table[i])
        #print(table[i])

    for pat in pattern_residue_list:
        document_str = preprocess_delete(document_str, pat)

    document_str = preprocess_residue_nl(document_str)

    # document_str.replace('||\n=', '||\n\n=').replace('||\n *', '||\n\n *') #왼쪽 문자열을 오른쪽으로 변환        ???
    # table_list_ = document_str.split('||\n\n') #||\n\n기준으로 문자열 분리 -> 리스트로 반환
    # table_list = []
    # scores = []
    #
    # #table
    # for i, table_text in enumerate(table_list_):    #||\n\n으로 분리된 문자열(document_str)을 하나씩 가져옴
    #     new_table_text = ''
    #     opened = False
    #     check1 = 1                                  #???
    #     check2 = 1                                  #???
    #
    #     for j in range(len(table_text)):
    #         if j > 1:
    #             if table_text[j - 1] == '|' and table_text[j - 2] == '|':   #표의 행 시작
    #                 opened = True
    #             if table_text[j - 1] == '\n' and table_text[j] == '|':      #표 개행
    #                 check1 += 1
    #             if table_text[j] == '\n':
    #                 check2 += 1
    #
    #         if opened is True:                                              #표의 행이 시작됐을 때
    #             new_table_text += table_text[j]                             #테이블 텍스트에 삽입하기 시작함
    #
    #
    #     if opened is True:
    #         table_list.append(new_table_text)
    #         scores.append(check1 / check2)                                  #???

    # for k, table_text in enumerate(table_list):  #dictionary와 비슷, key값과 value값
    #     table_text = table_text.replace('[[', '{x').replace(']]', 'x}')   #[[]] : 하이퍼링크 단어
    #     table_text = re.sub(pattern=pattern1, repl='', string=table_text)  #특수문자 제거
    #     table_text = preprocess2(table_text, p3) #전처리2 [[]]
    #
    #
    #     if "||||" in table_text:
    #         (table2list2d(table_text))
    #     elif "|| '" in table_text:
    #         (table2list2d(table_text))
    #     elif "|| " in table_text:
    #         (table2list2d(table_text))
    #     elif "||\n||" in table_text:
    #         (table2list2d(table_text))

    #표를 2d list로 처리
    table_result = []
    for tb in table:
        result = table2list2d(tb[2:])
        table_result.append(result)

    #printing preprocessed result
    # print('\n================')
    # print('---------------title--------------')
    # print(document_title)  # title 출력
    # print('----------------------------------\n')
    # print("--------document_str_start--------")
    # print(document_str)                                 #문서 text 출력
    # print("----------------------------------\n")
    # print("-----------table_start------------")
    # print(table_result)                         #문서 table 출력
    # print("------------table_done------------\n")
    # print("================\n")

    #save all in a json file
    savePreprocessedJson(document_title, document_str, table_result)

    # count += 1            #실험적으로
    # if (count>5000):      #일부 문서만 처리할 경우
    #    break              #주석 해제

    # input()            #문서 전처리 결과를 하나 씩 확인할 때 주석 해제

saveLeftoverPreprocessedJson()
translation_list_finalization()