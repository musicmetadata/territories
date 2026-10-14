import unittest

from music_metadata.territories.territory import Territory
from music_metadata.territories.territory_list import TerritoryList


class TestTerritory(unittest.TestCase):

    # noinspection PyTypeChecker
    def test_relations(self):
        """
        Test basic relations between hand-picked objects.
        """

        with self.assertRaises(AttributeError):
            Territory.get(2136)

        world = Territory.get('2136')
        self.assertEqual(str(world), 'WORLD')
        self.assertEqual(
            repr(world),
            'Territory: WORLD (GLG)')
        self.assertEqual(len(world.children), 5)
        self.assertIsNone(world.parent)
        d = world.to_dict(1)
        self.assertEqual(d['name'], 'WORLD')
        self.assertEqual(d['tis-n'], '2136')
        self.assertEqual(d['tis-a'], '2WL')
        self.assertIsNot('included_tis-a_country_codes', d)

        europe = Territory.get('2120')
        self.assertEqual(europe.parent, world)
        self.assertIn(europe, world.descendants)
        self.assertNotIn(europe, world.countries)
        d = europe.to_dict(2)
        self.assertEqual(d['name'], 'EUROPE')
        self.assertEqual(d['tis-n'], '2120')
        self.assertEqual(d['tis-a'], '2EU')
        codes = d['included_tis-a_country_codes']
        self.assertIn('HR', codes)

        croatia = Territory.get('HR')
        self.assertNotIn(croatia, europe.children)
        self.assertIn(croatia, europe.descendants)
        self.assertIn(croatia, europe.countries)
        self.assertIn(croatia, world.countries)
        d = croatia.to_dict(1)
        self.assertEqual(d['name'], 'CROATIA')
        self.assertEqual(d['tis-n'], '191')
        self.assertEqual(d['tis-a'], 'HR')

        cat = Territory.get('2115')
        self.assertNotIn(croatia, cat.descendants)
        self.assertNotIn(cat, world.descendants)
        self.assertEqual(list(cat.children), list(cat.descendants))
        self.assertEqual(list(cat.children), list(cat.countries))

        for c in cat.countries:
            self.assertIn(c, world.countries)


