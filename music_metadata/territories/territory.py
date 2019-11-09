from datetime import datetime
import csv
import os
import collections


dir_path = os.path.dirname(os.path.realpath(__file__))


TERRITORY_LIST_FILE = 'list.csv'
TERRITORY_TREE_FILE = 'tree.csv'


class Territory(object):

    all_tis_n = collections.OrderedDict()
    all_tis_a = collections.OrderedDict()
    all_tis_a_ext = collections.OrderedDict()

    def __init__(self, tis_n, tis_a, tis_a_ext, name, official_name, abbreviated_name, typ):
        self.tis_n = tis_n
        self.tis_a = tis_a
        self.tis_a_ext = tis_a_ext
        self.name = name
        self.official_name = official_name
        self.abbreviated_name = abbreviated_name
        self.type = typ
        self.parent = None
        self.children = set()

        self.__class__.all_tis_n[self.tis_n] = self
        self.__class__.all_tis_a[self.tis_a] = self
        self.__class__.all_tis_a_ext[self.tis_a_ext] = self

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @classmethod
    def get(cls, key, key_type='tis_n'):
        if not isinstance(key, str):
            raise AttributeError('key must be of type str')
        if key_type == 'tis_n':
            key = key.lstrip('0')
            return cls.all_tis_n.get(key)
        raise AttributeError('Key {key_type} not allowed.')

    def get_descendants(self, only_countries=False):
        for child in self.children:
            if child.children:
                if not only_countries:
                    yield child
                yield from child.descendants
            else:
                yield child

    @property
    def descendants(self):
        yield from self.get_descendants()

    @property
    def countries(self):
        yield from self.get_descendants(only_countries=True)


def import_territories():
    now = datetime.now()
    with open(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                TERRITORY_LIST_FILE
            )) as list_file:
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

            Territory(
                tis_n, tis_a, tis_a_ext, name, official_name, abbreviated_name,
                typ)


def import_structure():
    now = datetime.now()
    stack = []
    with open(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                TERRITORY_TREE_FILE
            )) as list_file:
        reader = csv.reader(list_file)
        next(reader)
        world = False
        for row in reader:
            level, tis_n, __, __, typ, __, __, frm, till, __ = row

            frm = datetime.strptime(frm, '%d.%m.%Y') if frm else None
            till = datetime.strptime(till, '%d.%m.%Y') if till else None
            if frm and till and not frm <= now <= till:
                continue

            territory = Territory.get(tis_n)

            # World section is special
            if tis_n == '2136':
                world = True
            elif level == '1':
                world = False

            if level == '1':
                stack = []  # Reset the stack
                # Included through World
                if not world and typ == 'GEOGRAPHICAL COUNTRY-GROUP':
                    continue
            elif stack == []:  # And the children
                continue
            elif not world and typ != 'COUNTRY': # Only Worldtree allowed
                continue


            if stack and world:
                while stack[-1][0] >= level:
                    stack.pop(-1)
                parent = stack[-1][1]
                territory.parent = parent
            elif stack:
                stack = [stack[0]]
                parent = stack[0][1]
            else:
                parent = None

            if parent:
                parent.children.add(territory)

            stack.append((level, territory))


import_territories()
import_structure()