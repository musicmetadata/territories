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
            'Territory: WORLD (GEOGRAPHICAL COUNTRY-GROUP)')
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

    def test_world(self):
        """
        Test basic includes/excludes
        """

        world = Territory.get('2136')
        balkans = Territory.get('2108')
        croatia = Territory.get('HR')
        slovenia = Territory.get('705')
        europe = Territory.get('2120')
        cat = Territory.get('2115')

        territory_list = TerritoryList()
        territory_list.include(world)
        territory_list.exclude(croatia)
        self.assertIn(slovenia, territory_list.countries)
        self.assertIn(slovenia, territory_list.keys())

        territory_list = TerritoryList()
        territory_list.include(balkans)
        self.assertIn(slovenia, territory_list.countries)
        self.assertIn(slovenia, territory_list.keys())

        territory_list = TerritoryList()
        territory_list.include(world)
        territory_list.exclude(balkans)
        self.assertNotIn(slovenia, territory_list.countries)
        self.assertNotIn(slovenia, territory_list.keys())

        territory_list = TerritoryList()
        territory_list.include(world)
        with self.assertRaises(ValueError):
            territory_list.include(croatia)

        territory_list = TerritoryList()
        territory_list.include(slovenia)
        with self.assertRaises(ValueError):
            territory_list.include(world)

        territory_list = TerritoryList()
        territory_list.include(world)
        with self.assertRaises(ValueError):
            territory_list.include(europe)

        territory_list = TerritoryList()
        territory_list.include(world)
        with self.assertRaises(ValueError):
            territory_list.include(cat)

        territory_list = TerritoryList()
        territory_list.include(world, '50%')
        territory_list.exclude(europe)
        territory_list.include(croatia, '25%')
        self.assertIn('25%', territory_list.values())
        self.assertIn((croatia, '25%'), territory_list.items())
        self.assertEqual(len(territory_list), 5)

        with self.assertRaises(ValueError):
            territory_list.include(croatia)

        self.assertNotIn(slovenia, territory_list.countries)
        with self.assertRaises(ValueError):
            territory_list.exclude(slovenia)

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

