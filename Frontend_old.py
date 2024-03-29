import time
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from st_aggrid.shared import GridUpdateMode
import pandas as pd
import numpy as np
import Backend


def Convert(lst):
    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return res_dct

#-----------------------    TEST DATEN   -----------------------
# Query Expansion #
trailer = [('Truck-trailer', 0.9386199712753296), ('semi-trailer', 0.9360169768333435), ("trailer's", 0.9236122965812683), ('truck-trailer-trailer', 0.9201167225837708), ('trailer/semi-trailer', 0.9138890504837036), ('trailer.trailer', 0.9103350043296814), ('truck', 0.9096668362617493), ('trailered', 0.9086657762527466), ('trailer-truck', 0.9079216122627258), ('trailer/semitrailer', 0.9059764742851257)]
tractor = [("tractor's", 0.8930355906486511), ('truck-tractor', 0.8929652571678162), ('mower', 0.8926917910575867), ('tractors', 0.8885779976844788), ('backhoe', 0.8791295289993286), ('tractor-mower', 0.8788689374923706), ('towing', 0.8769713044166565), ('skidder', 0.8757275938987732), ('semi-trailer', 0.8754765391349792), ('tractor-trailer', 0.8725751638412476)]
car = [('cars', 0.8518626093864441), ('passenger', 0.846340537071228), ('car.a', 0.8446317315101624), ('car-passenger', 0.8354069590568542), ('passenger-carried', 0.8326546549797058), ('passenger-car', 0.8320203423500061), ('passenger-carrying', 0.8313053846359253), ('car-trucks', 0.8252957463264465), ('passenger-cars', 0.8243130445480347), ('automobile', 0.8207235336303711)]
brake = [('brakes', 0.9286898970603943), ('brake-clutch', 0.9210224151611328), ('braking', 0.9137291312217712), ('brake-off', 0.8989164233207703), ('brake-apply', 0.8987146019935608), ('brake-on', 0.8957924842834473), ('brake-clutches', 0.8955795168876648), ('brake-actuating', 0.8929045796394348), ('shoe-brake', 0.8884227871894836), ('brake-actuation', 0.8883419632911682)]
trailer_str = []
tractor_str = []
car_str = []
brake_str =[]
for i in range(10):
    trailer_str.append(trailer[i][0])
    tractor_str.append(tractor[i][0])
    car_str.append(car[i][0])
    brake_str.append(brake[i][0])

df = pd.DataFrame(
    {
        "brake":brake_str,
        "tractor":tractor_str,
        "trailer": trailer_str,
        "car": car_str
    }
)

# Patentsuche #
anzahl = 10
patenteDummy = []
scoreDummy = []
titleDummy = "Dummy Patent Titel"
CPCDummy = "A61"
for i in range(anzahl):
    scoreDummy.append(np.random.randint(1,100))

#print(patenteDummy)
dfAusgabeDummy = pd.DataFrame(
    {
        "Title":titleDummy,
        "CPC":CPCDummy,
        "Score":scoreDummy,
    }
)
dfAusgabeDummy = dfAusgabeDummy.sort_values("Score", ascending=False)


cpcDummy = pd.DataFrame(
    {
        "Index": [1],
        "cpc": "A61",
        "Desciption": "MEDICAL OR VETERINARY SCIENCE; HYGIENE",
})

#-----------------------    Attribute  -----------------------
df3 = pd.DataFrame()

fasttextModel = None #Must be laoded by click, due to long loading times

if 'initialized' not in st.session_state:
    st.session_state.initialized = False

if 'expandQueryStart' not in st.session_state:
    st.session_state.expandQueryStart = False

if 'selectedTerms' not in st.session_state:
    st.session_state.selectedTerms = []

if 'fastTextModel_loaded' not in st.session_state:
    st.session_state.fastTextModel_loaded = False



#-----------------------    DEFINITION DER FUNKTIONEN   -----------------------
def sucheStarten():
    with st.spinner('Suche im Index wird durchgeführt'):
        time.sleep(3)
    st.success('Suche abgeschlossen')


