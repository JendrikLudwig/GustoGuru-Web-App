
# GustoGuru Webanwendung

Dieser Webanwendung wurde für ein Projekt im Modul "Fortgeschrittene Programmierung" des Studiengangs "Digital Reality" der HAW Hamburg entwickelt.

Sie implementiert eine Nutzeranwendung, in Form einer Flask API. Die Anwendung ermöglicht dem Nutzer die Generierung eines Rezeptes, auf basis von selbst gewählten Zutaten.


## WICHTIG
Zur Nutzung der Anwendung ist das herunterladen der Rezeptdaten erforderlich. Hierfür einfach die [Daten herunterladen]("https://1drv.ms/f/s!AkZiqagXI1TMm8MBBKWjgbtWf5QbOA?e=q3k3ix") und in einen "data"-Ordner auf Root-Ebene ziehen. 
## Ordnerstruktur

```
Web-App
|
├── data/                       # Rezeptdaten (Müssen selbst heruntergeladen werden s.O.)
├── python/                     # Enthält alle für das Backend relevanten Skripte (neben app.py)
├── static/                     # Statische Datein für das Webfrontend (CSS, JavaScript, Bilder)
├── templates/                  # Templates für das Serverseitige Webseiten Rendering
└── app.py                      # Hauptprogramm mit Server und Endpunktdefinitionen

```