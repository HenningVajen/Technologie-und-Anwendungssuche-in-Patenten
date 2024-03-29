import utility_Index_und_Suche
import config


def alleDokumente():
    #Rückgabe aller Dokumente in einem Index
    query_ = {"match_all": {}}
    resp = esClient.search(index=index_, query=query_)
    return resp


def sucheEinFeld (keyword, feld):
    #Suche in einzelnen Feldern
    #Keywords sind oder-Verknüpft
    query_ = {
            "match": {
                str(feld): str(keyword)
            }
        }
    resp = esClient.search(index=index_, query=query_)

    return resp


def sucheStringQuery(keywords, felder = "volltext"):
    #Felder und Query als Liste übergeben und zu json zusammensetzen

    if felder == "volltext":
        felder = ["title", "abstract", "claims", "description"]

    query_ = {
        "query_string": {
            "query": keywords,
            "fields": felder

        }
    }
    resp = esClient.search(index=index_, query=query_)
    return resp


def sucheSatzweise(keywords):
    query_ = {
        "match": {
            "satz": str(keywords)
        }
    }
    resp = esClient.search(index=config.esIndexSaetze, query=query_)
    return resp


def suchePhrase (keyword,feld):
    #Suche in einzelnen Feldern
    #Keywords sind oder-Verknüpft

    query_ = {
            "match_phrase": {
                str(feld): str(keyword)
            }
        }
    resp = esClient.search(index=index_, query=query_)

    return resp


def sucheStringQueryPOS(keywords, felder = "volltext"):
    #Felder und Query als Liste übergeben und zu json zusammensetzen

    if felder == "volltext":
        felder = ["title", "abstract", "claims", "description"]

    query_ = {
        "query_string": {
            "query": keywords,
            "type": "phrase",
            "fields": felder

        }
    }
    resp = esClient.search(index=index_, query=query_)
    return resp


if __name__ == "__main__":
    print('Ausführung als main: ' + __file__)

    #TESTEINGABEN
    #esClient = utility_Index_und_Suche.clientStarten(config.esPort)
    #index_ = esIndexText
    #antwort = alleDokumente()
    #antwort = sucheEinFeld("manufacturing liquid", "title")
    #antwort = sucheStringQuery("(virtual machine) OR (manufacturing liquid)", ["title"])
    #antwort = sucheSatzweise("detection")
    #POS Suche
    #index_ = config.esIndexText_POS
    #antwort = suchePhrase("machine|NOUN", "title")
    #antwort = sucheStringQueryPOS("machine|NOUN", ["title"])
    #print("Anzahl der Treffer: %d" % antwort['hits']['total']['value'])
    #for hit in antwort['hits']['hits']:
    #    print(hit['_source']['publication_number'])
    #    print(hit['_source']['title'])




