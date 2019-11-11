# Music Metadata - Territories

A very simple library for dealing with territory hierarchies used in music 
metadata, currently primarily focused on CISAC TIS.

It loads the territories and hierarchies from CSV files, made from Excel
files downloaded from CISAC documents.

One of the most importaint features is that it turns any combination of
includes and excludes into a include-only list.

It has only two classes:

* `Territory` - the territory, e.g. World, Europe, Croatia
* `TerritoryList` - this class makes including and excluding territories 
simpler, it also splits territories down when needed, e.g. World excluding 
Croatia results in a minimal list of included territories, and not all the
countries:

```python
from music_metadata.territories import *

# 
world = Territory.get('2136')
croatia = Territory.get('191')

l = TerritoryList()
l.include(world)
l.exclude(croatia)

for t in sorted(l, key=lambda x: x.name):
    print(f'{t.tis_n:0>4}', t.name)
```

Result:

```
2100 AFRICA
2101 AMERICA
0020 ANDORRA
2106 ASIA
0040 AUSTRIA
0056 BELGIUM
0070 BOSNIA AND HERZEGOVINA
2111 BRITISH ISLES
2119 EASTERN EUROPE
0246 FINLAND
0250 FRANCE
0276 GERMANY
0300 GREECE
0336 HOLY SEE (VATICAN CITY STATE)
0352 ICELAND
0380 ITALY
0438 LIECHTENSTEIN
0442 LUXEMBOURG
0807 MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF
0470 MALTA
0492 MONACO
0499 MONTENEGRO
0528 NETHERLANDS
2130 OCEANIA
0620 PORTUGAL
0674 SAN MARINO
2131 SCANDINAVIA
0688 SERBIA
0705 SLOVENIA
0724 SPAIN
0756 SWITZERLAND
```
