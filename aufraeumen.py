"""
aufraeumen.py

Ziel ist es, einen Ordner mit Backups 'aufzurämen':
    - alle Objekte sind Ordner oder Dateien
    - abhängig von den Parametern:
        - halte_monate
        - halte_wochen
        - halte_tage
        werden werden alle anderen Objekte außer denen der aktuellen Woche gelöscht
        Bedeutung:
            - halte_monate: das ist die Anzahl vergangener Monate, von denen noch 
              der letzte Backup erhalten bleiben soll
            - halte_wochen: Anzahl Wochen, von denen der letzte Backup noch erhalten bleiben soll
            - halte_tage: Anzahl Tage der letzten Backups, die erhalten bleiben sollen
        

rg, ab 2026-10-08
"""
BACKUPORDNER = "E:\\calcardbackup"
halte_monate = 3        # wieviele Monate rückwärts je ein Backup erhalten bleibt
halte_wochen = 4        # wieviele Wochen rückwärts je ein Backup erhalten bleibt
halte_tage = 7          # wieviele Tage zurück ein Backup erhalten bleibt

test = False
# test = True
dryrun = False

import os
import stat
import shutil
import time
from dotenv import dotenv_values 
from pathlib import Path
import argparse

heute = time.gmtime()
version = "0.3 vom 2026-10-15"

wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

class dirObjekt(object):
    # Klasse, um einen Verzeichniseintrag mit seinen nötigen Attributen zu halten.
    # Werden sie nicht per Parm übergeben, holt sich die Klasse diese per os.stat-Call    
    def __init__(self, fpn, isDir=None, flen=None, mTime=None) -> None:
        self.fullPathName = fpn
        self.ordner, self.name = os.path.split(fpn)
        if isDir is None or flen is None or mTime is None:
            dat_stat = os.stat(fpn)            
            self.isDir = stat.S_ISDIR(dat_stat.st_mode)
            self.flen = dat_stat.st_size
            self.mtime = dat_stat.st_mtime
        else:
            self.isDir = isDir
            self.flen = flen
            self.mtime = mTime
        self.struzeit = time.gmtime(mTime)

    def __str__(self):
        x = self.fullPathName
        x = x + " Ordner: " if self.isDir else " Datei: "
        x = x + f"(Len={self.flen}, ModZeit={time.strftime("%Y-%m-%dT%H-%M-%S", self.struzeit)})"
        return x


class backups():    
    def __init__(self, dirObj: dirObjekt, id: int):
        self.dirObj = dirObj
        self.name = dirObj.name
        self.fullPathName = dirObj.fullPathName
        self.id = id
        self.alter_tage = 0
        self.alter_wochen = 0
        self.alter_monate = 0
        self.erhalten = False
        self.erhaltenGrund = ""
        self.datei = dirObj.fullPathName
        self.is_dir = dirObj.isDir
        self.len = dirObj.flen
        self.zeit = dirObj.mtime
        self.struzeit = time.gmtime(self.zeit)
        heute = time.gmtime()
        self.alter_tage = heute.tm_yday - self.struzeit.tm_yday
        self.alter_wochen = self.alter_tage // 7
        # das Monatsalter ab 2000 berechnen
        heutemonate = (heute.tm_year - 2000 - 1) *12 + heute.tm_mon # Anzahl Monate seit 01.2000
        datmonate = (self.struzeit.tm_year - 2000 - 1) *12 + self.struzeit.tm_mon # Anzahl Monate seit 01.2000
        self.alter_monate = heutemonate - datmonate

    def __str__(self):
        x = ""
        if self.datei:
            if self.is_dir:
                x += f"Ordner: "
                # print(f"Ordner: ", end = "")
            else:
                # print(f"Datei: ", end = "")
                x += f"Datei: "
            # print(self.datei)
            x += self.datei + "\n"
            x += f"... Größe: {self.len}\n"
            x += f"... Zeit : {self.struzeit}\n"
            x += f"... Tage   alt: {self.alter_tage}\n"
            x += f"... Wochen alt: {self.alter_wochen}\n"
            x += f"... Monate alt: {self.alter_monate}\n"
        else:
            x = self.name + " is None!"
        return x

