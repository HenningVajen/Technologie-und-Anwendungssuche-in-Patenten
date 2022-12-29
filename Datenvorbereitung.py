from datetime import datetime
import os
import spacy

import utility_Datenbearbeitung
import utility_Index_und_Suche
import utility_NLP_Bearbeitung



#-----------------------    CONFIG   -----------------------
pfadDateneingabe = os.path.join(os.getcwd(), "input") #Verzeichnis in dem .json Patentdaten gesucht und verarbeitet werden sollen
pfadDatenausgabe = os.path.join(os.getcwd(), "output") #Verzeichnis in dem (bearbeitete) Daten abgelegt werden
bezeichnungWoerterbuch ="woerterbuch.pkl" #Dateiname der Wörterbuchdatei (im Wörterbuch sind zu den Patennnummern weiter Felder mit Informationen zum Patent abgelegt
anzahlDokumenteInBlock = 10 #Anzahl an Dokumenten je Bearbeitungsblock
esPort = 9200 #Port des Elasticsearch Servers
esIndexText ="text_test" #Bezeichung des Index von Elasticsearch
esIndexSaetze ="saetze_test" #Bezeichung des Index von Elasticsearch
enablePayload = False  #True: Es wird die Wortart als Payload hinzugeführt; Bsp. "Coded|ADJ spectral|ADJ imager|NOUN"
enableLemma = False    #True: Lemmatisiert alle Ausdrücke und Worte
indexLoeschen = False #True: Löscht den bestehenden Index und leg einen leeren neuen Index an, z.B. zu Testzwecken
#-----------------------------------------------------------





if __name__ == "__main__":
    zeitpunktStart = datetime.now()
    print('Ausführung als main: ' + __file__)

    esClient = utility_Index_und_Suche.clientStarten(esPort)

    #modus 0: Anlegen Index, Einlesen der Dateien, NLP-Bearbeitung, Indexieren
    #modus 1: Refrehes der Indizes

    modus = 0


    if modus == 0:

        # Starten des Elasticsearch Servers und anlegen der Indexe
        if indexLoeschen:
            utility_Index_und_Suche.indexLoeschen(esClient, esIndexText)  # Löschen der alten Indexes zu Testzwecken
            utility_Index_und_Suche.indexLoeschen(esClient, esIndexSaetze)  # Löschen der alten Indexes zu Testzwecken
        utility_Index_und_Suche.indexAnlegen(esClient, esIndexText)
        utility_Index_und_Suche.indexAnlegen(esClient, esIndexSaetze)
        esIndicesClient = utility_Index_und_Suche.indicesClientStarten(esClient)

        #Starten von Spacy (In main und nicht im jeweiligen Funktionsaufruf, zur Laufzeitoptimierung)
        nlp = spacy.load("en_core_web_sm")

        patentdatenDict = utility_Datenbearbeitung.jsonDateienEinlesen(pfadDateneingabe)
        print("Speicherung des Wörterbuchs im Pfad " + str(pfadDatenausgabe))
        print(utility_Datenbearbeitung.speichereObjekt(patentdatenDict, pfadDatenausgabe, bezeichnungWoerterbuch))


        print("\n", '########## NLP Bearbeitugn und Indexierung ##########')
        # Aufteilung der Dokumente für die Bearbeitung und Indexierung, zur Reduktion des benötigten Speichers
        anzahlBloecke = int((patentdatenDict.__len__() - 1) / anzahlDokumenteInBlock) + 1
        print("Daten werden aufgeteilt in Blöcke zu " + str(
            anzahlDokumenteInBlock) + " Datensätzen. Anzahl der Blöcke = " + str(anzahlBloecke))
        dictListe = utility_Datenbearbeitung.split_dictionary(patentdatenDict, anzahlDokumenteInBlock)
        # NLP Bearbeitung und Indexierung in Blöcken
        i = 1
        for patentdatenDict in dictListe:
            print("Bearbeitung von Block " + str(i) + " von " + str(anzahlBloecke))
            neuesDict = {}
            neuesDict = patentdatenDict
            neuesDict = utility_NLP_Bearbeitung.nlpPipelineDurchlaufen(patentdatenDict)


            for key in neuesDict:
                if enablePayload == True:
                    # Hinzufügen der POS Tags nach jedem Wort als Payload für jeden Eintrag im Dict
                    docText = {
                        "publication_number": key,
                        "title": utility_NLP_Bearbeitung.posPayloadEinfuegen(neuesDict[key]['title'], enableLemma, nlp),
                        "abstract": utility_NLP_Bearbeitung.posPayloadEinfuegen(neuesDict[key]['abstract'], enableLemma, nlp),
                        "claims": utility_NLP_Bearbeitung.posPayloadEinfuegen(neuesDict[key]['claims'], enableLemma, nlp),
                        "description": utility_NLP_Bearbeitung.posPayloadEinfuegen(neuesDict[key]['description'], enableLemma, nlp),
                        "assignee": neuesDict[key]['assignee1']
                    }
                else:
                    docText = {
                        "publication_number": key,
                        "title": neuesDict[key]['title'],
                        "abstract": neuesDict[key]['abstract'],
                        "claims": neuesDict[key]['claims'],
                        "description": neuesDict[key]['description'],
                        "assignee": neuesDict[key]['assignee1']
                    }
                utility_Index_und_Suche.dokumentIndexieren(esClient, esIndexText, docText)

                # Ablage jedes Satzes, jedes Dokumentes in einem Indexeintrag zusammen mit dem Feld der Patentnummer
                saetze = list(neuesDict[key]['NLP_doc'].sents)
                for satz in saetze:
                    if enablePayload:
                        satz_ = utility_NLP_Bearbeitung.posPayloadEinfuegen(str(satz),enableLemma, nlp)
                    else:
                        satz_=str(satz)
                    utility_Index_und_Suche.dokumentIndexieren(esClient, esIndexSaetze, {"publication_number": key, "satz": satz_})
            del (neuesDict)
            i += 1

    if modus == 1:
        utility_Index_und_Suche.refresh(esClient, esIndexText)
        utility_Index_und_Suche.refresh(esClient, esIndexSaetze)

    if modus == 2:
        pass

    if modus == 3:

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

    if modus == 4:
        #zaehlenEinzigartigerPatente(dateienListe)
        #NLP_Bearbeitung.objektVisualisieren(patentdatenDict)

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
        #print(elasticsearch.getDocument(esIndex,esClient,"V0IblIQBXLfNnWU7TaQ0"))

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

        response=utility_Index_und_Suche.suche(esClient,esIndexText,query)

    zeitpunktEnde = datetime.now()
    print("\n", "Dauer der Bearbeitung = ", zeitpunktEnde - zeitpunktStart)
    #todo: OPTIMIERUNG: Visualisierung -  Einen Prograss-Bar z.B. mit tqdm einfügen