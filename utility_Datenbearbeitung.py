from datetime import datetime
import json
import os
import pickle

import utility_Index_und_Suche
import utility_NLP_Bearbeitung



#-----------------------    CONFIG   -----------------------
pfadDateneingabe = os.path.join(os.getcwd(), "input") #Verzeichnis in dem .json Patentdaten gesucht und verarbeitet werden sollen
pfadDatenausgabe = os.path.join(os.getcwd(), "output") #Verzeichnis in dem (bearbeitete) Daten abgelegt werden
bezeichnungWoerterbuch ="woerterbuch_metadaten.pkl" #Dateiname der Wörterbuchdatei (im Wörterbuch sind zu den Patennnummern weiter Felder mit Informationen zum Patent abgelegt
anzahlDokumenteInBlock = 10 #Anzahl an Dokumenten je Bearbeitungsblock
esPort = 9200 #Port des Elasticsearch Servers
esIndexText ="text_text" #Bezeichung des Index von Elasticsearch
esIndexSaetze ="saetze_text" #Bezeichung des Index von Elasticsearch
esIndexWoerterbuch ="woerterbuch_text" #Bezeichung des Index von Elasticsearch

#-----------------------------------------------------------



def dateienEinlesen(_pfad):
    _dateienListe = os.listdir(_pfad)  # Dateiliste im Verzeich der Datenablage erstellen
    for datei in _dateienListe:
        if not ('.json' in datei):
            _dateienListe.remove(datei)
    return _dateienListe


def leseJSONlines(dateienListe_):
    patentdatenObjekt_ = dict()
    anzahlDoubletten = 0
    cpcLeerDict = {"code" : "unknown"}
    cpcLeereListe = [cpcLeerDict, cpcLeerDict]

    for datei_ in dateienListe_:
        with open(os.path.join(pfadDateneingabe, datei_), 'r') as jsonDatei:
            for line in jsonDatei:
                temp = json.loads(line)
                if not temp["cpc"]: #Fängt leere Einträge ab
                    temp["cpc"] = cpcLeereListe
                #print(str(temp["publication_number"]) + "   " + str(temp["cpc"]))
                if patentdatenObjekt_.__contains__(temp["publication_number"]):
                    anzahlDoubletten = anzahlDoubletten + 1
                    print(str(anzahlDoubletten) + " doppelte Publication Number gefunden: "  + temp["publication_number"] + ".    Nur der erste Eintrag wird verarbeitet.")
                else:
                    patentdatenObjekt_[temp["publication_number"]] = {
                    "publication_date": int(temp["publication_date"]),
                    "title": temp["title"],
                    "abstract": temp["abstract"],
                    "claims": temp["claims"],
                    "description": temp["description"],
                    "cpc": temp["cpc"][0]['code'], #aus dem dict wird der CPC Code des erste (Haupt-)Eintrags übernommen
                    "assignee1": temp["assignee1"],
                }
    print(str(patentdatenObjekt_.__len__()) + " Datensätze eingelesen")
    return patentdatenObjekt_


def zaehlenEinzigartigerPatente(dateienListe_):
    patentdatenObjekt_ = dict()
    anzahlDoubletten = 0
    for datei_ in dateienListe_:
        with open(os.path.join(pfadDateneingabe, datei_), 'r') as jsonDatei:
            for line in jsonDatei:
                temp = json.loads(line)
                print (temp["cpc"][0]['code'])
                if patentdatenObjekt_.__contains__(temp["publication_number"]):
                    anzahlDoubletten = anzahlDoubletten + 1
                    print(str(anzahlDoubletten) + " DOUBLETTE GEFUNDEN "  + temp["publication_number"])
                patentdatenObjekt_[temp["publication_number"]] = {
                }


def split_dictionary(input_dict, chunk_size):
    res = []
    new_dict = {}
    for k, v in input_dict.items():
        if len(new_dict) < chunk_size:
            new_dict[k] = v
        else:
            res.append(new_dict)
            new_dict = {k: v}
    res.append(new_dict)
    return res


def speichereObjekt(object, pfad, dateiname):
    is_stored = True
    try:
        file = open(os.path.join(pfad, dateiname), 'wb')
        pickle.dump(object, file)
        file.close()
    except Exception as e:
        print("Speicherung des Objektes fehlgeschlagen")
        print(str(e))
        is_stored = False
    finally:
        return is_stored


def ladeObjekt(pfad, dateiname):
    file = open(os.path.join(pfad, dateiname), 'rb')
    objekt = pickle.load(file)
    file.close()
    return objekt


def jsonDateienEinlesen(pfadDateneingabe):
    print("\n", '########## Einlesen der Dateien ##########')
    print("Pfad der Daten: " + str(pfadDateneingabe))
    dateienListe = dateienEinlesen(pfadDateneingabe)
    print("Einlesen der Dateie(n) " + str(dateienListe))
    patentdatenDict = dict()
    patentdatenDict = leseJSONlines(dateienListe)
    return patentdatenDict



