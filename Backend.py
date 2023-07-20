import config
import itertools
from nltk.corpus import wordnet as wn
from jobimtextapi.jobimtext import JoBimText
import gensim
from gensim.models.fasttext import FastText
import pandas as pd
import pickle
import utility_Index_und_Suche
import re


def dictPatentdaten_einlesen():
    file = open(config.pfadPatentWoerterbuch, 'rb')
    woerterbuch = pickle.load(file)
    file.close()
    return woerterbuch


def dictCPC_einlesen():
    file = open(config.pfadCPCDict, 'rb')
    woerterbuch = pickle.load(file)
    file.close()
    return woerterbuch


def getCPC(_cpc):
    return (CPCdict[_cpc])


def serverstatus_abfragen(_esClient):
    if _esClient.ping == True:
        return True
    else:
        return False


def startFastText():
    print("FastText Modell wird geladen")
    print(config.pfadFasttextModel)
    loaded_HPI_FastText = gensim.models.fasttext.load_facebook_vectors(config.pfadFasttextModel)
    if loaded_HPI_FastText != None:
        print("FastText Modell geladen")
    return loaded_HPI_FastText


def startElasticsearchClient():
    esClient = utility_Index_und_Suche.clientStarten(config.esPort)
    esClient.ping
    return esClient


def queryExpansion_Fastext(wort, fastTextModel, anzahl = 10):
    fasttext = fastTextModel.most_similar(positive=[wort], topn=anzahl)
    fasttext_switch =[]
    for i in fasttext:
        fasttext_switch.append([i[1], i[0]])
    return fasttext_switch


def queryExpansion_JoBim(wort, anzahl, pos_tag=None):
    #Modelunterscheidung nach Anfrage mit oder ohne POS-Tag. Es können nicht alle Modelle POS-Tag verarbeiten. Wenn sie es können, muss ein Tag angegeben werden
    if pos_tag != None:
        pos_tag = pos_tag.upper()
    if pos_tag not in ["VERB", "NOUN", "ADJ", "ADV", None]:
        print("FEHLER: Der übergebenen POS-Tag " + str(pos_tag) + "kann in Jobim nicht verarbeitet werden. Der Tag wird ignoriert.")
        pos_tag = None
    if pos_tag == "VERB":
        pos_tag="VB"
    elif pos_tag == "NOUN":
        pos_tag = "NN"
    elif pos_tag == "ADJ":
        pos_tag = "JJ"
    elif pos_tag == "ADV":
        pos_tag = "RB"

    if pos_tag == None:
        holingtype = "trigram"
    else:
        holingtype = "stanford"

    jbAPI = JoBimText(api_url=config.jobim_API_URL)
    similar = jbAPI.similar(wort, pos = pos_tag, url_params={}, holingtype=holingtype)

    if similar.error != None:
        print(similar.error)
        return "FEHLER IN JOBIM QUERY EXPANSION!"

    rueckgabe = []
    if similar.results.__len__() >= anzahl:
        for i in range(anzahl):
            rueckgabe.append([similar.results[i].score, similar.results[i].term])
        else:
            for i in range(similar.results.__len__()):
                rueckgabe.append([similar.results[i].score, similar.results[i].term])

    return rueckgabe


def queryExpansion_Wordnet(wort, anzahl=10, pos_tag=None):

    #Wordnet kann nur mit diesen vier Wortarten umgehen. Ignoriern, wenn ein anderer POS-Tag übergeben wird
    if pos_tag not in ["VERB", "NOUN", "ADJ", "ADV", None]:
        print("FEHLER: Der übergebenen POS-Tag " + str(pos_tag) + "kann in Wordnet nicht verarbeitet werden. Der Tag wird ignoriert.")
        pos_tag = None
    if pos_tag == "VERB":
        pos_tag=wn.VERB
    elif pos_tag == "NOUN":
        pos_tag = wn.NOUN
    elif pos_tag == "ADJ":
        pos_tag = wn.ADJ
    elif pos_tag == "ADV":
        pos_tag = wn.ADV

    #Abfrage der Sysets zum übergebenen Wort
    s = wn.synsets(wort, pos=pos_tag)
    if s.__len__()==0:
        return []

    #Berechnung des Abstandes zum ersten Synset. Listung der Namen aller Eintrag in je Synset mit ihrem jeweiligen Abstand.
    #Entfernung von Doublette und Sortierung nach dem Abstand
    erstesSet = s[0]
    liste = []
    lemmaList = []
    for set in s:
        abstand = erstesSet.path_similarity(set)
        for eintrag in set.lemma_names():
            if eintrag not in lemmaList:
                lemmaList.append(eintrag)
                liste.append([abstand, eintrag])
    liste.sort(reverse=True)

    #Begrenzung auf die Anzahl der angeforderten Worte
    if anzahl < liste.__len__():
        rueckgabe = []
        for i in range(anzahl):
            rueckgabe.append(liste[i])
        return rueckgabe
    else:
        return liste


