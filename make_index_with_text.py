# import module
import os
from encodings import utf_8
from elasticsearch import Elasticsearch
from elasticsearch import helpers


es: Elasticsearch = Elasticsearch("http://localhost:9200/")


# folder path
path = r"C:\Users\anuuj\Desktop\PNU\Graduation project\docs\test_docs"

# change the directory
os.chdir(path)

# making the index
def make_index(es, index_name):
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    print(es.indices.create(index=index_name))

index_name = 'test'
make_index(es, index_name)

# read text File
def read_text_file(file_path):
    with open(file_path, 'r', encoding="utf_8") as f:
        lines = f.read()
        title = lines.split('\n', 1)[0] # getting the first line and save it in title
        texts = lines.split('\n', 1)[1:] # rest of the lines are saved in the texts

        es.index(index=index_name, doc_type='string', body=texts)

#        print(f.read())
        print(title)
        print(texts)

# iterate through all file
for file in os.listdir():
    # Check whether file is in text format or not
    if file.endswith(".txt"):
        file_path = f"{path}\{file}"

        # call read text file function
        read_text_file(file_path)

es.indices.refresh(index=index_name)
results = es.search(index=index_name, body={'from':0, 'size':10, 'query':{'match':{'한국어'}}})
for result in results['hits']['hits']:
    print('score:', result['_score'], 'source:', result['_source'])