if __name__ == "__main__":
    zeitpunktStart = datetime.now()
    print('Ausführung als main')

    print("\n", '########## Einlesen der Dateien ##########')
    print("Pfad der Daten: " + str(pfadDateneingabe))
    dateienListe = dateienEinlesen(pfadDateneingabe)
    print("Einlesen der Dateie(n) " + str(dateienListe))
    patentdatenDict = dict()
    patentdatenDict = leseJSONlines(dateienListe)
    print("Speicherung des Wörterbuchs im Pfad " + str(pfadDatenausgabe))
    print(speichereObjekt(patentdatenDict,pfadDatenausgabe,bezeichnungWoerterbuch))


    print("\n", '########## NLP Bearbeitugn und Indexierung ##########')
    #Aufteilung der Dokumente für die Bearbeitung und Indexierung, zur Reduktion des benötigten Speichers
    anzahlBloecke = int((patentdatenDict.__len__() - 1) / anzahlDokumenteInBlock) + 1
    print("Daten werden aufgeteilt in Blöcke zu " + str(anzahlDokumenteInBlock) + " Datensätzen. Anzahl der Blöcke = " + str(anzahlBloecke))
    dictListe = split_dictionary(patentdatenDict, anzahlDokumenteInBlock)


    #Starten des Elasticsearch Servers und anlegen der Indexes
    esClient = utility_Index_und_Suche.clientStarten(esPort)
    utility_Index_und_Suche.indexLoeschen(esClient, esIndexText) #Löschen der alten Indexes zu Testzwecken
    utility_Index_und_Suche.indexLoeschen(esClient, esIndexSaetze) #Löschen der alten Indexes zu Testzwecken
    utility_Index_und_Suche.indexAnlegen(esClient, esIndexText)
    utility_Index_und_Suche.indexAnlegen(esClient, esIndexSaetze)

    esIndicesClient = utility_Index_und_Suche.indicesClientStarten(esClient)



    resp = esIndicesClient.analyze(
        body={
            "tokenizer": "whitespace",
            "filter": ["delimited_payload"],
            "text": "the|0 brown|10 fox|5 is|0 quick|10",
        }
    )
    pass
    for token in resp['tokens']:
        print(token)



    #NLP Bearbeitung und Indexierung in Blöcken
    i=1
    for patentdatenDict in dictListe:
        print("Bearbeitung von Block " + str(i) + " von " + str(anzahlBloecke))
        neuesDict = {}
        neuesDict = utility_NLP_Bearbeitung.nlpPipelineDurchlaufen(patentdatenDict, "en_core_web_sm")

        for key in neuesDict:
            #Indexierung der einzelnen Felder jedes Patentes zusammen mit dem Feld der Patentnummer
            docText = {
                "publication_number": key,
                "title": neuesDict[key]['title'],
                "abstract": neuesDict[key]['abstract'],
                "claims": neuesDict[key]['claims'],
                "description": neuesDict[key]['description'],
                "assignee": neuesDict[key]['assignee1']
            }
            utility_Index_und_Suche.dokumentIndexieren(esClient, esIndexText, docText)

            #Ablage jedes Satzes, jedes Dokumentes in einem Indexeintrag zusammen mit dem Feld der Patentnummer
            saetze = list(neuesDict[key]['NLP_doc'].sents)
            for satz in saetze:
                utility_Index_und_Suche.dokumentIndexieren(esClient,esIndexSaetze, {"publication_number": key, "satz": str(satz)})

        del(neuesDict)
        i+=1


    #zaehlenEinzigartigerPatente(dateienListe)
    #MOST_NLP_Bearbeitung.objektVisualisieren(patentdatenDict)

    text1 = "super title1 Hallo Welt, nice to meet you. Ich beanspruche Weltherrschaft. Schreibtisch"
    saetze1 = "..."
    doc1 = {
        'publicationDate': "20220101",
        'title': "super title1",
        'abstract': "Hallo Welt, nice to meet you.",
        'claims': "Ich beanspruche Weltherrschaft",
        'description': "Schreibtisch",
        'cpc': "A1B2C3",
        'assignee': "Hugo Hubertus",
    }


    doc2 = {
        'publicationDate': "20220101",
        'title': "super title2",
        'abstract': "Hallo Welt, nice to meet you.",
        'claims': "Ich beanspruche Weltherrschaft",
        'description': "Selbsterklärend",
        'cpc': "A1B2C3",
        'assignee': "Hugo Hubertus",
    }

    utility_Index_und_Suche.dokumentIndexieren(esClient,esIndexText,doc1)
    utility_Index_und_Suche.dokumentIndexieren(esClient, esIndexText, doc2)
    utility_Index_und_Suche.refresh(esClient, esIndexText)
    #print(MOST_elastic.getDocument(esIndex,esClient,"V0IblIQBXLfNnWU7TaQ0"))

    query = {
        "match": {
            "description": "Schreibtisch"
        }
    }
    # query = {
    #     "match_all": {
    #         "Schreibtisch"
    #     }
    # }

    response=utility_Index_und_Suche.search(esClient,esIndexText,query)


    zeitpunktEnde = datetime.now()
    print("\n", "Dauer der Bearbeitung = ", zeitpunktEnde - zeitpunktStart)