def queryExpansion():
    st.session_state.QEDataframe = Backend.expandQuery(keywords, qeTermNumber, wordnet, jobim, fastext, fasttextModel) #creates a new sesson state variable each time the function is called. This prevents the
    # todo: FUNKTIONSERWEITERUNG - POS-Tags könnten hier nicht herausgefiltert, sondern in den späteren Abfragen zur Verbesserung der Resultate verwendet werden.
    st.session_state.initialized = True
    st.session_state.expandQueryStart = True

def set_sessionStateQueryExpansion_to_False():
    st.session_state.expandQueryStart=False

#Load the model into cache to speed up the searches following the first loading
@st.cache_data
def load_fasttext(text):
    _model = Backend.startFastText()
    return _model

def selectionTable(dataToDisplay):
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
                  update_mode=GridUpdateMode.SELECTION_CHANGED)
    #Die ausgewählten Terme werden an die Auswahlliste angehangen
    for auswahl in data["selected_rows"]:
        termeAuswahl.append(auswahl[queryTerm])
    return termeAuswahl

#-----------------------    LAYOUT DER WEBAPPLICATION   -----------------------
st.title("Multiterm-Overlap-Search for Technologies and Use Cases in Patents")

with st.sidebar:
    st.file_uploader("Load a synset", type=[".txt"])
    st.markdown("""---""")
    st.header("Status")
    # Pre-Load the HPI-FastText Model; needed to speed up search, as the loading can take several minutes
    if fasttextModel != None:
        st.markdown("FastText Model :green[loaded]")
    else:
        st.write("FastText Model :red[not loaded]")
    if st.button("Load Fastext"):
        fasttextModel = load_fasttext("asdf")




st.markdown("""---""")
st.header("1) Keywords")
keywords = st.text_input("Enter Keywords describing the an application or a technology ", key="keywords", placeholder="+brake +(tractor trailer) -car", on_change= set_sessionStateQueryExpansion_to_False)
with st.expander("Show possible search operators"):
    "All terms are optional (logical OR). "
    "Additional operators can be given:"
    st.table([("+", "term must be present"),
              ("-", "term must not be present"),
              ("*", "Wildcard, replaces one or more characters"),
              ("(.....)", "Gouping of terms to form sub-queries"),
              (' "...." ', "Phase that must be matched")
              ])


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
st.button("Start Query Expansion", on_click=queryExpansion, type="primary")

# st.markdown("""---""")
# query = st.text_input("Search in patent fulltext (Title, Abstact, Description and Claims) ", key="query", placeholder="brake#NOUN AND (tractor OR trailer) NOT car")
# queryInSentence = st.text_input("Alternativly search in a sentence ", key="queryInSatz", placeholder='"brake rear"~5 NOT drum')
# "Beide Sucheanfragen werden nacheinander ausgeführt und über den Score zusammengeführt"
#
# with st.expander("Show search operators"):
#     "All terms are optional (logical OR). "
#     "Additional operators can be given:"
#     st.table([("+", "term must be present"),
#               ("-", "term must not be present"),
#               ("*", "Wildcard, replaces one or more characters"),
#               ("(.....)", "Gouping of terms to form sub-queries"),
#               (' "...." ', "Phase that must be matched")
#               ])
#     "POS-Tags (Part-of-Speach-Tags) must be placed after the word to be tagged separated with one hash #"
#     "permissible tags are:"
#     st.table([("VERB", "Verb"),
#               ("NOUN", "Noun"),
#               ("ADJ", "Adjective"),
#               ("ADV", "Adverb")
#               ])
#
# col1, col2 = st.columns(2)
# with col1:
#     "Query Expansion Model"
#     wordnet = st.checkbox("WordNet", True)
#     jobim = st.checkbox("JoBim", False)
#     fastext = st.checkbox("FastText", False)
#     qeTermNumber = st.number_input("Number of expansion terms", min_value=1, value=10, key="anzahlExpansionTerme")
# with col2:
#     "Include Sub or Super Concepts"
#     superTerm = st.checkbox("Find Superordinate Concept / Hypernyms (Oberbegriffe)", False)
#     # if superTerm:
#     #     superTermNumber = st.number_input("Number of terms", min_value=1, value=3, key="numberSuperTerms")
#     subTerm = st.checkbox("Find Sub concept / Hyponyms (Unterbegriffe)", False)
#     # if subTerm:
#     #     subTermNumber = st.number_input("Number of terms", min_value=1, value=3, key="numberSubTerms")
#
# st.button("Erweitere Query", on_click=queryExpansion, type="primary")
#
# query = Backend.splitQuery(query, False)
#
# st.markdown("""---""")
# st.header("Query Expansion")

