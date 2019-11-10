# Music Metadata - Territories

A very simple library for dealing with territory hierarchies used in music 
metadata, currently primarily focused on CISAC TIS.

It loads the territories and hierarchies from CSV files, made from Excel
files downloaded from CISAC documents.

It has only two classes:

* `Territory` - the territory, e.g. World, Europe, Croatia
* `TerritoryList` - this class makes including and excluding territories 
simpler, it also splits territories down when needed, e.g. World excluding 
Croatia results in a minimal list of included territories

See the tests for usage details. 