def getOberbegriff_WordNet(wort, anzahl=1, pos_tag=None):
    #Suche nach Oberbegriffen (Hyperonym)
    #Auflösung der POS-Tags
    if pos_tag not in ["VERB", "NOUN", "ADJ", "ADV", None]:
        print("FEHLER: Der übergebenen POS-Tag " + str(pos_tag) + "kann in Wordnet nicht verarbeitet werden. Der Tag wird ignoriert.")
        pos_tag = None
    if pos_tag == "VERB":
        pos_tag=wn.VERB
    elif pos_tag == "NOUN":
        pos_tag = wn.NOUN
    elif pos_tag == "ADJ":
        pos_tag = wn.ADJ
    elif pos_tag == "ADV":
        pos_tag = wn.ADV

    #Synset zum Wort finden
    s = wn.synsets(wort)
    if s.__len__() == 0:
        return []

    #Suche und RÜckgabe der/des Oberbegriffes für das erste Synset
    rueckgabe = []
    erstesSet = s[0]
    obergegriff = erstesSet.hypernyms()
    for eintrag in obergegriff:
        rueckgabe.append(eintrag.lemma_names()[0])
    if rueckgabe.__len__() < anzahl:
        anzahl = rueckgabe.__len__()
    return rueckgabe[:anzahl]


def getUnterbegriff_WordNet(wort, anzahl=1, pos_tag=None):
    #Suche nach Unterbegriffen (Hyponym)
    #Auflösung der POS-Tags
    if pos_tag not in ["VERB", "NOUN", "ADJ", "ADV", None]:
        print("FEHLER: Der übergebenen POS-Tag " + str(pos_tag) + "kann in Wordnet nicht verarbeitet werden. Der Tag wird ignoriert.")
        pos_tag = None
    if pos_tag == "VERB":
        pos_tag=wn.VERB
    elif pos_tag == "NOUN":
        pos_tag = wn.NOUN
    elif pos_tag == "ADJ":
        pos_tag = wn.ADJ
    elif pos_tag == "ADV":
        pos_tag = wn.ADV

    #Synset zum Wort finden
    s = wn.synsets(wort)
    if s.__len__() == 0:
        return []

    #Suche und RÜckgabe der/des Unterbegriffe für das erste Synset
    rueckgabe = []
    rueckgabeLemma = []
    erstesSet = s[0]
    unterbegriff = erstesSet.hyponyms()
    for eintrag in unterbegriff:
        rueckgabe.append(eintrag.lemma_names()[0]) #es wird wieder nur der erst Eintrag verfolgt, auch wenn das Synset mehrere passende Begriffe hat, da diese synomym sind
    if rueckgabe.__len__() < anzahl:
        anzahl = rueckgabe.__len__()
    return rueckgabe [:anzahl]


