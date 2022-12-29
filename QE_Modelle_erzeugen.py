from datetime import datetime
import gensim
from gensim.models.fasttext import FastText
import os


#-----------------------    CONFIG   -----------------------
pfadDateneingabe = os.path.join(os.getcwd(), "input") #Verzeichnis in dem .json Patentdaten gesucht und verarbeitet werden sollen
DateinameFasttextModel = "patent-100.bin" #Dateiname des vewendeten Fasttext Models. nur .bin Datei. .vec ist menschenlesbar, aber redundant und wird ignoriert
pfadFasttextModel = os.path.join(os.getcwd(), "input", DateinameFasttextModel)
#-----------------------------------------------------------


def expandQueryFastext(wort):
    #gibt die 10 ähnlichsten Worte zurück
    return loaded_HPI_FastText.most_similar(positive=[wort], topn=10)
    #Alternative: simular_by_key


if __name__ == "__main__":
    zeitpunktStart = datetime.now()
    print('Ausführung als main: ' + __file__)

    print("\n", '########## Laden der Query Expansion Modelle ##########')
    print("### HPI FastText ###")
    loaded_HPI_FastText = gensim.models.fasttext.load_facebook_vectors(pfadFasttextModel)
    print(loaded_HPI_FastText)

    man = expandQueryFastext("man")
    brake= expandQueryFastext("brake")
    tractor = expandQueryFastext("tractor")
    trailer = expandQueryFastext("trailer")
    car = expandQueryFastext("car")


    zeitpunktEnde = datetime.now()
    print("\n", "Dauer der Bearbeitung = ", zeitpunktEnde - zeitpunktStart)