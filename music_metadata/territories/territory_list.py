"""
CISAC formats, including CWR, use hierarchies of territories.

The functionality coded here makes the inclusions/exclusions simpler.

"""

import collections
from .territory import Territory
from collections import OrderedDict, defaultdict


class TerritoryList(collections.OrderedDict):
    """Ordered dictionary with Territory objects as keys and any object,
    including None, as value."""

    @staticmethod
    def _clean_territory(territory):
        if isinstance(territory, Territory):
            return territory
        if isinstance(territory, str):
            return Territory.get(territory)
        raise ValueError('Territory must be a Territory or a str.')

    def __contains__(self, territory):
        territory = self._clean_territory(territory)
        if super().__contains__(territory):
            return True
        if any([territory in t.descendants for t in self.keys()]):
            return True
        return False

    def include(self, territory, obj=None):
        """
        Include a territory with its data to the list.

        Args:
            territory (Territory): territory object to be included
            obj (any): Any object, used in code that uses this functionality
        """

        territory = self._clean_territory(territory)

        if territory in self.keys():
            raise ValueError(
                f'Territory {territory} is already directly included.')

        if territory.children and not territory.in_world_tree:
            # This is some group not in the world tree:
            for t in territory.children:
                self.include(t, obj)
            return

        for t in self:
            if territory in t.descendants:
                raise ValueError(
                    f'Territory {territory} is already included through '
                    f'{t}.')

        for t in self:
            if territory in t.ascendants:
                raise ValueError(
                    f'Territory {territory} already contains '
                    f'{t}.')

        self[territory] = obj

    def exclude(self, territory):
        """
        Smartly exclude the territory from the list

        Args:
            territory (Territory): territory object to be excluded
        """

        territory = self._clean_territory(territory)

        # Let's try the trivial version
        if territory in self.keys():
            del self[territory]
            return

        # If it is some non-world-tree group, we must exclude each country
        if not territory.in_world_tree:
            for t in territory.children:
                self.exclude(t)
            return

        # Ok, so we must now do some calculations, lets create the stack
        stack = []
        for t in territory.ascendants:
            stack.append(t)
            if t in self.keys():
                break
        else:
            raise ValueError(
                f'Territory {territory} is not included, '
                'so can not be excluded.')

        # we remove the top level and add everything below the stack element,
        # except elements in stack and the removed territory
        top_level = stack[-1]
        obj = self[top_level]
        del self[top_level]
        for parent in reversed(stack):
            for t in parent.children:
                if t not in stack and t != territory:
                    self.include(t, obj)

    def _add_values(self, held, obj, territory):
        """
        Combine the value this list holds with the one being added.

        add() is arithmetic, so the two values have to add to each other and
        that addition is what decides. There is no separate rule about None:
        None adds to nothing, so a None anywhere in the pair fails here the
        same way a list of fields meeting a bare int would. Catching the
        TypeError keeps the failure a ValueError naming the territory, rather
        than an unsupported operand pair from the middle of this module.

        Args:
            held (any): the value already in the list
            obj (any): the value being added
            territory (Territory): for the error message

        Returns:
            any: the combined value

        """
        try:
            return held + obj
        except TypeError as e:
            raise ValueError(
                f'add() was given {obj!r} as its second argument, which can '
                f'not be added to the {held!r} this list holds for territory '
                f'{territory}. The values in a list have to add to each '
                f'other: a list built with add() carries values, and they '
                f'accumulate, while a list built with include() carries '
                f'None, and None adds to nothing.'
            ) from e

    def add(self, territory, obj):
        """
        Add a territory with its data, accumulating onto what is there.

        obj is required. add() exists to add a value to a value, and with
        obj defaulting to None a bare add(x) said nothing about which of the
        two it was: on a fresh list it quietly stored None, and on a
        territory already in the list it was None + None - a TypeError
        raised from inside this module for a condition include() already
        describes. Required, the call is refused at the call site instead,
        where the caller can see it. Use include(x) to add a territory with
        no value.

        Args:
            territory (Territory): territory object to be included
            obj (any): the value to add; it must add to what the list holds

        """

        territory = self._clean_territory(territory)

        # Territory already present as is, just add
        if territory in self.keys():
            self[territory] = self._add_values(
                self[territory], obj, territory)
            return

        # Territory is not in world tree, e.g. Balkans, add all children
        if not territory.in_world_tree:
            for t in territory.children:
                self.add(t, obj)
            return

        # If none of the above, splitting is necessary, so first split
        # the appropriate children territories
        keys = list(self.keys())
        for t in keys:
            if territory in t.descendants:
                new_obj = self._add_values(self[t], obj, t)
                self.exclude(territory)
                self.include(territory, new_obj)
                return

        # Then try including the new territory, and add if already in there
        try:
            self.include(territory, obj)
        except ValueError:
            for t in territory.children:
                self.add(t, obj)

    @property
    def countries(self):
        countries = TerritoryList()
        for territory, obj in self.items():
            if territory.is_country:
                countries[territory] = obj
            else:
                for country in territory.countries:
                    countries[country] = obj
        return countries

    def compress(self):
        if len(self) <= 1:
            return
        ascendants = defaultdict(int)
        for country, obj in self.countries.items():
            for t in country.ascendants:
                ascendants[(t, obj)] += 1
        ascendants = OrderedDict(
            sorted(ascendants.items(), key=lambda x: x[1], reverse=True))
        solved = set()
        for (territory, obj), count in ascendants.items():
            if territory in solved:
                continue
            if len(list(territory.countries)) == count:
                for country in territory.countries:
                    self.exclude(country)
                self.include(territory, obj)
                for sub_territory in territory.descendants:
                    if (sub_territory, obj) in ascendants.keys():
                        solved.add(sub_territory)