# if st.session_state.expandQueryStart:
#     query = Backend.splitQuery(keywords, False)
#     dataToDisplay = Backend.expandQuery(keywords, qeTermNumber, wordnet, jobim, fastext)
#     st.write(dataToDisplay)
#     for term in query:
#         #dataframe = pd.DataFrame()
#         queryTerms =[]
#         if subTerm==False and superTerm==False:
#             dataToDisplay = Backend.expandQuery(term, qeTermNumber, wordnet, jobim, fastext)
#             st.write(dataToDisplay)
#         elif superTerm:
#             queryTerms = Backend.getOberbegriff_WordNet(term)
#         queryTerms.append(term)
#         if subTerm:
#             listsubterm = Backend.getUnterbegriff_WordNet(term,5)
#             for i in listsubterm:
#                 queryTerms.append(i)
#         if subTerm:
#             #todo: Funktionserweiterung - dynamische Tabs, die sich mit einer einzugeben Zahl von Unter- oder Oberbegriffen anpassen. Ist nicht Teil von Streamlit, kann jedoch ggf. als Component erweitert werden
#             tab1, tab2, tab3, tab4, tab5, tab6, tab7  = st.tabs(["SUPER: " + queryTerms[0], "QUERY: " + queryTerms[1], "SUB: " +  queryTerms[2], "SUB: " + queryTerms[3], "SUB: " + queryTerms[4],"SUB: " +  queryTerms[5],"SUB: " +  queryTerms[6]])
#             with tab1:
#                 st.write(Backend.expandQuery(queryTerms[0], qeTermNumber, wordnet, jobim, fastext))
#             with tab1:
#                 st.write(Backend.expandQuery(queryTerms[1], qeTermNumber, wordnet, jobim, fastext))
#             with tab2:
#                 st.write(Backend.expandQuery(queryTerms[2], qeTermNumber, wordnet, jobim, fastext))
#             with tab3:
#                 st.write(Backend.expandQuery(queryTerms[3], qeTermNumber, wordnet, jobim, fastext))
#             with tab4:
#                 st.write(Backend.expandQuery(queryTerms[4], qeTermNumber, wordnet, jobim, fastext))
#             with tab5:
#                 st.write(Backend.expandQuery(queryTerms[5], qeTermNumber, wordnet, jobim, fastext))
#             with tab6:
#                 st.write(Backend.expandQuery(queryTerms[6], qeTermNumber, wordnet, jobim, fastext))
#             with tab7:
#                 st.write(Backend.expandQuery(queryTerms[7], qeTermNumber, wordnet, jobim, fastext))

# Get and select Query Expansion Data
if st.session_state.initialized:
    # Can be used to update without display or not update on every entry, if performace issues arise
    if st.session_state.expandQueryStart:
        for queryTerm in st.session_state.QEDataframe.columns:
            st.subheader("Expansion of the query term: " + queryTerm)

            #get and display Super Concepts of each term of the query
            if superTerm:
                super = {"Super Concept of " + queryTerm : Backend.getOberbegriff_WordNet(queryTerm, superTermNumber)}
                super_DF = pd.DataFrame(super)
                termSelection_super = selectionTable(super_DF)

            #get and display  Query Expansion of each term of the query
            data_termExpansion = Backend.expandQuery(queryTerm, qeTermNumber, wordnet, jobim, fastext, fasttextModel)
            termSelection_termExpansion = selectionTable(data_termExpansion)

            #get and display  Sub Concepts of each term of the query
            if subTerm:
                sub = {"Sub Concept of " + queryTerm :Backend.getUnterbegriff_WordNet(queryTerm, subTermNumber)}
                sub_DF = pd.DataFrame(sub)
                termSelection_sub = selectionTable(sub_DF)






