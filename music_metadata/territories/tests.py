import unittest
from music_metadata.territories.territory import Territory
from music_metadata.territories.territory_list import TerritoryList


class TestTerritory(unittest.TestCase):

    def test_relations(self):
        """
        Test basic relations between hand-picked objects.
        """

        with self.assertRaises(AttributeError):
            Territory.get(2136)

        world = Territory.get('2136')
        self.assertEqual(str(world), 'WORLD')
        self.assertEqual(
            repr(world), 'Territory: WORLD (GEOGRAPHICAL COUNTRY-GROUP)')
        self.assertEqual(len(world.children), 5)
        self.assertIsNone(world.parent)

        europe = Territory.get('2120')
        self.assertEqual(europe.parent, world)
        self.assertIn(europe, world.descendants)
        self.assertNotIn(europe, world.countries)

        croatia = Territory.get('HR')
        self.assertNotIn(croatia, europe.children)
        self.assertIn(croatia, europe.descendants)
        self.assertIn(croatia, europe.countries)
        self.assertIn(croatia, world.countries)

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
