# Das verwendete Multithreading Package akzeptiert nur Funktionen über die mehrere Threads eröffnetwerden,
# die in einzelnen Dateien liegen, daher wurde diese Funktion aus der Datenvorbereitung.py ausgegliedert
import spacy
import utility_Index_und_Suche
import utility_NLP_Bearbeitung
import config


nlp = spacy.load(config.spacyModel)
esClient = utility_Index_und_Suche.clientStarten(config.esPort)

def index_dict_parts(patentDict):
	neuesDict = utility_NLP_Bearbeitung.nlpPipelineDurchlaufen(patentDict, config.spacyModel)

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