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

for t in l:
    print(t)
```

Result:

```
ASIA
AFRICA
OCEANIA
AMERICA
ICELAND
BRITISH ISLES
MALTA
SAN MARINO
GERMANY
MONTENEGRO
SPAIN
SWITZERLAND
PORTUGAL
NETHERLANDS
AUSTRIA
BELGIUM
ANDORRA
LIECHTENSTEIN
SLOVENIA
EASTERN EUROPE
GREECE
ITALY
MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF
HOLY SEE (VATICAN CITY STATE)
MONACO
SERBIA
SCANDINAVIA
FINLAND
LUXEMBOURG
FRANCE
BOSNIA AND HERZEGOVINA
```
