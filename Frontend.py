import time
import streamlit as st
#from st_aggrid import AgGrid
#from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from st_aggrid.shared import GridUpdateMode
import pandas as pd
#import numpy as np
from io import StringIO
import Backend
import random

#-----------------------    Attribute  -----------------------
df3 = pd.DataFrame()

#fasttextModel = None

if 'initialized' not in st.session_state:
    st.session_state.initialized = False

if 'expandQueryStart' not in st.session_state:
    st.session_state.expandQueryStart = False

if 'selectedTerms' not in st.session_state:
    st.session_state.selectedTerms = []

if 'fastTextModel_loaded' not in st.session_state:
    st.session_state.fastTextModel_loaded = False

if 'use_fileUpload' not in st.session_state:
    st.session_state.use_fileUpload = False

if 'visualisation_start' not in st.session_state:
    st.session_state.visualisation_start = False

st.session_state.visualisation_start  = False


#-----------------------    DEFINITION DER FUNKTIONEN   -----------------------
def insert_parentheses(string_original, string_expanded):
    # Initialisierung von string3 mit öffnenden Klammern
    string3 = "("
    # Splitting von string_expanded in eine Liste von Wörtern
    words = string_expanded.split()
    # Überprüfung jedes Worts auf das Vorhandensein in string_original
    i = 0
    for word in words:
        if i != 0:
            if word in string_original:
                # Einfügen von ") (" zu string3, falls das Wort in string_original vorhanden ist
                string3 += ") (" + word
            else:
                string3 += " " + word
        else:
            string3 += " " + word
        i += 1
    # Abschluss des Stings3 mit Klammer
    string3 += ")"
    return string3

def sucheStarten():
    with st.spinner('Suche im Index wird durchgeführt'):
        time.sleep(3)
    st.success('Suche abgeschlossen')


def queryExpansion():
    #st.session_state.QEDataframe = Backend.expandQuery(keywords, qeTermNumber, wordnet, jobim, fastext, fasttextModel) #creates a new sesson state variable each time the function is called. This prevents the
    # todo: FUNKTIONSERWEITERUNG - POS-Tags könnten hier nicht herausgefiltert, sondern in den späteren Abfragen zur Verbesserung der Resultate verwendet werden.
    st.session_state.initialized = True
    st.session_state.expandQueryStart = True

def startVisualisation():
    st.session_state.visualisation_start = True

def set_sessionStateQueryExpansion_to_False():
    st.session_state.expandQueryStart=False
    #When Query Expansion is used, there cannot be an uploaded file at the same time
    st.session_state.use_fileUpload=False

#Load the model into cache to speed up the searches following the first loading
@st.cache_resource
def load_fasttext(text):
    _model = Backend.startFastText()
    return _model

def selectionTable(dataToDisplay, key):
    #Creation of the selectable table; returns selectes values
    termeAuswahl = []
    gb = GridOptionsBuilder.from_dataframe(pd.DataFrame(dataToDisplay))
    #gb = GridOptionsBuilder.from_dataframe(pd.DataFrame(st.session_state.QEDataframe[queryTerm]))
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=False)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)  # Die Reihen auswählbar machen
    # gb.configure_pagination() #Buttons zum Seitenblättern unter der Tabelle
    gridOptions = gb.build()
    data = AgGrid(pd.DataFrame(dataToDisplay), #data ist der Rückgabewert der Auswahl der Tabelle
                  gridOptions=gridOptions,
                  #enable_enterprise_modules=True,
                  allow_unsafe_jscode=True,
                  key=key,
                  update_mode=GridUpdateMode.SELECTION_CHANGED)
    #Die ausgewählten Terme werden an die Auswahlliste angehangen
    for auswahl in data["selected_rows"]:
        #termeAuswahl.append(auswahl[queryTerm])
        termeAuswahl.append(auswahl)
    return termeAuswahl

#-----------------------    LAYOUT DER WEBAPPLICATION   -----------------------
st.title("Multiterm-Overlap-Search for Technologies and Use Cases in Patents")


