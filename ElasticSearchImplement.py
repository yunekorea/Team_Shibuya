import json
import os
from encodings import utf_8
from elasticsearch import Elasticsearch
from elasticsearch import helpers

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# path to the files
path = r"C:\Users\anuuj\Desktop\PNU\Graduation project\docs\\"
datas = []


# making the index
def make_index(es, index_name):
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    print(es.indices.create(index=index_name))


index_name = "shibuya"

# makes new index everytime the code runs
make_index(es, index_name)


# read text file
def read_text_file_and_index(path_to_json):
    for file_name in [file for file in os.listdir(path_to_json) if file.endswith('.json')]:
        with open(path_to_json + file_name, encoding="utf8") as json_file:
            data = json.load(json_file)
            for jsonObject in data:
                es.index(index=index_name, doc_type='string', body=jsonObject)
    for file_name in [file for file in os.listdir(path_to_json) if file.endswith('.txt')]:
        with open(path_to_json + file_name, 'r', encoding="utf8") as f:
            lines = f.read()
            title = lines.split('\n', 1)[0]
            texts = lines.split('\n', 1)[1:]

            doc = {}
            doc = {'text': texts, 'title': title}

            es.index(index=index_name, doc_type='string', body=doc)


read_text_file_and_index(path)

# search
results = es.search(index=index_name, body={"query": {
    "bool": {"should": [{"match": {"title": "#FairyJoke"}}, {"match": {"text": "지미 카터"}}, {"match": {"table": ""}}]}}})
for result in results['hits']['hits']:
    print("***************************************************")
    print('score:', result['_score'], 'source:', result['_source'])