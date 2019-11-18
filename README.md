# Music Metadata - Territories

[![Build Status](https://travis-ci.com/musicmetadata/territories.svg?branch=master)](https://travis-ci.com/musicmetadata/territories)
[![Coverage Status](https://coveralls.io/repos/github/musicmetadata/territories/badge.svg?branch=master)](https://coveralls.io/github/musicmetadata/territories?branch=master)
![GitHub](https://img.shields.io/github/license/musicmetadata/territories)
![PyPI](https://img.shields.io/pypi/v/music-metadata-territories)

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
