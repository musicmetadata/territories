# Music Metadata - Territories

[![Build Status](https://travis-ci.com/musicmetadata/territories.svg?branch=master)](https://travis-ci.com/musicmetadata/territories)
[![Coverage Status](https://coveralls.io/repos/github/musicmetadata/territories/badge.svg?branch=master)](https://coveralls.io/github/musicmetadata/territories?branch=master)
![GitHub](https://img.shields.io/github/license/musicmetadata/territories)
![PyPI](https://img.shields.io/pypi/v/music-metadata-territories)

A simple library for dealing with territory hierarchies used in music 
metadata, currently primarily focused on CISAC TIS.

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
The shorter version also works, yielding same results: 
```python
from music_metadata.territories.territory_list import TerritoryList

l = TerritoryList()
l.include('2136')  # WORLD
l.exclude('US')  # USA

for t in sorted(l, key=lambda x: x.name):
    print(f'{t.tis_n:0>4}', t.name)
```

One can check if a country is finally included in the list:

```python
usa in l
```

```Result:
False
```

Works also with territories deeper in the structure, also with codes:

```python
'hr' in l
```

```Result:
True
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

## Compressing output

Long lists can be trimmed, both if they have values and if they do not.
Only territories with the same object will be compressed. Consider this:

```python
from music_metadata.territories.territory_list import TerritoryList

l = TerritoryList()
l.include('2136', 25)
l.exclude('HR')
l.add('US', 25)  # US is now at 50
l.include('HR', 25)  # same as it used to be

for t, v in l.items():
    print(f'{t.name}: {v}')
```

```Result:
ASIA: 25
OCEANIA: 25
AFRICA: 25
MALTA: 25
ICELAND: 25
... 30 territories cut out ...
MEXICO: 25
UNITED STATES: 50
CROATIA: 25
```

But, if we compress:

```python
l.compress()

for t, v in l.items():
    print(f'{t.name}: {v}')
```

```Result:
CANADA: 25
MEXICO: 25
UNITED STATES: 50
AFRICA: 25
ASIA: 25
EUROPE: 25
OCEANIA: 25
WEST INDIES: 25
SOUTH AMERICA: 25
CENTRAL AMERICA: 25
```
## Demo
Available as utility in free online [CWR.tools](<https://cwr.tools>).

Similar utility is part of 
[Web Wrapper for Music Metadata Python Libraries](https://github.com/musicmetadata/web-wrapper),
but you need to deploy it yourself. Deployment to Heroku is fully automated.