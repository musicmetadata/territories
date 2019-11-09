import unittest
from music_metadata.territories import Territory

class TestTerritory(unittest.TestCase):

    def test_relations(self):
        world = Territory.get('2136')
        self.assertEqual(str(world).upper(), 'WORLD')
        self.assertEqual(len(world.children), 5)
        self.assertIsNone(world.parent)

        europe = Territory.get('2120')
        self.assertEqual(europe.parent, world)
        self.assertIn(europe, world.descendants)
        self.assertNotIn(europe, world.countries)

        croatia = Territory.get('191')
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


