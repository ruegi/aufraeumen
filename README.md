# aufraeumen
## Ein Programm, um das Volumen eines Backup-Ordners im Zaum zu halten
### Das Problem und seine Lösung:
Ein Programm hatte Kalender- und Adressbuch aus Nextcloud jeden Tag in einen eigenen Unterordner eines 
Backup-Ordners gespeichert.
Mit der Zeit wurde dieser Backup-Ordner sehr voll.
Dieses Programm erlaubt es, den Ordner zu bereinigen.
Es behält die SIcherungen der letzten x Tage, die jeweils letzten Sicherungen der letzten y Wochen und die jeweils letzten Sicherungen der letzten z Monate und schreibt sein Protokoll nach stdout.

### Konfiguration
Das Programm wird durch eine conf-Datei gesteuert, per default nimmt es die Start-Ordner liegende **aufraeumen.conf**.

#### Ein Beispiel für den Inhalt:
```
backupdir=/home/rg/calcardbackup/
tage=7
wochen=3
monate=4
```
Die Bedeutung der Einträge sollte selbsterklärend sein.

### Abhängigkeit
Die App benötigt das Modul **dotenv**


rg, 2026-10-20

