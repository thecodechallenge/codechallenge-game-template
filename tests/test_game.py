import unittest

from game.game import Game
from game.exceptions import InvalidData
from game import SIDE, TOTAL_MOVES


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game(['alice', 'bob'])

    def test_two_players_with_distinct_sides(self):
        self.assertEqual({p.side for p in self.game.players}, set(SIDE))
        self.assertEqual(self.game.remaining_moves, TOTAL_MOVES)
        self.assertFalse(self.game.game_over())

    def test_valid_move_scores(self):
        player = self.game.current_player
        self.game.move(number=7)
        self.assertEqual(player.score, 7)

    def test_invalid_move_raises(self):
        for bad in (0, 11, 'x', None):
            with self.assertRaises(InvalidData):
                self.game.move(number=bad)

    def test_game_over_after_total_moves(self):
        for _ in range(TOTAL_MOVES):
            self.game.move(number=1)
            self.game.next_turn()
        self.assertTrue(self.game.game_over())
        self.assertNotEqual(self.game.get_winner(), '')

    def test_serialization_roundtrip(self):
        self.game.move(number=5)
        restored = Game.from_dict(self.game.to_dict())
        self.assertEqual(restored.game_id, self.game.game_id)
        self.assertEqual(restored.current_player.side, self.game.current_player.side)
        self.assertEqual(restored.history, self.game.history)
        self.assertEqual(
            [p.score for p in restored.players],
            [p.score for p in self.game.players],
        )


if __name__ == '__main__':
    unittest.main()
