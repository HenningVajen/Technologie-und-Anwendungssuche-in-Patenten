import json
import os
import pickle
import config


def dateienEinlesen(_pfad):
    _dateienListe = os.listdir(_pfad)  # Dateiliste im Verzeich der Datenablage erstellen
    __dateienListe = _dateienListe.copy()
    for datei in _dateienListe:
        if not ('.json' in datei):
            __dateienListe.remove(datei)
    return __dateienListe


def leseJSONlines(dateienListe_):
    patentdatenObjekt_ = dict()
    anzahlDoubletten = 0
    cpcLeerDict = {"code": "unknown"}
    cpcLeereListe = [cpcLeerDict, cpcLeerDict]

    for datei_ in dateienListe_:
        with open(os.path.join(config.pfadDateneingabe, datei_), 'r') as jsonDatei:
            for line in jsonDatei:
                temp = json.loads(line)
                if not temp["cpc"]: #Fängt leere Einträge ab
                    temp["cpc"] = cpcLeereListe
                #print(str(temp["publication_number"]) + "   " + str(temp["cpc"]))
                if patentdatenObjekt_.__contains__(temp["publication_number"]):
                    anzahlDoubletten = anzahlDoubletten + 1
                    print(str(anzahlDoubletten) + " doppelte Publication Number gefunden: "  + temp["publication_number"] + ".    Nur der erste Eintrag wird verarbeitet.")
                else:
                    patentdatenObjekt_[temp["publication_number"]] = {
                    "publication_date": int(temp["publication_date"]),
                    "title": temp["title"],
                    "abstract": temp["abstract"],
                    "claims": temp["claims"],
                    "description": temp["description"],
                    "cpc": temp["cpc"][0]['code'], #aus dem dict wird der CPC Code des erste (Haupt-)Eintrags übernommen
                    "assignee1": temp["assignee1"],
                }
    print(str(patentdatenObjekt_.__len__()) + " Datensätze eingelesen")
    return patentdatenObjekt_


def zaehlenEinzigartigerPatente(dateienListe_):
    patentdatenObjekt_ = dict()
    anzahlDoubletten = 0
    for datei_ in dateienListe_:
        with open(os.path.join(config.pfadDateneingabe, datei_), 'r') as jsonDatei:
            for line in jsonDatei:
                temp = json.loads(line)
                print(temp["cpc"][0]['code'])
                if patentdatenObjekt_.__contains__(temp["publication_number"]):
                    anzahlDoubletten = anzahlDoubletten + 1
                    print(str(anzahlDoubletten) + " DOUBLETTE GEFUNDEN "  + temp["publication_number"])
                patentdatenObjekt_[temp["publication_number"]] = {
                }


def split_dictionary(input_dict, chunk_size):
    res = []
    new_dict = {}
    for k, v in input_dict.items():
        if len(new_dict) < chunk_size:
            new_dict[k] = v
        else:
            res.append(new_dict)
            new_dict = {k: v}
    res.append(new_dict)
    return res


def speichereObjekt(object, pfad, dateiname):
    is_stored = True
    try:
        file = open(os.path.join(pfad, dateiname), 'wb')
        pickle.dump(object, file)
        file.close()
    except Exception as e:
        print("Speicherung des Objektes fehlgeschlagen")
        print(str(e))
        is_stored = False
    finally:
        return is_stored


def ladeObjekt(pfad, dateiname):
    file = open(os.path.join(pfad, dateiname), 'rb')
    objekt = pickle.load(file)
    file.close()
    return objekt


def jsonDateienEinlesen(pfadDateneingabe):
    print("\n", '########## Einlesen der Dateien ##########')
    print("Pfad der Daten: " + str(pfadDateneingabe))
    dateienListe = dateienEinlesen(pfadDateneingabe)
    print("Einlesen der Dateie(n) " + str(dateienListe))
    patentdatenDict = dict()
    patentdatenDict = leseJSONlines(dateienListe)
    return patentdatenDict



if __name__ == "__main__":
    pass
