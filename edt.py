#!/usr/bin/python

#ical
from requests   import post,Request
from zoneinfo   import ZoneInfo
from datetime   import datetime
from icalendar  import Calendar, Event, vText, vDatetime, vCalAddress

#traiter la couleur
from webcolors          import hex_to_name, hex_to_rgb, rgb_to_hex
from scipy.spatial      import KDTree

#publier les agendas
from time       import time
from hashlib    import md5


conf = {
    "auth": ("",""), #tuple storing my authentification data, e.g. ("foo", "bar")
    "prototype": {
        "id": "",
        "date_debut": "01/01/2025 8:00:00",
        "date_fin": "01/01/2025 9:20:00",
        "categorie": "Sans catégorie",
        "couleur": "#40A0FF", #adoucir(couleur["UEO"])
        "enseignant": [],
        "equipe": [],
        "salle": [],
        "groupe": [],
        "matiere": [],
        "remarque": ""
    },
    "exclusion": {
        "annulé", "férié", "congés", "evénement ua", "réservation", "interruption des cours", "indisponibilité", "invisible étudiant", "révisions"
    },
    "inclusion": {
        "distance", "spe", "récup", "rattrapage", "hybride", "ancien", "examen cm", "continu cm", "choix encadrés"
    },
    "edt":{
        "perso": { # mon emploi du temps
            'id': "E9FDFA3899510A1D790FD6DF7A55B9F21",
            'dateDebut': "20230821",
            'dateFin':   "20240616"
        },
        "p2": { # tous les edts / santé (médecine) / 2ème année
            'id': "G9F8A5BD6AA0188EDE0530100007FD17D",
            'dateDebut': "20240916",
            'dateFin':   "20251231"
        },
        "l2": { # tous les edts / sciences / L2 M2 6-7
            'id': "G9F8A5BD6AC7088EDE0530100007FD17D",
            'dateDebut': "20240909",
            'dateFin':   "20251231"
        }
    }
}

def strip(ble):
    return [epi.strip() for epi in ble] if type(ble) is list else ble.strip()

def date2utc(date):
    return datetime.strptime(date, "%d/%m/%Y %H:%M:%S").replace(tzinfo = ZoneInfo("Europe/Paris")).astimezone(ZoneInfo("UTC"))

def nompre(nompre):
    for index, lettre in enumerate(nompre):
        if lettre.islower():
            return [nompre[index - 1:].strip(), nompre[:index - 1].strip()]

    return ["", nompre.strip()]

def attendee(cutype, cn, adr):
    part = vCalAddress("MAILTO:" + adr)
    part.params["cutype"]   = vText(cutype)
    part.params["cn"]       = vText(cn)

    return part

celcat = {
    edt: post("https://edt.univ-angers.fr/edt/jsonSemaine", parargs).json() for edt, parargs in conf["edt"].items()
}

celdog = {
    edt: [
        {
            champs: strip(e.get(champs, "")) or ble for champs, ble in conf["prototype"].items()
        } for e in celcat[edt] if not any(exclu in e.get("categorie", "").lower() for exclu in conf["exclusion"])
    ] for edt in celcat
}

css3_colors = [
    '#f0f8ff', '#faebd7', '#00ffff', '#7fffd4', '#f0ffff', '#f5f5dc', '#ffe4c4', '#000000', '#ffebcd', '#0000ff', '#8a2be2', '#a52a2a', '#deb887', '#5f9ea0', '#7fff00', '#d2691e', '#ff7f50', '#6495ed', '#fff8dc', '#dc143c', '#00008b', '#008b8b', '#b8860b', '#a9a9a9', '#006400', '#bdb76b', '#8b008b', '#556b2f', '#ff8c00', '#9932cc', '#8b0000', '#e9967a', '#8fbc8f', '#483d8b', '#2f4f4f', '#00ced1', '#9400d3', '#ff1493', '#00bfff', '#696969', '#1e90ff', '#b22222', '#fffaf0', '#228b22', '#ff00ff', '#dcdcdc', '#f8f8ff', '#ffd700', '#daa520', '#808080', '#008000', '#adff2f', '#f0fff0', '#ff69b4', '#cd5c5c', '#4b0082', '#fffff0', '#f0e68c', '#e6e6fa', '#fff0f5', '#7cfc00', '#fffacd', '#add8e6', '#f08080', '#e0ffff', '#fafad2', '#d3d3d3', '#90ee90', '#ffb6c1', '#ffa07a', '#20b2aa', '#87cefa', '#778899', '#b0c4de', '#ffffe0', '#00ff00', '#32cd32', '#faf0e6', '#800000', '#66cdaa', '#0000cd', '#ba55d3', '#9370db', '#3cb371', '#7b68ee', '#00fa9a', '#48d1cc', '#c71585', '#191970', '#f5fffa', '#ffe4e1', '#ffe4b5', '#ffdead', '#000080', '#fdf5e6', '#808000', '#6b8e23', '#ffa500', '#ff4500', '#da70d6', '#eee8aa', '#98fb98', '#afeeee', '#db7093', '#ffefd5', '#ffdab9', '#cd853f', '#ffc0cb', '#dda0dd', '#b0e0e6', '#800080', '#ff0000', '#bc8f8f', '#4169e1', '#8b4513', '#fa8072', '#f4a460', '#2e8b57', '#fff5ee', '#a0522d', '#c0c0c0', '#87ceeb', '#6a5acd', '#708090', '#fffafa', '#00ff7f', '#4682b4', '#d2b48c', '#008080', '#d8bfd8', '#ff6347', '#40e0d0', '#ee82ee', '#f5deb3', '#ffffff', '#f5f5f5', '#ffff00', '#9acd32'
]