class TestTerritoryList(unittest.TestCase):

    def test_add_requires_a_value(self):
        """add() is arithmetic, so it needs something to add.

        With obj defaulted to None, add(x) was a call with no meaning: on a
        fresh list it silently stored None, and on a territory already in
        the list it was None + None - a TypeError naming nothing, raised
        from inside this module. Making the argument required refuses the
        call at the call site instead, where the caller can see it.

        The fix for a caller that wanted a plain include is include(x),
        which was always the right method and still raises the named
        errors.
        """
        territory_list = TerritoryList()
        usa = Territory.get('840')

        with self.assertRaises(TypeError) as caught:
            territory_list.add(usa)
        self.assertIn('obj', str(caught.exception))

        # and on a list that already holds it, where it used to be
        # None + None rather than a missing-argument error
        territory_list.add(usa, 10)
        with self.assertRaises(TypeError):
            territory_list.add(usa)

    def test_add_refuses_none_explicitly(self):
        """None is not a value, so passing it is the same mistake."""
        territory_list = TerritoryList()
        usa = Territory.get('840')
        territory_list.add(usa, 10)

        with self.assertRaises(ValueError) as caught:
            territory_list.add(usa, None)
        self.assertIn('None', str(caught.exception))

        # unchanged by the refusal
        self.assertEqual(territory_list[usa], 10)

    def test_adding_a_value_onto_a_none_value_raises(self):
        """include() stores None, so a list can hold no data at all.

        That list and a value have nothing to combine, so this is refused
        by name. It is the likeliest of the three to be met, because
        include() is the default obj and add() is the natural next call.
        """
        territory_list = TerritoryList()
        territory_list.include(Territory.get('2120'))  # Europe, value None
        self.assertEqual(list(territory_list.values()), [None])

        with self.assertRaises(ValueError) as caught:
            territory_list.add(Territory.get('276'), 25)  # Germany, inside
        self.assertIn('None', str(caught.exception))

        # add(x, 0) fails too - there is no value that happens to work
        with self.assertRaises(ValueError):
            territory_list.add(Territory.get('276'), 0)

    def test_the_split_refuses_a_none_value_too(self):
        """The second accumulation site, which the check must also cover:
        adding a container whose held value is None reaches the split."""
        territory_list = TerritoryList()
        territory_list.include(Territory.get('2120'))  # Europe, value None

        with self.assertRaises(ValueError):
            territory_list.add(Territory.get('2136'), 25)  # World contains it

    def test_include_still_takes_no_value(self):
        """The asymmetry is the point: include() is a set operation and
        None is a legitimate thing to store, add() is arithmetic and is not.
        """
        territory_list = TerritoryList()
        territory_list.include(Territory.get('840'))

        self.assertEqual(list(territory_list.values()), [None])
        self.assertIn(Territory.get('840'), territory_list)

    def test_add_still_accumulates_when_there_is_an_obj(self):
        """The documented behaviour, unchanged: the accumulation is the
        point of add() and must survive the signature change."""
        territory_list = TerritoryList()
        territory_list.add('2136', 10)
        territory_list.add('191', 10)  # Croatia
        self.assertEqual(territory_list[Territory.get('191')], 20)
        territory_list.add('191', 10)
        self.assertEqual(territory_list[Territory.get('191')], 30)

    def test_add_with_an_obj_still_splits_a_containing_territory(self):
        """Europe added after Croatia must fold Croatia up into it, keeping
        the accumulated value.

        40, not 50: Europe's 10 lands on Croatia as well, so Croatia has its
        own 30 plus 10 more, and Europe keeps a separate 10. That is the
        semantics the existing test_world pins at its last lines.
        """
        territory_list = TerritoryList()
        territory_list.add('2136', 10)
        territory_list.add('191', 10)  # Croatia
        territory_list.add('191', 10)
        territory_list.add('2120', 10)  # Europe, contains Croatia

        self.assertEqual(territory_list[Territory.get('191')], 40)
        # Croatia stays a direct key: exclude() splits the territory that
        # contains it, not the territory being added, so only World is
        # re-bucketed around Europe. The value moved, the key did not go.

    def test_a_split_succeeds_and_keeps_the_accumulated_value(self):
        """Adding a territory that contains a present one splits it rather
        than failing - the documented behaviour, pinned here because the
        fix touches this branch and must not have changed it.

        World over Europe(10) with 25 more: Europe's 10 and World's 25 both
        land on it, so Europe is 35. World is not a key afterwards, because
        exclude() pulls it apart before it is re-added - it becomes its own
        children carrying 25 each, except Europe which kept the accumulation.
        """
        world = Territory.get('2136')
        europe = Territory.get('2120')
        territory_list = TerritoryList()
        territory_list.add(europe, 10)
        territory_list.add(world, 25)

        self.assertEqual(territory_list[europe], 35)
        self.assertNotIn(world, territory_list)
        for child in world.children:
            expected = 35 if child == europe else 25
            self.assertEqual(territory_list[child], expected)

    def test_overlap_across_a_non_world_tree_group_still_raises(self):
        """NAFTA has no ascendants, so an upward walk never reaches the USA
        through it - include() finds it only by expanding the group.

        The duplicate branch is reached because the expansion puts the USA
        in as a direct key, so the error is the named one and the list is
        not left half-built.
        """
        territory_list = TerritoryList()
        territory_list.include(Territory.get('2126'))  # NAFTA
        self.assertIn(Territory.get('840'), territory_list)

        with self.assertRaises(ValueError) as caught:
            territory_list.include(Territory.get('840'))
        self.assertIn('already directly included', str(caught.exception))

    def test_world(self):
        """
        Test basic includes/excludes
        """

        world = Territory.get('2136')
        balkans = Territory.get('2108')
        germany = Territory.get('DE')
        croatia = Territory.get('HR')
        slovenia = Territory.get('705')
        europe = Territory.get('2120')
        cat = Territory.get('2115')
        usa = Territory.get('0840')
        asia = Territory.get('2AS')

        # World excluding Croatia includes Slovenia
        territory_list = TerritoryList()
        territory_list.include(world)
        territory_list.exclude('hr')
        self.assertIn(slovenia, territory_list)
        self.assertIn(slovenia, territory_list.countries)
        self.assertIn(slovenia, territory_list.keys())

        # Balkans includes Slovenia
        territory_list = TerritoryList()
        territory_list.include(balkans)
        self.assertIn(slovenia, territory_list)
        self.assertIn(slovenia, territory_list.countries)
        self.assertIn(slovenia, territory_list.keys())

        # World excluding Balkans does not include Slovenia
        territory_list = TerritoryList()
        territory_list.include(world)
        territory_list.exclude(balkans)
        self.assertNotIn(slovenia, territory_list)
        self.assertNotIn(slovenia, territory_list.countries)
        self.assertNotIn(slovenia, territory_list.keys())

        # World including Croatia raises errors
        # (Croatia is part of the World)
        territory_list = TerritoryList()
        territory_list.include(world)
        with self.assertRaises(ValueError):
            territory_list.include('192')

        # Slovenia including World raises an error
        territory_list = TerritoryList()
        territory_list.include(slovenia)
        with self.assertRaises(ValueError):
            territory_list.include(world)

        # World including Europe raises an error
        territory_list = TerritoryList()
        territory_list.include(world)
        with self.assertRaises(ValueError):
            territory_list.include(europe)

        # World including Commonwealth of African territories raises an error
        territory_list = TerritoryList()
        territory_list.include(world)
        with self.assertRaises(ValueError):
            territory_list.include(cat)

        # World excluding Europe including Balkans includes Slovenia
        territory_list = TerritoryList()
        territory_list.include(world)
        territory_list.exclude(europe)
        territory_list.include(balkans)
        self.assertIn(slovenia, territory_list)
        self.assertIn(slovenia, territory_list.countries)
        self.assertIn(slovenia, territory_list.keys())

        # World excluding US includes Slovenia, but not in keys
        territory_list = TerritoryList()
        territory_list.include('2136')
        territory_list.exclude('840')
        self.assertIn(slovenia, territory_list)
        self.assertIn(slovenia, territory_list.countries)
        self.assertNotIn(slovenia, territory_list.keys())

        # Simple share manipulations
        territory_list = TerritoryList()
        territory_list.include(world, '50%')
        territory_list.exclude(europe)
        territory_list.include('hr', '25%')
        self.assertIn('25%', territory_list.values())
        self.assertIn((croatia, '25%'), territory_list.items())
        self.assertEqual(len(territory_list), 5)

        with self.assertRaises(ValueError):
            territory_list.include(croatia)

        self.assertNotIn(slovenia, territory_list.countries)
        with self.assertRaises(ValueError):
            territory_list.exclude(slovenia)

        # Slovenia is not in Africa
        territory_list = TerritoryList()
        territory_list.include(world)
        territory_list.exclude(cat)
        self.assertGreater(len(territory_list.countries), 100)
        self.assertIn(slovenia, territory_list.countries)

        territory_list = TerritoryList()
        territory_list.add(world, 10)
        territory_list.add(croatia, 10)
        self.assertIn(slovenia, territory_list)
        self.assertEqual(territory_list[croatia], 20)
        territory_list.add(croatia, 10)
        self.assertEqual(territory_list[croatia], 30)
        territory_list.add(balkans, 10)
        self.assertEqual(territory_list[croatia], 40)
        territory_list.add(europe, 10)
        self.assertEqual(territory_list[croatia], 50)

        territory_list = TerritoryList()
        territory_list.include(europe)
        territory_list.exclude(balkans)
        self.assertIn(germany, territory_list.countries)
        self.assertNotIn(slovenia, territory_list.countries)

        territory_list = TerritoryList()
        with self.assertRaises(ValueError):
            territory_list.include(0)

        # Test compressing without objects
        t = TerritoryList()
        t.compress()

        t.include('2136')
        t.exclude('hr')
        t.include('hr')
        t.exclude('2NA')
        t.include('2NA')
        t.exclude('US')
        t.include('US')
        t.compress()
        
        t2 = TerritoryList()
        t2.include('2136')
        self.assertEqual(t, t2)

        # Test compressing with objects
        t = TerritoryList()
        t.compress()

        t.include('2136', 50)
        t.exclude('hr')
        t.include('hr', 50)
        t.exclude('2NA')
        t.include('2NA', 25)
        t.exclude('US')
        t.include('US', 100)
        t.compress()

        self.assertIn(asia, t.keys())
        self.assertEqual(t.get(asia), 50)

        self.assertIn(europe, t.keys())
        self.assertEqual(t.get(europe), 50)

        self.assertIn(usa, t.keys())
        self.assertEqual(t.get(usa), 100)

        # Test with complex territories and compressing
        bt = Territory.get('2111')
        uk = Territory.get('826')
        t = TerritoryList()
        t.add('2136', 50)
        t.add(bt, 25)
        t.compress()
        self.assertEqual(t.get(bt), 75)
        self.assertEqual(t.get(uk), None)
