import random

class GameBoard:
    board = None
    flip_lut = None
    special_count = 0

    # DIFFICULTY_TABLE[LEVEL][VARIANT][0 | 2x | 3x]
    _DIFFICULTY_TABLE = [[[6,  3, 1], [6,  0, 3], [6,  5, 0], [6, 2, 2],  [6, 4, 1]],
                         [[7,  1, 3], [7,  6, 0], [7,  3, 2], [7, 0, 4],  [7, 5, 1]],
                         [[8,  2, 3], [8,  7, 0], [8,  4, 2], [8, 1, 4],  [8, 6, 1]],
                         [[8,  3, 3], [8,  0, 5], [10, 8, 0], [10, 5, 2], [10, 2, 4]],
                         [[10, 7, 1], [10, 4, 3], [10, 1, 5], [10, 9, 0], [10, 6, 2]],
                         [[10, 3, 4], [10, 0, 6], [10, 8, 1], [10, 5, 3], [10, 2, 5]],
                         [[10, 7, 2], [10, 4, 4], [13, 1, 6], [13, 9, 1], [10, 6, 3]],
                         [[10, 0, 7], [10, 8, 2], [10, 5, 4], [10, 2, 6], [10, 7, 3]]]

    def __init__(self, level = 0, size = 5):
        # select variant 0-4
        variant = random.randrange(0, 5)

        # table of all values
        self.board = []
        self.flip_lut = []

        # create SIZE rows in the value table
        for i in range(0, size):
            self.board.append([])
            self.flip_lut.append([0] * size)

        # insert 0, 2, and 3 cards
        self._insert_special(0, self._DIFFICULTY_TABLE[level][variant][0])
        self._insert_special(2, self._DIFFICULTY_TABLE[level][variant][1])
        self._insert_special(3, self._DIFFICULTY_TABLE[level][variant][2])

        # fill in the rest of the spaces with 1s
        for row in self.board:
            while len(row) < size:
                row.insert(random.randrange(0, size + 1), 1)

    def _insert_special(self, value, count):
        for i in range(0, count):
            try:
                row = random.randrange(0, len(self.board))
            except ValueError:
                row = 0
            try:
                col = random.randrange(0, len(self.board))
            except ValueError:
                col = 0

            if len(self.board[row]) < len(self.board):
                self.board[row].insert(col, value)
            else:
                i -= 1
                continue

            if value > 1:
                self.special_count += 1

    def __str__(self):
        return str(self.board)