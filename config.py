import os

# ALLGEMEIN
pfadCPCDict = os.path.join(os.getcwd(), "model_data", "CPCDict.pkl")      #Pfad zur Datei mit dem Wörterbuch der CPC-Beschreibungen
pfadDateneingabe = os.path.join(os.getcwd(), "input") #Verzeichnis in dem .json Patentdaten gesucht und verarbeitet werden sollen
pfadDateneingabe = os.path.join(os.getcwd(), "model_data") #Verzeichnis in dem .json Patentdaten gesucht und verarbeitet werden sollen
DateinameFasttextModel = "patent-100.bin" #Dateiname des vewendeten Fasttext Models. nur .bin Datei. .vec ist menschenlesbar, aber redundant und wird ignoriert
pfadFasttextModel = os.path.join(os.getcwd(), "model_data", DateinameFasttextModel)
#pfadPatentWoerterbuch = os.path.join(os.getcwd(), "model_data", "dict_metadata_random_full.pkl") #Pfad zur Datei des in der Datenvorbereitung erzeugten Wörterbuches der Metadaten der eingelesenen Patente
#pfadPatentWoerterbuch = os.path.join(os.getcwd(), "model_data", "woerterbuch_metadaten_G01L_100.pkl")
pfadPatentWoerterbuch = os.path.join(os.getcwd(), "model_data", "woerterbuch_metadaten_G01L.pkl")
jobim_API_URL = 'http://ltmaggie.informatik.uni-hamburg.de/jobimviz/ws' #API für das Jobim Model, Standard ist die Demo der Uni HH
ListeQueryOperatoren =["and", "or", "not"]
esPort = 9200 #Port des Elasticsearch Servers
listOfSearchfield = ("title", "abstract", "claims", "description")
# Anlegen der internen Indexbezeichnungen / muss identisch sein zu den Bezeichnungen beim Anlegen in Datenvorbereitung.py
#indexFulltext = "fulltext"
#indexFulltextPOS = "fulltext_payload"
#indexSentence = "sentence"
#indexSentencePOS = "sentence_payload"
#indexFulltext = "fulltext_random_full"
#indexFulltextPOS = "fulltext_payload_random_full"
#indexSentence = "sentence_random_full"
#indexSentencePOS = "sentence_payload_random_full"
# indexFulltext = "fulltext"
# indexFulltextPOS = "fulltext_payload"
# indexSentence = "sentence_random"
# indexSentencePOS = "sentence_payload"
#indexFulltext = "fulltext_g01l_manual"
#indexFulltextPOS = "fulltext_payload_g01l_manual"
#indexSentence = "sentence_g01l_manual"
#indexSentencePOS = "sentence_payload_g01l_manual"
indexFulltext = "fulltext_g01l"
indexFulltextPOS = "fulltext_payload_g01l"
indexSentence = "sentence_g01l"
indexSentencePOS = "sentence_payload_g01l"
html_baselink_for_patents = "https://worldwide.espacenet.com/patent/search?q=pn%3D" #to be added with the Patentnumber, without "-", e.g. 'US-9614992-B2' => 'https://worldwide.espacenet.com/patent/search?q=pn%3DUS9614992B2'


# DATENVORBEREITUNG
anzahlDokumenteInBlock = 1 #Anzahl an Dokumenten je Bearbeitungsblock
enablePayload = True  #True: Es wird die Wortart als Payload hinzugeführt; Bsp. "Coded|ADJ spectral|ADJ imager|NOUN"
enableLemma = False    #True: Lemmatisiert alle Ausdrücke und Worte
indexLoeschen = True #True: Löscht den bestehenden Index und leg einen leeren neuen Index an, z.B. zu Testzwecken
spacyModel = "en_core_web_sm" #Legt das zu angewendete, vortrainierte Model fest. Zur Entwicklung
                # Zur Entwicklung verwendet "en_core_web_sm"; zum produktiven Bearbeiten ggf. Wechsel auf "en_core_web_lg"
                # Weitere Informationen https://spacy.io/models/
bezeichnungWoerterbuch ="woerterbuch_metadaten_G01L_100.pkl" #Dateiname der Wörterbuchdatei (im Wörterbuch sind zu den Patennnummern weiter Felder mit Informationen zum Patent abgelegt
multiprocess_indexing = True #Verwendung von Multithreading
save_Metadatafile = False #In Modus 2, a CVS-file with the Metadata is saved. Can be used to asses the indexed Dokument manually for a calculation of performance parameter
name_Metadatafile = "metadata.csv"