def dirInhalt(dir):
    ordner, nam = os.path.split(dir)
    liste = []
    # für jeden Eintrag ein dirObjekt erzeugen
    # und in eine Liste eintragen
    if ("*" or "?") in dir:
        dirLst = Path(ordner).glob(nam)
        for eintrag in dirLst:
            do = dirObjekt(eintrag)
            liste.append(do)
    else:
        with os.scandir(ordner) as it:
            for e in it:
                stat = e.stat()
                do = dirObjekt(e.path, isDir=e.is_dir(), flen=stat.st_size, mTime=stat.st_mtime)
                liste.append(do)
    return liste


def klassifizieren(dirListe, halte_tage, halte_wochen, halte_monate):
    # Aufgabe dieser Funktion ist es, zu entscheiden, welches 
    # dirobj erhalten oder gelöscht werden soll.

    # Indizes aufbauen
    # jeder index enthält den neuesten Eintrag zum gegebenen Zeitraum
    idxMonate = {}
    idxWochen = {}
    for dirobj in dirListe:
        if dirobj.alter_monate > 0:
            if not dirobj.alter_monate in idxMonate:
                idxMonate[dirobj.alter_monate] = dirobj.id
        if dirobj.alter_wochen > 0:
            if not dirobj.alter_wochen in idxWochen:
                idxWochen[dirobj.alter_wochen]= dirobj.id
    if test:
        print(f"{idxMonate=}")
        print(f"{idxWochen=}")

    for dirobj in dirListe:
        if dirobj.alter_tage <= halte_tage:
            dirobj.erhalten = True
            dirobj.erhaltenGrund = "tage," 

        if dirobj.alter_wochen <= halte_wochen:
            try:
                if dirobj.id == idxWochen[dirobj.alter_wochen]:
                    dirobj.erhalten = True
                    dirobj.erhaltenGrund += "wochen," 
            except:
                pass

        if dirobj.alter_monate <= halte_monate:
            try:
                if dirobj.id == idxMonate[dirobj.alter_monate]:                
                    dirobj.erhalten = True
                    dirobj.erhaltenGrund += "monate," 
            except:
                pass


def dokumentieren(dirListe, test=False):
    fn = "aufraeumen_" + time.strftime("%Y-%m-%dT%H-%M-%S") + ".log"
    def ausg(txt):        
        print(txt)
        with open(fn, "a") as f:
            print(txt, file=f)
              
    for obj in dirListe:
        x = f"Index {obj.id}\n"
        if obj.is_dir:
            x += f"Ordner: "            
        else:
            x += f"Datei: "        
        x += obj.datei + "\n"
        if not obj.is_dir:
            x += f"... Size : {obj.len}\n"
        x += f"... Zeit : {obj.struzeit}\n"
        x += f"... Tage   alt: {obj.alter_tage}\n"
        x += f"... Wochen alt: {obj.alter_wochen}\n"
        x += f"... Monate alt: {obj.alter_monate}\n"
        x += f"...   erhalten: {obj.erhalten}\n"
        x += f"...      Grund: {obj.erhaltenGrund}\n"
        # else:
        #     x = obj.dirObj + " is None!"
        ausg(x)

def export_csv(dirliste):
    fn = "aufraeumen_" + time.strftime("%Y-%m-%dT%H-%M-%S") + ".csv"
    with open(fn, "w") as fc:
        print("id,name,dir,y,m,d,tage,wochen,monate,erhalten,grund", file=fc)
        for ob in dirliste:
            print(f"{ob.id},", end="", file=fc)            
            print(f"{ob.dirObj},", end="", file=fc)
            print("dir," if ob.is_dir else ",", end="", file=fc)
            print(f'{ob.struzeit.tm_year},', end="", file=fc)
            print(f'{ob.struzeit.tm_mon},', end="", file=fc)
            print(f'{ob.struzeit.tm_mday},', end="", file=fc)
            print(f'{ob.alter_tage},', end="", file=fc)
            print(f'{ob.alter_wochen},', end="", file=fc)
            print(f'{ob.alter_monate},', end="", file=fc)
            print(f'{ob.erhalten},', end="", file=fc)
            print(f'{ob.erhaltenGrund.replace(","," ")}', file=fc)