def expandWord(word, termNumber,posTag=None, wordnet=True, jobimText=True, hpiFastText=True, fastextModel=None, return_rank=False):
    #Erweitert das übergeben Wort in den auf True übergeben QE-Modellen.
    #Anzahl der erweiterten Terme wird in alle Modelle übernommen
    #Die Zusammenführung erfolgt über den Rang in der Listen der einzelnen Modelle

    wordlists = {}
    returnlist = []

    if wordnet:
        wordlists["wordnet"] = queryExpansion_Wordnet(word, termNumber, posTag)
    if jobimText:
        wordlists["jobim"] = queryExpansion_JoBim(word, termNumber, posTag)
    if hpiFastText:
        wordlists["hpiFastText"] = queryExpansion_Fastext(word, fastextModel, termNumber)

    # Erstellung des Startwertes des Randscores; max Anzahl an Termen in der längsten Liste.
    start_score = 0
    for liste in wordlists:
        if wordlists[liste].__len__() > start_score:
            start_score = wordlists[liste].__len__()

    for list in wordlists:
        rankScore = start_score #Startwert des Rankscores auf dem ersten Rank, wird mit jedem weiteren Rank um 1 reduziert
        for element in wordlists[list]:
            if element[1] != word:
                doublicat=False
                for elementReturnlist in returnlist:    #Prüfung, das jeweilige Element bereits vorhanden ist (aus einem anderen QE-Modell und addiert ggf. den Score)
                    if element[1] == elementReturnlist[1]:
                        elementReturnlist[0] += rankScore
                        doublicat = True
                if doublicat == False:          #Hinzufügen des Elementes zur Rückgabe liste inkl. Rankscore, falls es noch in der Liste vorhanden war
                    returnlist.append([rankScore, element[1]])
                rankScore -= 1
    returnlist.sort(reverse=True)
    #Übergibt die Liste inklusive des Ranges oder entfernt den Rang vor der Rückgabe
    if return_rank:
        return returnlist[:termNumber]
    else:
        liste = []
        for j in returnlist:
            liste.append(j[1])
            #del j[0]
        return liste[:termNumber]


def queryString_to_dict(query_string):
#    Parses a search query string and returns a dictionary with each term
#    of the string connected with its search operators.

    query_dict = {}

    # Split the query string by whitespace and double quotes
    #term_list = re.findall(r'(?:".*?"|\S+)', query_string)
    #term_list = re.findall(r'(?:".*?"|\S+(?=\s|$))', query_string)
    term_list = re.findall(r'(?:\+?"[^"]*"|\S+)', query_string)
    print(term_list)

    i = 0
    while i < len(term_list):
        term = term_list[i]
        operator = "+"
        pos_tag = None
        proximity = None

        if term.startswith("+"):
            operator = "+"
            term = term[1:]
        elif term.startswith("-"):
            operator = "-"
            term = term[1:]

        if "#" in term:
            term_parts = term.split("#")
            term = term_parts[0]
            pos_tag = term_parts[1]

        if i + 1 < len(term_list) and term_list[i + 1].startswith("~"):
            # Combine current term and proximity operator with next term
            proximity = int(term_list[i + 1][1:])
            term = term + term_list[i + 1]
            i += 1

        # Remove the ~ form the term
        index = term.rfind("~")  # Finden des Indexes der letzten Tilde
        if index != -1:  # Wenn eine Tilde gefunden wurde
            term = term[:index]  # Extrahieren des Textes links von der Tilde

        if term != "":
            query_dict[term] = {"operator": operator, "pos_tag": pos_tag, "proximity": proximity}

        i += 1

    return query_dict


def queryString_to_dict_old(query_string):
    #Parses a search query string and returns a dictionary with each term of the string connected with its search operators.

    query_dict = {}

    # Split the query string by whitespace and double quotes
    term_list = re.findall(r'(?:".*?"|\S+)', query_string)

    for term in term_list:
        operator = ("+")
        pos_tag = None

        if term.startswith("+"):
            operator = "+"
            term = term[1:]
        elif term.startswith("-"):
            operator = "-"
            term = term[1:]

        if "#" in term:
            term_parts = term.split("#")
            term = term_parts[0]
            pos_tag = term_parts[1]

        # Remove double quotes from multi-word terms
        if term.startswith('"') and term.endswith('"'):
            term = term[1:-1]

        query_dict[term] = {"operator": operator, "pos_tag": pos_tag}

    return query_dict


def dict_to_queryString(query_dict):
#    Generates a search query string from a dictionary with each term of
#    the string connected with its search operators.

    query_list = []

    for term, values in query_dict.items():
        operator = values["operator"]
        pos_tag = values["pos_tag"]
        proximity = values["proximity"]
        term_str = term

        if operator:
            term_str = operator + term_str

        if pos_tag:
            term_str += "#" + pos_tag

        if proximity:
            term_str += "~" + str(proximity)

        query_list.append(term_str)

    return " ".join(query_list)