#-----------------------    SIDEBAR   -----------------------
with st.sidebar:
    uploadFile = None
    uploadFile = st.file_uploader("Load Searchstring", type=[".txt"])
    if uploadFile != None:
        stringio = StringIO(uploadFile.getvalue().decode("utf-8"))
        string_data = stringio.read()
        st.write(string_data)
        st.session_state.initialized = True
        st.session_state.expandQueryStart = True
        st.session_state.use_fileUpload = True
        # st.write(uploadFile.getvalue())
        expandedQueryString = string_data
        queryString = string_data

    st.markdown("""---""")
    st.header("Status")
    # Pre-Load the HPI-FastText Model; needed to speed up search, as the loading can take several minutes
    # Session State will be set once upon button click. Until that the model is None and it will be skipped
    if st.session_state.fastTextModel_loaded == True:
        fasttextModel = load_fasttext("asdf")
    else:
        fasttextModel = None
    
    button_ft = st.button("FastText Model laden")
    if button_ft:
        st.session_state.fastTextModel_loaded = True
    
    if fasttextModel != None:
        st.markdown("FastText Model :green[loaded]")
    else:
        st.write("FastText Model :red[not loaded]")

#-----------------------    KEYWORD INPUT   -----------------------
st.markdown("""---""")
st.header("1) Keywords")
keywords = st.text_input("Enter Keywords describing the an application or a technology ", key="keywords", placeholder="+brake +(tractor trailer) -car")

with st.expander("Show possible search operators"):
    "Additional operators can be given:"
    st.table([("+", "term must be present (default if no operator is given)"),
              ("-", "term must not be present"),
              ("#NOUN", "term must be a noun, e.g. brake#NOUN"),
              ("#VERB", "term mus be a verb"),
              ("#ADJ", "term must be an adjective"),
              ("#ADV", "term must be an adverb")
              ])


query_dict = Backend.queryString_to_dict(keywords)

#-----------------------    QUERY EXPANSION   -----------------------
st.markdown("""---""")
st.header("2) Query Expansion")

st.markdown("Expand your keywords with simlar terms to generate more results (improve the recall)")

col1, col2 = st.columns(2)
with col1:
    "Query Expansion Model"
    wordnet = st.checkbox("WordNet", True)
    jobim = st.checkbox("JoBim", True)
    fastext = st.checkbox("FastText", False)
    qeTermNumber = st.number_input("Number of expansion terms", min_value=1, value=10, key="anzahlExpansionTerme")
with col2:
    "Include Sub or Super Concepts"
    superTerm = st.checkbox("Find Superordinate Concept / Hypernyms (Oberbegriffe)", False)
    if superTerm:
        superTermNumber = st.number_input("Number of terms", min_value=1, value=1, key="numberSuperTerms")
    subTerm = st.checkbox("Find Sub concept / Hyponyms (Unterbegriffe)", False)
    if subTerm:
        subTermNumber = st.number_input("Number of terms", min_value=1, value=10, key="numberSubTerms")

st.write("Expanded keywords: " + keywords)
st.button("Start Query Expansion", on_click=queryExpansion(), type="primary")

