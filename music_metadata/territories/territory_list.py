"""
CISAC formats, including CWR, use hierarchies of territories.

The functionality coded here makes the inclusions/exclusions simpler.

"""

import collections


class TerritoryList(collections.OrderedDict):

    def include(self, territory, obj=None):
        """
        Include a territory with it's data to the list.

        Args:
            territory (Territory): territory object to be included
            obj (any): Any object, used in code that uses this functionality
        """

        if territory in self:
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

        # Let's try the trivial version
        if territory in self:
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
            if t in self:
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

        # Territory already present as is, just add
        if territory in self:
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

        # Then try including the new territory, and add if already in there
        try:
            self.include(territory, obj)
        except ValueError:
            for t in territory.children:
                self.add(t, obj)

    @property
    def countries(self):
        countries = collections.OrderedDict()
        for territory, obj in self.items():
            if territory.is_country:
                countries[territory] = obj
            else:
                for country in territory.countries:
                    countries[country] = obj
        return countries

