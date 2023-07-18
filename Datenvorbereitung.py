import config

from datetime import datetime
import os
import spacy

import utility_Datenbearbeitung
import utility_Index_und_Suche
import utility_NLP_Bearbeitung
import copy
import multiprocessing
from until_index_dict_parts import index_dict_parts
from tqdm import tqdm
import csv





if __name__ == "__main__":
    zeitpunktStart = datetime.now()
    print('Ausführung als main: ' + __file__)

    esClient = utility_Index_und_Suche.clientStarten(config.esPort)

    #modus 0: Anlegen Index, Einlesen der Dateien, NLP-Bearbeitung, Indexieren
    #modus 1: Refrehes der Indizes; wird periodisch von Elasticsearch gemacht, jedoch nur in Indizes in denen auch Suche durchgeführt werden. Um sicherzustellen, dass alle Änderunge enthalten sind, kann ein manueller refresh durchgeführt werden
    #modul 2: Erstelles der Wörterbuches der Metadaten der Dokumente im Input-Verzeichnis. Kann verwendet werden, der Index nicht einer Session erstellt wird. In diesem Fall muss das Wörterbuch über alle Dokumente separat erzeugt werden. Achtung: Es wird nicht angehangen. Erstellung in einem Aufruf.

    modus = 0

    if modus == 0:

        # Starten des Elasticsearch Servers und anlegen der Indexe
        if config.indexLoeschen:
            utility_Index_und_Suche.indexLoeschen(esClient, config.indexFulltext)
            utility_Index_und_Suche.indexLoeschen(esClient, config.indexFulltextPOS)
            utility_Index_und_Suche.indexLoeschen(esClient, config.indexSentence)
            utility_Index_und_Suche.indexLoeschen(esClient, config.indexSentencePOS)
        utility_Index_und_Suche.indexAnlegen(esClient, config.indexFulltext)
        utility_Index_und_Suche.indexAnlegen(esClient, config.indexFulltextPOS)
        utility_Index_und_Suche.indexAnlegen(esClient, config.indexSentence)
        utility_Index_und_Suche.indexAnlegen(esClient, config.indexSentencePOS)
        esIndicesClient = utility_Index_und_Suche.indicesClientStarten(esClient)

        #Starten von Spacy (In main und nicht im jeweiligen Funktionsaufruf, zur Laufzeitoptimierung)
        nlp = spacy.load(config.spacyModel)

        patentdatenDict = utility_Datenbearbeitung.jsonDateienEinlesen(config.pfadDateneingabe)

        # Speicherung der Metadaten des Wörterbuches zur späteren Verwendung im Backend
        print("\n", '########## Speicherung des Wörterbuchs der Metadaten ##########')
        print("Speicherung des Wörterbuchs mit den Metadaten der eingelesenen Patente im Pfad " + str(config.pfadDatenausgabe))
        patentdatenDict_META = copy.deepcopy(patentdatenDict)
        for eintrag in patentdatenDict_META:
            del patentdatenDict_META[eintrag]["abstract"]
            del patentdatenDict_META[eintrag]["claims"]
            del patentdatenDict_META[eintrag]["description"]
        print(utility_Datenbearbeitung.speichereObjekt(patentdatenDict_META, config.pfadDatenausgabe, config.bezeichnungWoerterbuch))


        def index_documents(patentdatenDict):
            print("\n", '########## NLP Bearbeitugn und Indexierung ##########')
            print("Startzeit der Bearbeitung: " + str(datetime.now()))
            # Aufteilung der Dokumente für die Bearbeitung und Indexierung, zur Reduktion des benötigten Speichers
            anzahlBloecke = int((patentdatenDict.__len__() - 1) / config.anzahlDokumenteInBlock) + 1
            print("Daten werden aufgeteilt in Blöcke zu " + str(
                config.anzahlDokumenteInBlock) + " Datensätzen. Anzahl der Blöcke = " + str(anzahlBloecke))
            dictListe = utility_Datenbearbeitung.split_dictionary(patentdatenDict, config.anzahlDokumenteInBlock)
            # NLP Bearbeitung und Indexierung in Blöcken
            block_startzeit = 0
            letzter_block_startzeit = 0
            i = 1
            for patentdatenDict in dictListe:
                print("Bearbeitung von Block " + str(i) + " von " + str(anzahlBloecke))
                block_startzeit = datetime.now()
                if letzter_block_startzeit != 0:
                    dauer_letzter_block = block_startzeit - letzter_block_startzeit
                    print("Bearbeitungszeit letzter Block = " + str(dauer_letzter_block))
                    gescheatzte_bearbeitungszeit = (anzahlBloecke - i) * dauer_letzter_block
                    print("Geschätzte Zeit bis zum Abschluss der Bearbeitung = " + str(gescheatzte_bearbeitungszeit))
                if i == 2:
                    gesamte_bearbeitungszeit = dauer_letzter_block
                    print("Bisherige Gesamtbearbeitungszeit = " + str(gesamte_bearbeitungszeit))
                if i > 2:
                    gesamte_bearbeitungszeit += dauer_letzter_block
                    print("Bisherige Gesamtbearbeitungszeit = " + str(gesamte_bearbeitungszeit))
                letzter_block_startzeit = datetime.now()
                neuesDict = {}
                neuesDict = patentdatenDict
                neuesDict = utility_NLP_Bearbeitung.nlpPipelineDurchlaufen(patentdatenDict, config.spacyModel)

                for key in neuesDict:
                    docText = {
                        "publication_number": key,
                        "title": neuesDict[key]['title'],
                        "abstract": neuesDict[key]['abstract'],
                        "claims": neuesDict[key]['claims'],
                        "description": neuesDict[key]['description'],
                        "assignee": neuesDict[key]['assignee1']
                    }
                    utility_Index_und_Suche.dokumentIndexieren(esClient, config.indexFulltext, docText)

                    if config.enablePayload == True:
                        # Hinzufügen der POS Tags nach jedem Wort als Payload für jeden Eintrag im Dict
                        docText = {
                            "publication_number": key,
                            "title": utility_NLP_Bearbeitung.posPayloadEinfuegen(neuesDict[key]['title'], config.enableLemma,
                                                                                 nlp),
                            "abstract": utility_NLP_Bearbeitung.posPayloadEinfuegen(neuesDict[key]['abstract'],
                                                                                    config.enableLemma, nlp),
                            "claims": utility_NLP_Bearbeitung.posPayloadEinfuegen(neuesDict[key]['claims'], config.enableLemma,
                                                                                  nlp),
                            "description": utility_NLP_Bearbeitung.posPayloadEinfuegen(neuesDict[key]['description'],
                                                                                       config.enableLemma, nlp),
                            "assignee": neuesDict[key]['assignee1']
                        }
                        utility_Index_und_Suche.dokumentIndexieren(esClient, config.indexFulltextPOS, docText)

                    # Ablage jedes Satzes, jedes Dokumentes in einem Indexeintrag zusammen mit dem Feld der Patentnummer
                    saetze = list(neuesDict[key]['NLP_doc'].sents)
                    for satz in saetze:
                        satz_ = str(satz)
                        utility_Index_und_Suche.dokumentIndexieren(esClient, config.indexSentence,
                                                                   {"publication_number": key, "satz": satz_})
                        if config.enablePayload:
                            satz_ = utility_NLP_Bearbeitung.posPayloadEinfuegen(str(satz), config.enableLemma, nlp)
                            utility_Index_und_Suche.dokumentIndexieren(esClient, config.indexSentencePOS,
                                                                       {"publication_number": key, "satz": satz_})

                del (neuesDict)
                i += 1



        if config.multiprocess_indexing == False:
            index_documents(patentdatenDict)
        else:
            dictListe = utility_Datenbearbeitung.split_dictionary(patentdatenDict, config.anzahlDokumenteInBlock)
            pool = multiprocessing.Pool()  # Erzeugen eines Prozesspools
            #results = pool.map(index_dict_parts, dictListe)  # Parallele Ausführung
            # Parallee Ausführung und Darstllung eines Statusbalkens
            results = []
            with tqdm(total=len(dictListe)) as progress_bar:
                for result in pool.imap(index_dict_parts, dictListe):
                    results.append(result)
                    progress_bar.update(1)
            pool.close()
            pool.join()



    if modus == 1:
        utility_Index_und_Suche.refresh(esClient, config.indexFulltext)
        utility_Index_und_Suche.refresh(esClient, config.indexFulltextPOS)
        utility_Index_und_Suche.refresh(esClient, config.indexSentence)
        utility_Index_und_Suche.refresh(esClient, config.indexSentencePOS)


    if modus == 2:
        patentdatenDict = utility_Datenbearbeitung.jsonDateienEinlesen(config.pfadDateneingabe)

        print("\n", '########## Speicherung des Wörterbuchs der Metadaten ##########')
        print("Speicherung des Wörterbuchs mit den Metadaten der eingelesenen Patente im Pfad " + str(config.pfadDatenausgabe))
        patentdatenDict_META = copy.deepcopy(patentdatenDict)
        for eintrag in patentdatenDict_META:
            del patentdatenDict_META[eintrag]["abstract"]
            del patentdatenDict_META[eintrag]["claims"]
            del patentdatenDict_META[eintrag]["description"]
        print(utility_Datenbearbeitung.speichereObjekt(patentdatenDict_META, config.pfadDatenausgabe, config.bezeichnungWoerterbuch))
        if config.save_Metadatafile:
            columnnames = patentdatenDict_META.keys()
            with open(config.name_Metadatafile, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=columnnames)
                writer.writeheader()
                writer.writerow(patentdatenDict_META)

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

        utility_Index_und_Suche.dokumentIndexieren(esClient,"indexfulltexttest",doc1)
        utility_Index_und_Suche.dokumentIndexieren(esClient, "indexfulltexttest", doc2)
        utility_Index_und_Suche.refresh(esClient, config.indexFulltext)
        #print(elasticsearch.getDocument(esIndex,esClient,"V0IblIQBXLfNnWU7TaQ0"))

        # query = {
        #     "match": {
        #         "description": "Schreibtisch"
        #     }
        # }

        query = {
            "match_all": "Schreibtisch"
            }


        response=utility_Index_und_Suche.search(esClient,config.indexFulltext,query)

    zeitpunktEnde = datetime.now()
    print("\n", "Dauer der Bearbeitung = ", zeitpunktEnde - zeitpunktStart)
    #todo: OPTIMIERUNG: Visualisierung -  Einen Prograss-Bar z.B. mit tqdm einfügen