def splitQuery(query, returnPOS=True):
    #Splits the query in terms and POS-Tags; returns a list with terms and tags as pairs

    query = query.lower()
    query = query.replace("(", "")
    query = query.replace(")", "")
    liste = query.rsplit()
    for operator in config.ListeQueryOperatoren:
        if liste.__contains__(operator):
            liste.remove(operator)
    liste2 = []
    if returnPOS == False:
        for i in liste:
            temp = i.rsplit(sep="#")
            liste2.append(temp[0])
        return liste2
    for i in liste:
        liste2.append(i.rsplit(sep="#"))

    #add None as POS-Tag, if the item has no tag attached to it and make the POS-Tag Upper-Case for further processing
    for i in liste2:
        if i.__len__() == 1:
            i.append(None)
        else:
            i[1]=i[1].upper()
    return liste2


def expandQuery(Query, termNumber, wordnet, jobim, hpiFastText, _hpifastextmodel=None):
    #Expands the term in the Query-String by splitting the query and searching the Query-Expansion models give as true
    #Returns a Dataframe
    if hpiFastText==False:
        hpiFastTextModel = None
    terms = splitQuery(Query)
    dataframe = pd.DataFrame()
    for term in terms:
        wordlist = expandWord(term[0],termNumber,term[1], wordnet, jobim, hpiFastText, _hpifastextmodel)
        if wordlist.__len__() < termNumber:
            for i in range(termNumber-wordlist.__len__()):
                wordlist.append([0,0])
        for j in wordlist:
            del j[0]
        dataframe[term[0]] = wordlist
    return dataframe


def useCaseSearch(searchString, query_dict, search_type):
# Carries out a search accronding to the searchString. The results are analysed and stored orderd by quantiy in dataframes.
# The desciption of CPC classes is added

    esclient = startElasticsearchClient()

    # Set the search index based on pos_tag
    if search_type == "Document search":
        search_index = config.indexFulltext
    if search_type == "Document search" and any(term.get("pos_tag") for term in query_dict.values()):
        search_index = config.indexFulltextPOS
    if search_type == "Sentence search":
        search_index = config.indexSentence
    if search_type == "Sentence search" and any(term.get("pos_tag") for term in query_dict.values()):
        search_index = config.indexSentencePOS

    # Create and execute the query
    query = \
        {"query_string":
            {
            "query": searchString,
            "analyze_wildcard": True,
            "default_operator": "AND"
            #"fields": listOfSearchfield
            }
        }

    results = utility_Index_und_Suche.search(esclient, search_index, query)


    # Analyze and store the results in two dictionaries. One for the CPC-Classes and one for Assignees.
    CPC_Subclass_analysis_dict = {}
    CPC_Maingroup_analysis_dict ={}
    Assignee_analysis_dict={}
    CPCdict = dictCPC_einlesen()
    patentdict = dictPatentdaten_einlesen()

    for result in results:
        # Extraction of the needed informations for the statistical analysis of the search results for each document in the set of results
        publication_number = result["_source"]["publication_number"]
        CPC_No = patentdict[publication_number]["cpc"]
        CPC_parts = CPC_No.split("/")
        CPC_Maingroup_No = CPC_parts[0] + "/00"
        CPC_Subclass_No = CPC_No[:4]
        Assignee = patentdict[publication_number]["assignee1"]


        # To enrich the results, the CPC descriptions are fetched
        if CPC_Subclass_No in CPCdict:
            CPC_Subclass_description = CPCdict[CPC_Subclass_No]
        else:
            CPC_Subclass_description = {"No desciption available in Database"}

        if CPC_Maingroup_No in CPCdict:
            CPC_Maingroup_description = CPCdict[CPC_Maingroup_No]
        else:
            CPC_Maingroup_description = {"No desciption available in Database"}

        # Counting of the quantity of the results
        if CPC_Subclass_No in CPC_Subclass_analysis_dict:
            CPC_Subclass_analysis_dict[CPC_Subclass_No]["Quantity"] += 1
        else:
            CPC_Subclass_analysis_dict[CPC_Subclass_No] = {"Quantity": 1, "Description": CPC_Subclass_description}

        if CPC_Maingroup_No in CPC_Maingroup_analysis_dict:
            CPC_Maingroup_analysis_dict[CPC_Maingroup_No]["Quantity"] += 1
        else:
            CPC_Maingroup_analysis_dict[CPC_Maingroup_No] = {"Quantity": 1, "Description": CPC_Maingroup_description}

        if Assignee in Assignee_analysis_dict:
            Assignee_analysis_dict[Assignee]["Quantity"] += 1
        else:
            Assignee_analysis_dict[Assignee] = {"Quantity" : 1}

    #Store the results in Pandas Dataframes, sort each dataframe by quantity and return the Dataframes
    if results.__len__() == 0: # Catch of searches without results
        dataframe_CPC_Subclass = {"No results"}
        dataframe_CPC_Maingroup = {"No results"}
        dataframe_Assignee = {"No results"}
    else:
        dataframe_CPC_Subclass = pd.DataFrame(CPC_Subclass_analysis_dict).transpose().sort_values(by="Quantity", ascending=False)
        dataframe_CPC_Maingroup = pd.DataFrame(CPC_Maingroup_analysis_dict).transpose().sort_values(by="Quantity", ascending=False)
        dataframe_Assignee = pd.DataFrame(Assignee_analysis_dict).transpose().sort_values(by="Quantity", ascending=False)
    return dataframe_CPC_Subclass, dataframe_CPC_Maingroup, dataframe_Assignee


