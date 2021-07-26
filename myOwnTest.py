import ijson

def load_json(filename):
    count=0
    with open(filename, 'r') as fd:
        parser = ijson.parse(fd)
        for prefix, event, value in parser:
            if prefix.endswith('.title'):
                print('index=', count+1)
                print("\nTITLE: %s" % value)
            elif prefix.endswith('.text'):
                print("\nCONTENT: %s" % value)
                count += 1
            # debug
            if count== 1 :
                break

def load_json_title(title):
    filename = 'docData200302.json'
    doc = 0
    with open(filename, 'r') as fd:
        parser = ijson.parse(fd)
        for prefix, event, value in parser:
            if prefix.endswith('.title'):
                if(value == title):
                    doc = 1
                    print("\nTITLE: %s" % value)
            elif prefix.endswith('.text'):
                if(doc == 1):
                    print("\nCONTENT: %s" % value)
                    doc = 0
                    break

def procResultShow(filename):
    count=0
    with open(filename, 'r') as fd:
        parser = ijson.parse(fd)
        for prefix, event, value in parser:
            if prefix.endswith('.title'):
                print('index=', count+1)
                print("\nTITLE: %s" % value)
            elif prefix.endswith('.text'):
                print("\nCONTENT: %s" % value)
            elif prefix.endswith('.table'):
                print("\nTABLE: %s" % value)
                count += 1
            # debug
            if count== 100 :
                break

if __name__ == "__main__":
    #load_json('docData200302.json')
    #load_json_title('*NSYNC')
    procResultShow('processedWiki.json')


