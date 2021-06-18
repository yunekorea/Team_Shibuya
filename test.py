import re

doc = '||<-2><:>기점||<width=300px><:>서울특별시 서대문구 북가좌동(북가좌동차고지)||<-2><:>종점||<width=300px><:>서울특별시 금천구 가산동(가산동차고지)||'
doc = '||<|2><width=50px><:>종점행||<width=50px><:>첫차||<:>?||<|2><width=50px><:>기점행||<width=50px><:>첫차||<:>?||'
doc = doc.replace('<|', '<r')
doc = doc.replace('<-', '<c')

pattern1 = '<c[^>]*>'
pattern2 = '<r[^>]*>'

p1 = re.compile(pattern1)
p2 = re.compile(pattern2)

#re.sub(pattern=pattern, repl='', string=doc)

print(p1.findall(doc))
print(p2.findall(doc))