def overlap_search(query_dict, search_type, results_to_display):
#    Carries out an overlap search using the query dictionary obtained from the
#    queryString_to_dict() function.

    # Start of the ElasticSearch Client & Patent Dictionary
    esclient = startElasticsearchClient()
    patentdict = dictPatentdaten_einlesen()

   # Correction of the proximity when search in done in an index with these tag. As the tags are interpreted as word, the proximity has to be increased accordingly (P = 2*P+1)
    for term in query_dict:
        if query_dict[term]["proximity"] != None:
            query_dict[term]["proximity"] = query_dict[term]["proximity"]* 2 + 1

    # Create a list of queries, start with the original query
    queries_list = []
    queries_list.append(dict_to_queryString(query_dict))

    # Adds the single terms including POS-Tags and Operators and Proximity to either a list of excluded or included terms
    dict_list = []  # Liste, die die getrennten Dictionaries enthalten wird
    for key, value in query_dict.items():
        new_dict = {key: value}  # Erstellt ein neues Dictionary mit einem Schlüssel-Wert-Paar
        dict_list.append(new_dict)  # Fügt das neue Dictionary der Liste hinzu
    included_terms = []
    excluded_terms = []
    for dict in dict_list:
        for queryString in dict:
            if dict[queryString]["operator"] == "+":
                included_terms.append(dict_to_queryString(dict))
            if dict[queryString]["operator"] == "-":
                excluded_terms.append(dict_to_queryString(dict))
    # Creats all combinations of all numbers form N to 1 of the search terms with operator "+" and adds the terms with operator "-" to the end
    for i in range(len(included_terms) - 1, 0, -1):
        for combination in itertools.combinations(included_terms, i):
            a = (str(combination), " " + str(excluded_terms)) #is a tuple
            a_str = "".join(a) #is a string with charaters of the list like , ( )
            chars_to_remove = "',()[]"
            translator = str.maketrans('', '', chars_to_remove)
            a_str_cleaned = a_str.translate(translator) # remove the unwanded characters in the string
            queries_list.append(a_str_cleaned)

    # Generation of the query format and call of the search
    # storing the results in the results_dict
    results_dict = {}
    for queryString in queries_list:

        # Set the search index based on pos_tag
        if search_type == "Document search":
            search_index = config.indexFulltext
        if search_type == "Document search" and "#" in queryString:
            search_index = config.indexFulltextPOS
        if search_type == "Sentence search":
            search_index = config.indexSentence
        if search_type == "Sentence search" and "#" in queryString:
            search_index = config.indexSentencePOS

        queryString = queryString.replace("#","¶") #replace the POS separator

        query = \
            {"query_string":
                {
                    "query": queryString,
                    "analyze_wildcard": True,
                    "default_operator": "AND"
                    # "fields": listOfSearchfield
                }
            }

        result = utility_Index_und_Suche.search(esclient, search_index, query)
        if result != []:
            #foundTerms =  [word[1:] for word  in queryString.split() if word.startswith("+")] # Extracts the term with "+" form the query
            foundTerms = re.findall(r'\+("[^"]*"|\w+)', queryString)  # Extracts the term with "+" form the query
            publicationNumbers = []
            for entry in result:
                publicationNumbers.append(entry["_source"]["publication_number"])
            results_dict[queryString] = {
                "Found Terms": foundTerms,
                "Number of Terms" : foundTerms.__len__(),
                "Publication Numbers": publicationNumbers,
                "Number of Publications": publicationNumbers.__len__()
            }

    # create the list of included terms without search operators
    for i in range(len(included_terms)):
        if included_terms[i].startswith("+"):
            included_terms[i] = included_terms[i][1:]

    #create DICT OF DETAILS
    sorted_results = sorted(results_dict.items(), key=lambda x: x[1]['Number of Terms'], reverse=True) #list of results, sorted by the number of term found
    sorted_results = sorted_results[:results_to_display] #reducte the list to the number of elements to display
    details_dict_list = []
    for i in range(min(results_to_display, sorted_results.__len__())):
        temp_dict_list = []
        for publication in sorted_results[i][1]["Publication Numbers"]:
            temp_dict ={}
            temp_dict[publication] = {
                "Title": patentdict[publication]["title"],
                "Assignee": patentdict[publication]["assignee1"],
                "Publication Date": patentdict[publication]["publication_date"],
                "Link": config.html_baselink_for_patents + publication.replace("-","")
            }
            temp_dict_list.append(temp_dict)

        # in sentence search a patent can be found multiple times, therefor it must not be added if allready in the list
        unique_temp_dict_list = []
        for element in temp_dict_list:
            if element not in unique_temp_dict_list:
                unique_temp_dict_list.append(element)

        details_dict_list.append(unique_temp_dict_list)

    #create DICT OF RESULTS
    overlap_results_dict = {}
    i = 0
    if sorted_results.__len__() > 0:
        for entry in sorted_results:
            second_row = []
            caption_terms = included_terms.copy()
            caption_terms_noPOS = []
            for term_ in caption_terms:
                if "#" in term_:
                    caption_terms_noPOS.append(term_.split("#")[0])
                else:
                    caption_terms_noPOS.append(term_)



            for term in caption_terms_noPOS:
                if term in sorted_results[i][1]["Found Terms"]:
                    second_row.append("Y")
                else:
                    second_row.append("N")

            second_row.append(sorted_results[i][1]["Number of Terms"])
            #second_row.append(sorted_results[i][1]["Number of Publications"])
            second_row.append(details_dict_list[i].__len__()) #Number of Publication after the reduction to unique entries
            caption_terms.append("No. of TERMS")
            caption_terms.append("No. of PATENTS")

            overlap_results_dict[i] = {
                "overview": {
                    "=>": caption_terms,
                    " ": second_row
                },
                "details": details_dict_list[i]
                }
            i += 1

    #return caption, body_string_list, details_dict_list
    return overlap_results_dict


