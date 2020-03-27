"""
CISAC formats, including CWR, use hierarchies of territories.
See included CSV files for details.

They are then combined in different expressions, e.g.

* including World excluding Balkans including Croatia
* including US including Canada

This should make things a bit simpler.

"""

import collections
import csv
import os
from datetime import datetime

dir_path = os.path.dirname(os.path.realpath(__file__))

TERRITORY_LIST_FILE = 'list.csv'
TERRITORY_TREE_FILE = 'tree.csv'


class Territory(object):
    """
    Territory class contains CISAC TIS territories and their relations.

    Please note that variable names correspond to TIS, not the usual ones.
    """

    all_tis_n = collections.OrderedDict()
    all_tis_a = collections.OrderedDict()

    def __init__(self, tis_n, tis_a, tis_a_ext, name, official_name,
            abbreviated_name, typ):
        """

        Args:
            tis_n (str): Numeric code, e.g. 2136 for World, 840 for USA
            tis_a (str): 2 char ISO country codes plus extras, e.g. US, 2WL
            tis_a_ext (str): 2 char ISO country codes, e.g. USA
            name (str): Normal name
            official_name (str): A bit longer name
            abbreviated_name (str): A shorter name
            typ (str): e.g. COUNTRY, GEOGRAPHICAL COUNTRY-GROUP
        """
        self.tis_n = tis_n
        self.tis_a = tis_a
        self.tis_a_ext = tis_a_ext
        self.name = name
        self.official_name = official_name
        self.abbreviated_name = abbreviated_name
        self.type = typ
        self.parent = None
        self.children = set()

        self.all_tis_n[self.tis_n] = self
        self.all_tis_a[self.tis_a] = self
        if self.tis_a_ext:
            self.all_tis_a[self.tis_a_ext] = self

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Territory: {self.name} ({self.type})'

    @property
    def is_world(self):
        return self.tis_n == '2136'

    @property
    def in_world_tree(self):
        return self.is_world or self.parent

    @property
    def is_group(self):
        return bool(self.children)

    @property
    def is_country(self):
        return not self.is_group

    @classmethod
    def get(cls, key):
        """
        Get the territory by one of the keys.

        Args:
            key (str): key value

        Returns:
            Territory
        """
        if not isinstance(key, str):
            raise AttributeError('key must be of type str')
        if key.isnumeric():
            key = key.lstrip('0')
            return cls.all_tis_n.get(key)
        else:
            return cls.all_tis_a.get(key.upper())

    def get_descendants(self, only_countries=False):
        """
        Return all descendants, or all containing countries.

        Args:
            only_countries (bool): Choose if you want only countries to be
            included.

        Returns:
            list of Territory objects

        """
        for child in self.children:
            if child.is_group:
                if not only_countries:
                    yield child
                yield from child.get_descendants(only_countries=only_countries)
            else:
                yield child

    @property
    def descendants(self):
        """
        Return all included territories.

        Returns:
            list of Territory objects
        """
        yield from self.get_descendants()

    @property
    def countries(self):
        """
        Return all included countries.

        Returns:
            list of Territory objects
        """
        yield from self.get_descendants(only_countries=True)

    def get_ascendants(self):
        if self.parent:
            yield self.parent
            yield from self.parent.get_ascendants()

    @property
    def ascendants(self):
        yield from self.get_ascendants()

    def to_dict(self, verbosity=1):
        d = collections.OrderedDict()
        if verbosity >= 1:
            d['name'] = self.name
        d['tis-n'] = self.tis_n
        d['tis-a'] = self.tis_a
        if verbosity >= 1:
            d['type'] = self.type
            if self.children and verbosity >= 2:
                d['included_tis-a_country_codes'] = sorted([
                    t.tis_a for t in self.countries])
        return d


def import_territories():
    """
    Import territories from a CSV file.
    """

    now = datetime.now()
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
            TERRITORY_LIST_FILE)) as list_file:
        reader = csv.reader(list_file)
        next(reader)
        for row in reader:
            (tis_n, exists_from, exists_until, typ, __, tis_a, tis_a_ext,
            name_from, name_until, name, official_name, abbreviated_name,
            __) = row

            frm = datetime.strptime(exists_from, '%d.%m.%Y')
            until = datetime.strptime(exists_until, '%d.%m.%Y')
            frm2 = datetime.strptime(name_from, '%d.%m.%Y')
            until2 = datetime.strptime(name_until, '%d.%m.%Y')
            if not (frm <= now <= until and frm2 <= now <= until2):
                continue

            Territory(tis_n, tis_a, tis_a_ext, name, official_name,
                abbreviated_name, typ)


def import_world_tree():
    """
    Import the territory structure, world-tree only.

    This import is partial, as it allows only the world tree, and what it
    includes.
    """

    now = datetime.now()
    stack = []
    world = False
    with open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
        TERRITORY_TREE_FILE)
    ) as list_file:
        reader = csv.reader(list_file)
        next(reader)
        for row in reader:
            level, tis_n, __, __, typ, __, __, frm, till, __ = row

            frm = datetime.strptime(frm, '%d.%m.%Y') if frm else None
            till = datetime.strptime(till, '%d.%m.%Y') if till else None
            if frm and till and not frm <= now <= till:
                continue

            territory = Territory.get(tis_n)

            # World section is special
            if territory.is_world:
                world = True
                stack = []
            elif level == '1':
                world = False

            if not world:
                continue

            if stack:

                # if this is a new branch, remove the garbage from the stack
                while stack[-1][0] >= level:
                    stack.pop(-1)

                parent = stack[-1][1]
                assert (territory.parent is None)
                territory.parent = parent
                parent.children.add(territory)

            stack.append((level, territory))


def add_child_to_stack(stack, territory):
    for __, t in stack:
        t.children.add(territory)


def reduce_stack_to_level(stack, level):
    if stack:
        while stack[-1][0] >= level:
            stack.pop(-1)
    return stack


def process_reader(reader):
    now = datetime.now()
    stack = []
    world = False
    for row in reader:
        level, tis_n, __, __, typ, __, __, frm, till, __ = row

        frm = datetime.strptime(frm, '%d.%m.%Y') if frm else None
        till = datetime.strptime(till, '%d.%m.%Y') if till else None
        if frm and till and not frm <= now <= till:
            continue

        territory = Territory.get(tis_n)

        if territory.is_world:
            world = True
            stack = []
            continue
        elif level == '1':
            world = False
            stack = []
        elif territory.parent and typ != 'COUNTRY':
            world = True

        if world:
            continue

        stack = reduce_stack_to_level(stack, level)

        if typ != 'COUNTRY':
            stack.append((level, territory))
        else:
            add_child_to_stack(stack, territory)


def import_other_structure():
    """
    Import the territory structure.

    This is the second part of the import, where everything in the world-tree
    is ignored.
    """

    with open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
        TERRITORY_TREE_FILE)
    ) as list_file:
        reader = csv.reader(list_file)
        next(reader)
        process_reader(reader)


import_territories()
import_world_tree()
import_other_structure()
