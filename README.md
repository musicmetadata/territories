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

world = Territory.get('2136')
croatia = Territory.get('191')

l = TerritoryList()
l.include(world)
l.exclude(croatia)

for t in sorted(l, key=lambda x: x.tis_a):
    print(f'{t.tis_n:0>4}', t.name)
```

Result:

```
2100 AFRICA
2101 AMERICA
2106 ASIA
2111 BRITISH ISLES
2119 EASTERN EUROPE
2130 OCEANIA
2131 SCANDINAVIA
0020 ANDORRA
0040 AUSTRIA
0070 BOSNIA AND HERZEGOVINA
0056 BELGIUM
0756 SWITZERLAND
0276 GERMANY
0724 SPAIN
0246 FINLAND
0250 FRANCE
0300 GREECE
0352 ICELAND
0380 ITALY
0438 LIECHTENSTEIN
0442 LUXEMBOURG
0492 MONACO
0499 MONTENEGRO
0807 MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF
0470 MALTA
0528 NETHERLANDS
0620 PORTUGAL
0688 SERBIA
0705 SLOVENIA
0674 SAN MARINO
0336 HOLY SEE (VATICAN CITY STATE)
```