# Get and select Query Expansion Data
if st.session_state.initialized:
    # Can be used to update without display or not update on every entry, if performace issues arise
    if st.session_state.expandQueryStart:
        widgetID = 0 # continuos number for all created AgGrid Tables; need in order to not run into dublicate widget ID Error
        temp_query_expanded_dict = {}
        temp_query_usecaseSearch_string = "" # generates the string for the Use Case Search
        first_word = True
        for queryTerm in query_dict:
            if query_dict[queryTerm]["proximity"] == None:
                _pos_tag = query_dict[queryTerm]["pos_tag"]
                st.subheader("Expansion of the query term: " + queryTerm)

                # get and display  Query Expansion of each term of the query
                st.write("Similar Terms for " + queryTerm)

                data_termExpansion = {"Terms": Backend.expandWord(queryTerm, qeTermNumber,_pos_tag, wordnet, jobim, fastext, fasttextModel)}
                data_termExpansion_DF = pd.DataFrame(data_termExpansion)
                termSelection_queryTerm = selectionTable(data_termExpansion_DF, widgetID)
                widgetID += 1
                userSelectedTerms = termSelection_queryTerm



                # get and display Super Concepts of each term of the query
                if superTerm:
                    st.write("Super Concept of " + queryTerm)
                    super = {"Terms": Backend.getOberbegriff_WordNet(queryTerm, superTermNumber, _pos_tag)}
                    super_DF = pd.DataFrame(super)
                    termSelection_super = selectionTable(super_DF, widgetID)
                    widgetID += 1
                    userSelectedTerms = userSelectedTerms + termSelection_super



                # get and display  Sub Concepts of each term of the query
                if subTerm:
                    st.write("Sub Concept of " + queryTerm)
                    sub = {"Terms": Backend.getUnterbegriff_WordNet(queryTerm, subTermNumber, _pos_tag)}
                    sub_DF = pd.DataFrame(sub)
                    termSelection_sub = selectionTable(sub_DF, widgetID)
                    widgetID += 1
                    userSelectedTerms = userSelectedTerms + termSelection_sub

                # create new entries in the expanded query dict according to the selected terms, starts with original terms and adds after that
                temp_query_expanded_dict[queryTerm] = {"operator": query_dict[queryTerm]["operator"],
                                                  "pos_tag": query_dict[queryTerm]["pos_tag"],
                                                  "proximity": query_dict[queryTerm]["proximity"]}
                for entry in userSelectedTerms:
                    temp_query_expanded_dict[entry["Terms"]] = {"operator": query_dict[queryTerm]["operator"],
                                                           "pos_tag": query_dict[queryTerm]["pos_tag"],
                                                           "proximity": query_dict[queryTerm]["proximity"]}

                if first_word == True:
                    temp_query_usecaseSearch_string += "(" + queryTerm
                    for term in userSelectedTerms:
                        temp_query_usecaseSearch_string += " OR " + term["Terms"]
                    first_word = False
                else:
                    if query_dict[queryTerm]["operator"] == "+" or None:
                        temp_query_usecaseSearch_string += ") AND (" + queryTerm
                    if query_dict[queryTerm]["operator"] == "-":
                        temp_query_usecaseSearch_string += ") NOT (" + queryTerm
                    for term in userSelectedTerms:
                        temp_query_usecaseSearch_string += " OR " + term["Terms"]
        temp_query_usecaseSearch_string += ")"
