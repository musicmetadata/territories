# Music Metadata - Territories

[![Build Status](https://travis-ci.com/musicmetadata/territories.svg?branch=master)](https://travis-ci.com/musicmetadata/territories)
[![Coverage Status](https://coveralls.io/repos/github/musicmetadata/territories/badge.svg?branch=master)](https://coveralls.io/github/musicmetadata/territories?branch=master)
![GitHub](https://img.shields.io/github/license/musicmetadata/territories)
![PyPI](https://img.shields.io/pypi/v/music-metadata-territories)

A simple library for dealing with territory hierarchies used in music 
metadata, currently primarily focused on CISAC TIS.

Conversion between TIS and ISO (DDEX!) territories will follow in the next release.

## Classes

It has only two classes:

* `Territory` - the territory, e.g. World, Europe, Croatia
* `TerritoryList` - this class makes including and excluding territories 
simpler, it also splits territories down when needed

### Territory manipulation

World excluding USA results in a minimal list of included territories:

```python
from music_metadata.territories.territory import Territory
from music_metadata.territories.territory_list import TerritoryList

world = Territory.get('2136')
usa = Territory.get('US')

l = TerritoryList()
l.include(world)
l.exclude(usa)

for t in sorted(l, key=lambda x: x.name):
    print(f'{t.tis_n:0>4}', t.name)
```

Result:

```
2100 AFRICA
2106 ASIA
0124 CANADA
2113 CENTRAL AMERICA
2120 EUROPE
0484 MEXICO
2130 OCEANIA
2132 SOUTH AMERICA
2134 WEST INDIES
```

It is simple to list all the countries as well:

```python
for t in sorted(l.countries, key=lambda x: x.name):
    print(f'{t.tis_a:0>4}', t.name)
```

Result:

```
AF AFGHANISTAN
AL ALBANIA
DZ ALGERIA
AD ANDORRA
AO ANGOLA
AG ANTIGUA AND BARBUDA
AR ARGENTINA
AM ARMENIA
AU AUSTRALIA
AT AUSTRIA
...
```

One can check if a country is finally included in the list:

```python
usa in l
```

```Result:
False
```

### Share manipulation

Share calculations are also possible, by using a second argument to 
``TerritoryList.include`` and ``TerritoryList.add``. This second argument can
be any objects that allows adding. 

```python
from music_metadata.territories.territory import Territory
from music_metadata.territories.territory_list import TerritoryList

world = Territory.get('2136')
usa = Territory.get('US')
canada = Territory.get('CA')

l = TerritoryList()
l.include(world, 25)
l.add(usa, 25)
```

So, we there is 25 for the whole world and additional 25 for the US.
If we ask for values for the US and Canada:

```python
l[usa], l[canada]
```

We get 50 for the US and 25 for Canada.

```Result:
(50, 25)
```

Any numeric type will work out of the box,
custom ``__add__`` method might be required for complex objects. Here is
an example for a list of numeric fields:

```python
class Shares(list):
    def __add__(self, other):
        return Shares([self[i] + other[i] for i in range(len(self))])   
```

You may test it online, no coding skills required: https://music-metadata.herokuapp.com/territories/

The code for the demo is here: https://github.com/musicmetadata/web-wrapper
