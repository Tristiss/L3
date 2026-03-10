# Python Programme für Paderborner Physik Praktikum (3P) Versuch L3 im GP1c

Dieses Repository beinhaltet alle nötigen Programme zur Messwertaufnahme und Auswertung der Daten für den Praktikumsversuch L3 des Paderborner Physikpraktikums. Dabei wurden die Programme für die Quecksilberdampflampe verwendet. In den Programmen gibt es viele Variablen die jeweils für die verwendete Hardware bzw. Dateipfade angepasst werden müssen.

## Messwertaufnahme
### Requirements
Notwendigen Packages: 
* time
* pandas
* numpy
* threading
* scipy
* tinkerforge
* pynput
* serial

Notwendige Programme:
* Data_Collection (Main Programm)
* Static_Methods_L3

Bei der Messwertaufnahme werden direkt mehrere Messreihen für unterschiedliche Gegenspannungen aufgenommen. In einer Messreihe wird dabei ein linearer Sweep über alle vorgegebenen Beschleunigungsspannungen durchgeführt. Nach einer Messreihe werden die gemessenen Kollektorströme bzw. die zugehörigen Spannungen mit den Beschleunigungsspannungen in eine csv Datei geschrieben.
Sicherheitsmechanismen des Programms:
* Abschaltung durch Esc-Taste möglich (Verbindungen werden ordnungsgemäß getrennt)
* Serielle Befehle werden über das von den Netzteilen gesendete OK bestätigt
* Automatische Abschaltung bei Software Bugs durch try-except Blöcke

**Es muss trotzdem immer auf die Röhre geachtet werden, da eine Chance besteht (vor allem bei zu niedriger Temperatur oder zu hoher Beschleunigungsspannung), dass sich Plasma in der Röhre bildet und sie sich selbst zerstört.**


## Auswertung
### Requirements
Notwendigen Packages: 
* pandas
* numpy
* scipy

Notwendige Programme:
* L3_eval

Das Auswertungsprogramm untersucht vorwiegend den Zusammenhang der Signalstärke und der Sichtbarkeit (Kontrast) des vorletzten Peaks bzw. Valleys, auch wird der Verlauf der beiden Größen bei steigender Gegenspannung untersucht. Die durchschnittliche Anregungsenergie wird ebenfalls aus einem gewichteten Mittelwert über alle gemittelten Anregungsenergiewerte der einzelnen Messreihen berechnet.


## Weitere Anmerkungen
Die MCC-Simulation ist nicht aussagekräftig, da die Konsequenzen eines Stoßes momentan falsch sind (Rutherford-Streuung, Richungsänderung nach inelastischem Stoß, falsche Koordinatentransformation bei Richtungsänderung).