t = KDTree([hex_to_rgb(hex) for hex in css3_colors])

cat = {
    e["categorie"]: hex_to_name(css3_colors[t.query(tuple(round(c * 0.75 + 255 * 0.25) for c in hex_to_rgb(e["couleur"])))[1]]) for edt in celdog for e in celdog[edt] + [conf["prototype"]] #ajouter l'événement générique
}

#agendas principaux
cal = {
    edt: Calendar() | {
        "prodid":       vText("-//" + edt + "//"),
        "version":      vText('2.0'),
        "color":        vText(cat[edt]),
        "name":         vText(edt),
        "x-wr-calname": vText(edt)
    } for edt in cat if not any(inclu in edt.lower() for inclu in conf["inclusion"]) or edt.lower() == "cours à distance"
}

principaux = list(cal)

#alias
cal |= {
    categorie: cal[edt if any(categorie.startswith(edt := agenda) for agenda in sorted(principaux, reverse=True)) else conf["prototype"]["categorie"]] for categorie in cat
}

print({e.get("categorie") for edt in conf["edt"].keys() for e in celcat[edt]})
print("\n")
print(list[cat])
print("\n")
print(principaux)


def filtre(e, edt):
    if edt == "p2":
        if not "2ème année" in e["groupe"] and not "2ème année - G2" in e["groupe"]:
            if any("2ème année - " + grp in e["groupe"] for grp in ["G1", "G3", "G4"]):
                return 0 #groupes 1, 3 et 4
        
        if "optionnel" in (mat := "".join(e["matiere"]).lower()):
            if any(maj in mat for maj in ["tutorat", "sens et vécu"]):
                return 0 #majeur tuto, sens et vécu
               
        if "TP" in e["categorie"]:
            if set(e["enseignant"]) & {"GOUEL Yamina", "RACHIERU SOURISSEAU Petronela", "RIQUIN Elise", "MENARD Laure-Anne"}:
                return 0 #communication etc...
    
    if edt == "l2":
        if "TP" in e["categorie"]:
            if "anglais" in "".join(e["matiere"]).lower():
                return 0 #anglais
        if "Tutorat" in e["categorie"]:
            return 0
    
    return 1

def e2cal(e, edt):
    cal[e["categorie"]].add_component(Event() |
        {p: a for p, a in {
            "dtstart":  vDatetime(date2utc(e["date_debut"])),
            "dtend":    vDatetime(date2utc(e["date_fin"])),
            "uid":      vText(conf["edt"][edt]["id"] + "-" + e["id"]),
    
            "summary":      vText( " ".join(e["matiere"]) or e["categorie"]),
            "location":     vText(", ".join(e["salle"]).replace("MED-", "").replace("AMPHI", "Amphi")),
            "description":  vText(e["remarque"]),
    
            "color": vText(cat[e["categorie"]]), #if e["categorie"] not in principaux else "",

            "attendee": [attendee(
                            "INDIVIDUAL",
                            " ".join(nompre(prof)).strip(),
                            ".".join([copule.replace(" ","").lower() for copule in nompre(prof)])
                        ) for prof in e["enseignant"]] +
                        [attendee(
                            "GROUP",
                            groupe,
                            groupe.strip().replace(" ",".").lower()
                        ) for groupe in e["groupe"] + e["equipe"]]
        }.items() if a})

for edt in conf["edt"]:
    for e in celdog[edt]:
            if filtre(e, edt):
                e2cal(e, edt)


#préparation de l'envoi
req = Request("POST", "https://None", files= {edt:
    (
        edt,
        ical := cal[edt].to_ical(),
        "",
        {
            "X-File-Path":      "/Agendas/" + edt.replace("/","_") + ".ics",
            "X-OC-Mtime":       int(time()),
            "X-File-MD5":       md5(ical).hexdigest(),
            "Content-Length":   len(ical)
        }
    ) for edt in principaux
}).prepare()

#envoi
post(
    "https://uabox.univ-angers.fr/remote.php/dav/bulk/",
    headers={"Content-Type": req.headers["Content-Type"].replace("multipart/form-data", "multipart/related")},
    data=req.body,
    auth=conf["auth"]
)
