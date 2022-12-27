import time
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from st_aggrid.shared import GridUpdateMode
import pandas as pd
import numpy as np


def Convert(lst):
    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return res_dct

#-----------------------    TEST DATEN   -----------------------
# Query Expansion #
trailer = [('truck-trailer', 0.9386199712753296), ('semi-trailer', 0.9360169768333435), ("trailer's", 0.9236122965812683), ('truck-trailer-trailer', 0.9201167225837708), ('trailer/semi-trailer', 0.9138890504837036), ('trailer.trailer', 0.9103350043296814), ('truck', 0.9096668362617493), ('trailered', 0.9086657762527466), ('trailer-truck', 0.9079216122627258), ('trailer/semitrailer', 0.9059764742851257)]
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

print(patenteDummy)
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
print(cpcDummy)

#-----------------------    DEFINITION DER FUNKTIONEN   -----------------------
def sucheStarten():
    with st.spinner('Suche im Index wird durchgeführt'):
        time.sleep(3)
    st.success('Suche abgeschlossen')

def queryExpansion():
    pass


#-----------------------    LAYOUT DER WEBAPPLICATION   -----------------------
st.title("Multiterm-Overlap-Suche nach Technologien und Applikationen in Patenten")


synset = st.sidebar.file_uploader("Gespeichertes Synset verwenden", type=[".txt"])

st.markdown("""---""")
st.header("Status")
"Verbindung zum Backend: OK"

st.markdown("""---""")
st.header("Query")
st.text_input("Die Suchanfrage, kann optional POS-Tags und boolsche Opteratoren ergänzt werden ", key="query", placeholder="brake|NOUN AND (tractor OR trailer) NOT car")
st.text_input("Optional / Alternativ: Suche nach dieser Termen IN EINEM SATZ ", key="queryInSatz", placeholder='"brake rear"~5 NOT drum')
"Beide Sucheanfragen werden nacheinander ausgeführt und über den Score zusammengeführt"
st.number_input("Anzahl an Expansion Termen", min_value=1, value=10, key="anzahlExpansionTerme")
st.button("Erweitere Query", on_click=sucheStarten, type="primary")

st.markdown("""---""")
st.header("Query Expansion")

termeAuswahl = []
#für jede Spalte des Dataframes der Suche = für jeden Suchterm wird eine AgGrid-Tabelle konfiguriert und dargestellt
for spalte in df.columns:
    gb = GridOptionsBuilder.from_dataframe(pd.DataFrame(df[spalte]))
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=False)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)  # Die Reihen auswählbar machen
    # gb.configure_pagination() #Buttons zum Seitenblättern unter der Tabelle
    gridOptions = gb.build()
    data = AgGrid(pd.DataFrame(df[spalte]), #data ist der Rückgabewert der Auswahl der Tabelle
                  gridOptions=gridOptions,
                  #enable_enterprise_modules=True,
                  allow_unsafe_jscode=True,
                  update_mode=GridUpdateMode.SELECTION_CHANGED)
    #Die ausgewählten Terme werden an die Auswahlliste angehangen
    for auswahl in data["selected_rows"]:
        termeAuswahl.append(auswahl[spalte])
        #st.write(auswahl[spalte])

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







