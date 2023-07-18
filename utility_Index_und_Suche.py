import sys
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient



def clientStarten(_port):
    client = None
    client = Elasticsearch("http://localhost:"+str(_port))
    if client.ping():
        print("Verbindung zum Elasticsearch Server hergestellt")
        return client
    else:
        print("Verbindung zum Elasticsearch Server fehlgeschlagen. Verwendendeter Port: " +str(_port))
        return False
        #sys.exit()



def indicesClientStarten(client):
    indices_client = IndicesClient(client)
    return indices_client

def indexAnlegen(_client, _index):
    #Erstellt einen neuen Index, wenn dieser noch nicht vorhanden ist
    try:
        _client.indices.create(
            index=_index,
            body={
                "settings": {"number_of_shards": 1}
            }
            # body={
            #     "settings": {"number_of_shards": 1},
            #     "mappings": {
            #         "dynamic": "strict", #Verhindet das Hinzufügen von neuen Felder während der Laufzeit
            #         "properties": {
            #             "publicationDate": {"type": "date", "format": "yyyymmdd"},
            #             "title": {"type": "text"},
            #             "abstract": {"type": "text"},
            #             "claims": {"type": "text"},
            #             "description": {"type": "text"},
            #             "cpc": {"type": "text"},
            #             "assignee": {"type": "text"}
            #         }
            #     },
            # },
            #ignore=400,
        )
        print("Index " + str(_index) + " angelegt / zugegriffen")
    except Exception as e:
        print("Indexerstellung oder Zugriff fehlgeschlagen")
        print(e)

def refresh(client_, index_):
    #Übernimmt die Änderungen am Index und macht ihn für die Suche verfügbar
    try:
        response = client_.indices.refresh(index=index_)
        print ("Index '"+index_+"' aktualisiert. Änderungen verfügbar.")
        print(response)
    except Exception as e:
        print("Aktualisierung des Indexes fehlgeschlagen")
        print(e)


def indexLoeschen(_client, _index):
    try:
        response = _client.options(ignore_status=[400, 404]).indices.delete(index=_index)
        print("Löschung des Indexes '"+ str(_index) + "' erfolgreich." + str(response))
    except Exception as e:
        print("Indexlöschung fehlgeschlagen")
        print(e)


def dokumentIndexieren(client, index, data):
    is_stored = True
    try:
        #outcome = client.index(index=index, doc_type='_doc', body=data)
        outcome = client.index(index=index, document=data)
        #print(outcome)
    except Exception as e:
        print("Indexierung eines Dokumentes fehlgeschlagen")
        print(str(e))
        is_stored = False
    finally:
        return is_stored


def getDocument(index_, client_, id_):
    resp = client_.get(index=index_, id=id_)
    #print(resp['_source'])
    return(resp['_source'])


def search(client_, index_, query):
    resp = client_.search(index=index_ ,query=query, size=1000) #size means the max. number of documents that are stored in the response. 10000 is the Elasticsearch Limits w/o changes to the Server
    print("Trefferanzahl: " + str(resp['hits']['total']['value']))
    #for hit in resp['hits']['hits']:
    #   print(hit['_source']['title'])
    return resp['hits']['hits']





