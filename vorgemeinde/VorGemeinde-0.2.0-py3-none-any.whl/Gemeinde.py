import csv
import random

Gemeindelist = ["Alberschwende","Altach","Altenstadt","Andelsbuch","Au","Bartholomäberg","Bezau","Bildstein","Bizau","Bludenz","Buch","Bürs","Bürserberg","Dalaas","Damüls","Doren","Dornbirn","Düns","Dünserberg","Egg","Eichenberg","Feldkirch","Fontanelle","Frastanz","Fraxern","Fußach","Gaißau","Gaschurn","Göfis","Götzis","Hard","Hittisau","Höchst","Hörbranz","Hohenems","Hohenweiler","Innerbraz","Kennelbach","Klaus","Klösterle","Koblach","Krumbach","Langen bei Bregenz","Langenegg","Laterns","Lauterach","Lech","Lingenau","Lochau","Lorüns","Ludesch","Lustenau","Mäder","Meinigen","Mellau","Mittelberg","Möggers","Nenzing","Nüziders","Raggal","Rankweil","Reuthe","Riefensberg","Röns","Röthis","Satteins","Schlins","Schnepfau","Schnifis","Schoppernau","Schröcken","Schruns","Schruns","Schwarzach","Schwarzenberg","Sibratsgfäll","Silbertal","Sonntag","St. Anton im Montafon", "St. Gallenkirch","St. Gerold", "Stallehr", "Sulz", "Sulzberg","Thüringerberg","Tschagguns","Übersaxen","Vandans","Viktorsberg","Warth","Weiler","Wolfurt","Zwischenwasser"]

def randomGemeinde():
    return Gemeindelist[random.randint(0,96)]