def doit(dirliste):
    # führt die eigentliche Bereinigung durch
    #
    global dryrun

    print(f"Ergebnis")
    print("="*80)

    maxlen = 75
    for dirobj in dirliste:
        l = len(dirobj.name)
        if l > 60:
            n = dirobj.name[(l-60):] 
        else:
            n = dirobj.name + " " + "."*(60-l)
        if dirobj.erhalten:
            x = f"{n}" + "."*3 + " bleibt!"            
        else:
            x = f"{n}" + "."*3 
            # pfad = os.path.join(BACKUPORDNER, dirobj.datei)
            pfad = dirobj.fullPathName
            if dryrun:
                x  = x + "WÜRDE entfernt!"
            else:
                if dirobj.is_dir:
                    try:
                        shutil.rmtree(pfad, ignore_errors=False)
                        x = x + " entfernt!"
                    except:
                        x  = x + "entfernen GESCHEITERT!"
                else:
                    try:
                        os.remove(pfad)
                    except:
                        x  = x + "entfernen GESCHEITERT!"
        # x = f"{n}" + "."*3 + (" bleibt!" if dirobj.erhalten else " entfernt!")
        print(x)


def read_dict(dic, key, defaultWert)->int|str:
    # liest den Wert mit swm Schlüssel 'key' aus dem 'dic'
    # falls nicht gefunden, wird der default wert zurückgegeben
    # der Typ der Rückgabe wird vom Typ des Default-Wertes abgelesen
    # kann der Typ nicht konvertiert werden, wird der defaultWert zurückgegeben
    try:
        wert = dic[key]
        if type(defaultWert) is int and not type(wert) is int:
            try:
                wert = int(wert)
            except:
                wert = defaultWert
        elif type(defaultWert) is str and not type(wert) is str:
            try:
                wert = str(wert)
            except:
                wert = defaultWert
    except ValueError:
        wert = defaultWert
    return wert

# ---------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------
if __name__ == "__main__":
    print("="*80)
    print("aufraeumen.py" + " "*48 + version)
    print("="*80)
    print(f"Heute ist {wochentage[heute.tm_wday]}, der {heute.tm_mday}.{heute.tm_mon}., Tag {heute.tm_yday} im Jahr {heute.tm_year}")

    # Kommandzeilen Argumente verarbeiten
    parser = argparse.ArgumentParser(description="Backups nach Alter aufräumen")
    parser.add_argument("-t", "--test", action='store_true', default=False, help="Im Testmodus werden viele zusatzinfos ausgegeben")    
    parser.add_argument("--dryrun", action='store_true', help="Es wird nichts gelöscht, sondern nur so getan, als ob.")
    parser.add_argument("--config", default="aufraeumen.conf", help="Pfad zur Conf-Datei, die den Ablauf steuert")

    args = parser.parse_args()
    ConfDatei = args.config
    test = args.test
    dryrun = args.dryrun
        
    if not os.path.exists(ConfDatei):
        print(f"Die ConfDatei {ConfDatei} fehlt!")
        print("Bitte die Datei [aufraemen.conf] anlegen oder")
        print("einen anderen Namen wählen und als Parameter beim Start mitgeben!\n")
        exit(1)

    # alle conf-Begriffe sind in Kleinbuchstaben!
    config = dotenv_values(ConfDatei)
    BACKUPORDNER = str(read_dict(config, "backupdir", BACKUPORDNER))
    halte_tage = read_dict(config, "tage", halte_tage)
    halte_wochen = read_dict(config, "wochen", halte_wochen)
    halte_monate = read_dict(config, "monate", halte_monate)

    endchar = "\\" if (os.name == "nt") else "/"
    if not BACKUPORDNER.endswith(endchar):
        BACKUPORDNER += endchar
        
    print(f"ZielOrdner ist: {BACKUPORDNER}")
    print(f"Parameter: {halte_tage=}, {halte_wochen=}, {halte_monate=}")
    if dryrun:
        print(">>>> DRY RUN! <<<<")
    if test:
        print(">>>> TEST Modus <<<<")

    dl = dirInhalt(BACKUPORDNER)
    print(f"Anzahl Verzeichnis-Objekte: {len(dl)}\n")

    objListe = []

    i = 0
    for inh in dl:
        i += 1
        ob = backups(inh, id=i)        
        objListe.append(ob)
        # if test:
        #     print(ob)

    # sort nach alter, die neuesten zuerst
    objListe.sort(key=lambda x: x.alter_tage)

    klassifizieren(objListe, halte_tage, halte_wochen, halte_monate)

    if test:
        dokumentieren(objListe)
        export_csv(objListe)

    # zur Tat schreiten ...
    doit(objListe)

