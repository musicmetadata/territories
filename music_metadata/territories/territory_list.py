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
        Include a territory with it's data to the list.

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

    def add(self, territory, obj=None):
        """
        Include a territory with it's data to the list or add data to existing.

        Args:
            territory (Territory): territory object to be included
            obj (any): Any object, used in code that uses this functionality
        """

        territory = self._clean_territory(territory)

        # Territory already present as is, just add
        if territory in self.keys():
            self[territory] = self[territory] + obj
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
                new_obj = self[t] + obj
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
                for subterritory in territory.descendants:
                    if (subterritory, obj) in ascendants.keys():
                        solved.add(subterritory)