if __name__ == "__main__":
    pass
    #TESTEINGABEN
    #model = startFastText()
    #ab = expandWord("sensor", 10, None, True, True, False, None)
    #oberbegriff = getOberbegriff_WordNet("car", 1, None)
    #unterbegriff = getUnterbegriff_WordNet("car", 10, None)
    #erweitert_wort = expandWord("car", 10,None, True, True, False, None)

    #print(queryExpansion_Wordnet("trailer"))
    #print(getOberbegriff_WordNet("brake", 10))
    #print(getUnterbegriff_WordNet("cab", 10))
    #print(queryExpansion_JoBim("brake",10,"VB"))
    #print((queryExpansion_JoBim("car",10,"NOUN")))
    #fastTextModel = startFastText()
    #print(queryExpansion_Fastext("car",fastTextModel ,5))
    # print(expandWord("car", 10, None, True, True, False))
    # print(expandWord("car", 1, None, True, True, False))
    # print(expandWord("car", 100, None, True, True, False))
    # fastTextModel = serverStarten()
    # print(expandWord("car", 10, None, True, True, True,fastTextModel))
    # print(expandWord("car", 1, None, True, True, True, fastTextModel))
    # print(expandWord("car", 100, None, True, True, True, fastTextModel))
    # print(expandWord("jeep", 10, None, True, True, True, fastTextModel))
    # print(expandWord("asdf", 10, None, True, True, True, fastTextModel))
    # print(expandWord("asdf", 10, None, True, True, False))
    #print(splitQuery("brake#NOUN AND (tractor OR trailer) NOT car",False))
    #print(splitQuery("brake#NOUN AND (tractor OR trailer) (NOT car)"))
    #test = expandQuery("brake#NOUN AND (tractor OR trailer) NOT car",10,True,False, False)

    #esclient = startElasticsearchClient()
    #utility_Index_und_Suche.refresh(esclient, indexFulltext)

    #BEISPIEL FULLTEXT
    # query = {"multi_match":{
    #     "query": "waveband",
    #     "fields": listOfSearchfield,
    #     "operator": "or"
    #     }
    # }
    #Der Operator bezieht sich auf die Suchbegriffe. "and" und "or" sind zulässig.
    #a= utility_Index_und_Suche.search(esclient, indexFulltext, query)
    #print (a[0]["_source"])


    # #BEISPIEL PHRASE
    # query = {"match_phrase":{
    #     "message": "Coded spectral imager"
    #     }
    # }

    #BEISPIEL FULLTEXT MIT OPERATOREN UND PHRASE
    #query = {"query_string":{
    #    #"query": "clean* OR separat* AND brush* AND “motion controlled”",
    #    "query": "infusion",
    #    "fields": config.listOfSearchfield
    #    }
    #}
    #b= utility_Index_und_Suche.search(esclient, config.indexFulltext, query)
    #print (b[0]["_source"])


    #BEISPIEL SUCHE INNERHALB EINES SATZES
    #query = {"query_string":{
    #    #"query": "filter AND spectral AND wavebands AND multiple and processor AND configured AND to AND generate",
    #    "query": "filter spectral wavebands multiple processor configured to generate",
    #    "default_operator": "AND"
    #    }
    #}
    #alle Terme müssen mit AND verknüft sein, da sonst auch einzelne Funde in einem Satz zurückgegeben werden
    #c= utility_Index_und_Suche.search(esclient, indexSentence, query)
    #print (a[0]["_source"])

    #BEISPIEL VOLLTEXTSUCHE MIT EINGRENZUNG DER WORTART
    #query = {"query_string":
    #        {
    #        "query": ' "includes¶VERB" bra* "the system"~5 NOT wise ',
    #        "analyze_wildcard": True,
    #        "default_operator": "AND",
    #        "fields": listOfSearchfield
    #        }
    #    }
    #Die Hochkommas um die Wort/POS-Komibination müssen vorhanden sein, um nach der fixen Phase zu suchen