# if st.session_state.initialized:
#     termeAuswahl = []
#     #für jede Spalte des Dataframes der Suche = für jeden Suchterm wird eine AgGrid-Tabelle konfiguriert und dargestellt
#     for queryTerm in st.session_state.QEDataframe.columns:
#
#         # Processing of each term in the query
#         st.subheader("Expansion of the query term: " + queryTerm)
#         numberOfTabs = 1
#         #Build the dataframe to display without sub oder superterm
#
#         #Expansino of each query term
#         dataToDisplay = st.session_state.QEDataframe[queryTerm]
#         termAuswahl_termExpansion = selectionTable(dataToDisplay)
#
#         if superTerm:
#             st.caption('Superordinate Concept (Oberbegriff)')
#             dataToDisplay = [Backend.getOberbegriff_WordNet(queryTerm,1)]
#             st.write(dataToDisplay)
#             termAuswahl_superTerms = selectionTable(dataToDisplay)
#
#
#
#
#         elif subTerm:
#             #liste aus dem Backend holen
#             listSubTerms = Backend.getUnterbegriff_WordNet(queryTerm, subTermNumber)
#             numberOfTabs += listSubTerms.__len__()
#             dataToDisplay = pd.DataFrame()
#             st.write(listSubTerms)
#             # Synonymliste für jeden Subterm erstellen
#             for term in listSubTerms:
#                 subSimilarTerms = Backend.expandQuery(term, qeTermNumber, wordnet, jobim, fastext, fasttextModel)
#                 dataToDisplay = pd.concat([dataToDisplay, subSimilarTerms],ignore_index=True)
#             # Kombination von QEDataframe und der Unterbegriffliste
#             #st.write(frames)
#             #dataToDisplay = pd.concat(frames)
#             #st.write(dataToDisplay)
#             #dataToDisplay = subSimilarTerms + st.session_state.QEDataframe[queryTerm]
#             #st.write(dataToDisplay)
#


    st.number_input("Anzahl an Top Patenten für die Ausgabe", min_value=1, value=10, key="anzahlTopPatenten")
    if st.checkbox('Zeige erweiterte Query'):
        st.write(termeAuswahl)

    overlap = st.checkbox('Overlap-Suche')
    if overlap:
        pass
    st.button("Suche im Index", on_click=sucheStarten, type="primary")


st.markdown("""---""")
st.header("Ausgabe")
st.download_button("Synset speichern", data="tbd")

#Ausgabe der Resultate
gb1 = GridOptionsBuilder.from_dataframe(pd.DataFrame(dfAusgabeDummy))
gb1.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=False)
gb1.configure_pagination(enabled=True, paginationPageSize=10) #Buttons zum Seitenblättern unter der Tabelle
gridOptions1 = gb1.build()
AgGrid(pd.DataFrame(dfAusgabeDummy),
              gridOptions=gridOptions1,
              enable_enterprise_modules=True,
              allow_unsafe_jscode=True,
              update_mode=GridUpdateMode.SELECTION_CHANGED)


st.table(cpcDummy)

st.subheader("ANSÄTZE FÜR ZUSÄTZLICHE AUSGABEN")
"- Score als Häufigkeitsverteilung + User-Eingabe zur Einstellung eines Cut-Off-Scores, bis zu dem die Ergebnisse ausgegeben werden. Deutlich größerer Datenverkeht zw. Frontend und Backend. Fraglich bis zu welchem Score die Resultate zurückgegeben werden. Es können sicher nicht jedes mal 150.000 Patente dargestellt werden. Ggf. muss eine Reduzierung auf z.B. jedes 10. Patent in der Score-Sortierten Liste durchgeführt werden."
"- Statistische Auswertugn der Suchergebnisse, insbesondere der CPC-Klassen (Histogramm der Häufigkeit des Auftretens ab Cut-Off-Score). Wäre eine Zusatzfunktion im Backend "

st.subheader("Ausgabe als Overlap-Suche")
st.markdown("3 Terme enthalten")
AgGrid(pd.DataFrame(dfAusgabeDummy),
              gridOptions=gridOptions1,
              #enable_enterprise_modules=True,
              allow_unsafe_jscode=True,
              update_mode=GridUpdateMode.SELECTION_CHANGED,
              key=1  )


st.markdown("2 Terme enthalten")
AgGrid(pd.DataFrame(dfAusgabeDummy),
              gridOptions=gridOptions1,
              enable_enterprise_modules=True,
              allow_unsafe_jscode=True,
              update_mode=GridUpdateMode.SELECTION_CHANGED,
              key=2  )







