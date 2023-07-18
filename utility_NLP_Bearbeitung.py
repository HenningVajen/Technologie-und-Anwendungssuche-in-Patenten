import spacy
from spacy import displacy

#from dataclasses import dataclass
#from typing import Any

# @dataclass()
# class patendatenKlasse:
#     __slots__ = ['publication_number', 'publication_date', 'title', 'abstract', 'claims', 'description', 'cpc', 'assignee1', 'doc' ] #Optional, gibt die Struktur der Klasse vor. Reduziert den Speicherbedarf und die Zugriffzeit
#     publication_number: str
#     publication_date: int
#     title: str
#     abstract: str
#     claims: str
#     description: str
#     cpc: str
#     assignee1: str
#     doc: Any



def nlpPipelineDurchlaufen(_patentdatenObjekt, _spacyModel):
    nlp = spacy.load(_spacyModel)

    # Konfiguration der NLP Pipeline abweichend vom Standard ['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer', 'ner']
    # Tokenizer ist immer aktiviert
    # parser : depedency parsing
    # tagger : POS Tagging
    # lemmatizer : Lammatization
    #nlp.remove_pipe('tok2vec') #Darf nicht entfernt werden, wird für die Satzerkennung benötigt
    #nlp.remove_pipe('attribute_ruler') #Darf nicht entfernt werdnen, wird für die Wortartenerkennung benötigt
    nlp.remove_pipe('lemmatizer')
    #print("Anwendung dieser Bearbeitungsschritte: ", nlp.pipe_names)
    nlp.max_length = 2000000  # Max. Anzahl an Buchstaben. Standardwert=1000000. Ca. 1 GB Arbeitsspeicher pro 1000000.

    txt = ""
    i = 0
    for publication_number in _patentdatenObjekt:
        # Erstellen eines strings je Eintrag im Dictionary zur Bearbeitung
        txt = txt + _patentdatenObjekt[publication_number]["title"] + " " \
              + _patentdatenObjekt[publication_number]["abstract"] + " " \
              + _patentdatenObjekt[publication_number]["claims"] + " " \
              + _patentdatenObjekt[publication_number]["description"] + " "
        # todo OPTIMIERUNG: Speicheroptimeirung - Es werdnen immer einzelne Stirngs erzeugt. Besser die .join Methode verwenden. Kann nur auf Listen angewendet werden
        
        # Garantierung der Einhaltung des max. Anzahl an Buchstaben
        if len(txt) >= 2000000: #enforce the max. character limit of spacy by cutting the string
            txt = txt[:1999999]
        
        # NLP Bearbeitung des Strings
        doc = nlp(txt)
        saetze = list(doc.sents)
        # Hinzufügen des doc-Objektes mit den Annotierten Text an das übergebene Objekt
        _patentdatenObjekt[publication_number]["NLP_doc"] = doc
        txt = ""

        i = i + 1
        #if i % 100 == 0:
        #   print(str(i) + " von " + str(_patentdatenObjekt.__len__()) + " Dokumenten bearbeitet.")
    return _patentdatenObjekt


def objektVisualisieren(patentdatenObjekt_):
    anzahlDokumente = 2
    i=0

    # Zugriff auf Wortart
    for publicationNumber in patentdatenObjekt_:
        for token in patentdatenObjekt_[publicationNumber]["NLP_doc"]:
            print(token.text + " => LEMMA: " + token.lemma_ +  " => POS: " + token.pos_)

    # Visualisierung der Struktur
    for publicationNumber in patentdatenObjekt_:
        saetze = list(patentdatenObjekt_[publicationNumber]["NLP_doc"].sents)
        displacy.serve(saetze, style="dep", port=5001) #Der Portwechsel ist auf MacOS erforderlich, da Airplay den Standardport 5000 belegt
        i=i+1
        if (i == anzahlDokumente):
            break


def posPayloadEinfuegen(text, lemma, nlp):
    #nlp = spacy.load("en_core_web_sm")
    if len(text) >= 1000000: #enforce the max. character limit of spacy by cutting the string
        text = text[:999999]
    doc = nlp(text)
    wortliste = []
    for token in doc:
        if lemma == True:
            wortliste.append(token.lemma_ + "¶" +  token.pos_)
        else:
            wortliste.append(token.text + "¶" + token.pos_)
    text = " ".join(wortliste)
    return text