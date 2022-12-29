




#-----------------------    CONFIG   -----------------------
pfadPatentDict = "tbd"  #Pfad der Patentwörterbuchs
pfadCPCDict ="tbd"      #Pfad zum Wörterbuch der CPC-Beschreibungen

#-----------------------------------------------------------


def dictPatentdaten_einlesen(pfadPatentDict):
    pass
    return True


def dictCPC_einlesen(pfadCPCDict):
    pass
    return True


def serverstatus_abfragen():
    #Alle Modelle und Wörterbucher vorhanden und eingelesen
    pass
    return True


def serverStarten():
    #Suchserver starten, Wörterbucher und Modelle einlesen
    pass


def queryErweitern(QueryDict):
    #Dict der Query enthält Strings zur Suche im Satz oder Volltext / POS Index => Trenen der Suchterme von den Suchannotationen
    #Starten der Erweiterung der Query in allen Modellen
    #Zusammenführen der Ergebnisse der QEs entsprechend des Rankings
    #Bau eines dataframes (Ursprüngliche Suche und Terme zur Erweiterung) zur Rückgabe an das Frontend
    pass

def erweiterteQueryAusführen(ErwQueryDict):
    #Aufsplitten der Query
    #Wenn Overlap-Suche == True, Suchanfrage für die Overlapping erzeugen
    #Suche im jeweiligen Index ausführen
    #Resulate zusammenführen (wenn mehrere Indexe abgefragt wurden)
    #CPC-Klassen der TOP-Patente bestimmen und anhängen
    #Alles als Dataframe zusammenfassen und an Frontend senden (incl. der Ursprünglichen Query, um das Synset im Frontend zu speichern
    pass



if __name__ == "__main__":
    pass