#    d= utility_Index_und_Suche.search(esclient, indexFulltextPOS, query)
#    treffer =  (a[0]["_source"]["publication_number"])
    #print (d)

#    patentDict = dictPatentdaten_einlesen()
#    print(patentDict[treffer])
#    print(patentDict[treffer]["title"])

    #CPCdict = dictCPC_einlesen()
    #print(getCPC("B01"))

#    useCaseSearch("the", queryString_to_dict("the"), "Document search")
    #useCaseSearch("( +image +picture +spectral +luminous +visual +optical +ocular) (-automotive) (-auto -automobile)", queryString_to_dict("( +image +picture +spectral +luminous +visual +optical +ocular) (-automotive) (-auto -automobile)"), "Document search")
    #useCaseSearch("the", queryString_to_dict("the"), "Sentence search")
    #testdict = queryString_to_dict('"fox quick"~5  brake "heavy vehicle" -test2 +tractor#noun -car -test')
    #testdict = queryString_to_dict('"zwei drei"~1 "vier fünf"~3 -car')
    #testdict = queryString_to_dict('protocol "key exchange"~5 brake#VERB "coefficient of friction"')
    #testdict = queryString_to_dict("eins zwei drei -vier")
    #test_result = overlap_search(testdict, "Document search", 10)

    # Testdaten zur Dokumentatioan in der Arbeit
    #testdict = queryString_to_dict('protocol "key exchange"~5 brake#VERB "coefficient of friction" -automotive')
    #results = overlap_search(testdict, "Document search", 10)
    #erweiterte_Worte = expandWord("protocol", 10, None, True, True, False, True)
    #print(testdict)
    #query_dict_refinded = queryString_to_dict('+measure +measures +measurement +tire +tires +pressure +pressures +"pressure level"')
    #search_Type = "Document search"
    #results_to_display = 10
    #overlap_search(query_dict_refinded, search_Type, results_to_display)