# -----------------------    QUERY REFINEMENT   -----------------------
    st.markdown("""---""")
    st.header("3) Query Refinement")

    searchtype = st.radio("The output and presentation depends on the goal of your search. Please specify:",
                          ("Use Case Search", "Technology Search"))
    with st.expander("Information about the search types"):
        "Use Case Search: How can an existing technologiy be used in different contenxt"
        "Technology Search: Which technologies can be used to establish a given Use Case"

    if uploadFile == None:
        expandedQueryString = Backend.dict_to_queryString(temp_query_expanded_dict)

    if searchtype == "Use Case Search" and uploadFile == None:
        #expandedQueryString = insert_parentheses(Backend.dict_to_queryString(query_dict), expandedQueryString)
        expandedQueryString = temp_query_usecaseSearch_string


    queryString_refined = st.text_input("Refine your expanded query. You can add search operators or enter new terms", value=expandedQueryString)
    with st.expander("Show possible search operators"):
        "All terms are optional (logical OR). "
        "Additional operators can be given:"
        st.table([("+", "term must be present"),
                  ("-", "term must not be present"),
                  ("*", "Wildcard, replaces zero or more characters"),
                  ("?", "Wildcard, replaces one character"),
                 # ("(.....)", "Gouping of terms to form sub-queries"),
                  (' "...." ', "Phase that must be matched"),
                  (' "WORD1 WORD2"~NUMBER ', "maximum distance between given word; distance given in words"),
                  ("#NOUN", "term must be a noun, e.g. brake#NOUN"),
                  ("#VERB", "term mus be a verb"),
                  ("#ADJ", "term must be an adjective"),
                  ("#ADV", "term must be an adverb"),
                  ("AND", "logical AND operator"),
                  ("OR", "logical OR operator")
                  ])
    if searchtype =="Technology Search":
        results_to_display = st.number_input("Number of results to display (for TECHNOLOGY SEARCH only)", min_value=1, value=10, key="numberresults_to_display")
        st.markdown("Remark: For **technology search** the maximum number of terms that must be present (operator +) is 10, due to restriction in the visualisation")

    query_dict_refinded = Backend.queryString_to_dict(queryString_refined)
    queryString_refined = "'" + queryString_refined + "'"
    st.write(queryString_refined)
    st.write(query_dict_refinded)
    " "

    col1, col2 = st.columns([3,1])
    with col1:
        fileName = st.text_input("Name your search = file name")
    with col2:
        st.download_button("Synset speichern", data=queryString_refined, file_name=fileName+".txt")
    " "


    search_Type = st.radio("Search will be carried out in the fulltext of the indexed patents (all Titles, Abstacts, Descriptions and Claims) or; Define if the query should be fullfilled within a patent or within an single sentence:",
                           ("Document search", "Sentence search"))




    # enforce the restiction of maximum number of terms for the technology search
    # get the number of term with operator "+"
    disable_visualistion_button = False
    if searchtype =="Technology Search":
        number_positive_terms = 0
        for term in query_dict_refinded:
            if query_dict_refinded[term]["operator"] == "+":
                number_positive_terms +=1
        # stop the workstream until an exceeded number of terms reduced
        if number_positive_terms > 10:
            st.error("Maximum number of positive terms (operator +) exceeded. Please correct the refined query. Maximum number = 10; Number entered = "+ str(number_positive_terms))
            disable_visualistion_button = True

    if st.button("Start Visualisation",type="primary", disabled=disable_visualistion_button):
        startVisualisation()
        if searchtype == "Use Case Search":
            dataframe_CPC_Subclass, dataframe_CPC_Maingroup, dataframe_Assignee = Backend.useCaseSearch(queryString_refined, query_dict_refinded, search_Type)
        if searchtype == "Technology Search":
            #Tech_results_dict = Backend.overlap_search(query_dict_refinded, search_Type, results_to_display)
            st.write(query_dict_refinded)
            overlap_results_dict = Backend.overlap_search(query_dict_refinded, search_Type, results_to_display)

    if st.session_state.visualisation_start:
        st.markdown("""---""")
        st.header("4) Visualization")

        # Definition of the visualition for the USE CASE SEARCH
        if searchtype == "Use Case Search":

            if searchtype == "Use Case Search":
                st.write("Visualization of a use-case search")
                st.write("CPC SUBCLASSES")
                st.dataframe(dataframe_CPC_Subclass)
                st.write("CPC MAIN GROUPS")
                st.dataframe(dataframe_CPC_Maingroup)
                st.write("ASSIGNEES")
                st.dataframe(dataframe_Assignee)


        # Definition of the visualition for the TECHNOLOGY SEARCH
        if searchtype == "Technology Search":

            #Create the visualisation table for each result in the dictionary of results
            for entry in overlap_results_dict:
                df = pd.DataFrame(overlap_results_dict[entry]["overview"])
                df = df.transpose()
                #st.dataframe(df, use_container_width=True)
                st.table(df)
                with st.expander("Details"):
                    overlap_results_dict[entry]["details"]


            # style = df.style.hide_index()
            # style.hide_columns()
            # st.write(style.to_html(), unsafe_allow_html=True)

            # data = {
            #     "first column": [1],
            #     "second column": [10]}
            # df = pd.DataFrame(data)
            # st.dataframe(df, use_container_width=True)
            # with st.expander("asdsafd"):
            #     "alsdfjölkdsaökjsadflöajsf"
            #
            # data = {
            #     "first column": [1],
            #     "second column": [10]}
            # df = pd.DataFrame(data)
            # st.dataframe(df, use_container_width=True)
            # with st.expander("asdsafd"):
            #     "alsdfjölkdsaökjsadflöajsf"
            #
            # data = {
            #     "first column": [1],
            #     "second column": [10]}
            # df = pd.DataFrame(data)
            # st.dataframe(df, use_container_width=True)
            # with st.expander("asdsafd"):
            #     "alsdfjölkdsaökjsadflöajsf"
            #
            # with st.expander("asdsafd"):
            #     "alsdfjölkdsaökjsadflöajsf"

            #example strings for testing
            #caption_string = "Term1 | Term2 | Term3 | Term1 | Term2 | Term3 | Term1 | Term2 | Term3 | Number of Terms | Patents"
            #results_string = "...J...|___N___|___N___|___N___|___N___|   N   |   N   |   N   |   N   |       14        |   1    "
            #resultsDetails_String = ["Patent123123123, Anmelder, Link,...", "Patent123123123, Anmelder, Link,...", "Patent123123123, Anmelder, Link,..."]

            # st.write(caption_string)
            #
            # i=0
            # for element in body_string_list:
            #     #st.write(element)
            #     with st.expander(element):
            #         st.write(details_dict_list[i])
            #         #st.write(details_dict_list[i]["Link"])
            #     i += 1



        #with st.expander(results_string):
        #    resultsDetails_String
        #with st.expander(results_string):
        #    resultsDetails_String
        #with st.expander(results_string):
        #    resultsDetails_String





        # OLD CODE TO BE DELTED EVENTUALIY
        # st.number_input("Anzahl an Top Patenten für die Ausgabe", min_value=1, value=10, key="anzahlTopPatenten")
        #
        # #Ausgabe der Resultate
        # gb1 = GridOptionsBuilder.from_dataframe(pd.DataFrame(dfAusgabeDummy))
        # gb1.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=False)
        # gb1.configure_pagination(enabled=True, paginationPageSize=10) #Buttons zum Seitenblättern unter der Tabelle
        # gridOptions1 = gb1.build()
        # AgGrid(pd.DataFrame(dfAusgabeDummy),
        #               gridOptions=gridOptions1,
        #               enable_enterprise_modules=True,
        #               allow_unsafe_jscode=True,
        #               update_mode=GridUpdateMode.SELECTION_CHANGED)
        #
        #
        # st.table(cpcDummy)
        #
        # st.subheader("ANSÄTZE FÜR ZUSÄTZLICHE AUSGABEN")
        # "- Score als Häufigkeitsverteilung + User-Eingabe zur Einstellung eines Cut-Off-Scores, bis zu dem die Ergebnisse ausgegeben werden. Deutlich größerer Datenverkeht zw. Frontend und Backend. Fraglich bis zu welchem Score die Resultate zurückgegeben werden. Es können sicher nicht jedes mal 150.000 Patente dargestellt werden. Ggf. muss eine Reduzierung auf z.B. jedes 10. Patent in der Score-Sortierten Liste durchgeführt werden."
        # "- Statistische Auswertugn der Suchergebnisse, insbesondere der CPC-Klassen (Histogramm der Häufigkeit des Auftretens ab Cut-Off-Score). Wäre eine Zusatzfunktion im Backend "
        #
        # st.subheader("Ausgabe als Overlap-Suche")
        # st.markdown("3 Terme enthalten")
        # AgGrid(pd.DataFrame(dfAusgabeDummy),
        #               gridOptions=gridOptions1,
        #               #enable_enterprise_modules=True,
        #               allow_unsafe_jscode=True,
        #               update_mode=GridUpdateMode.SELECTION_CHANGED,
        #               key=1  )
        #
        #
        # st.markdown("2 Terme enthalten")
        # AgGrid(pd.DataFrame(dfAusgabeDummy),
        #               gridOptions=gridOptions1,
        #               enable_enterprise_modules=True,
        #               allow_unsafe_jscode=True,
        #               update_mode=GridUpdateMode.SELECTION_CHANGED,
        #               key=2  )






if __name__ == "__main__":
    pass
