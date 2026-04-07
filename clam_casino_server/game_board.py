import random
import os
import math

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

    def __init__(self, level = 0, size = 6):
        maxlevel=0

        # Override max level value if using Voltorb Flip values
        if int(os.getenv("USE_VTFLIP_VALS", 1)) == 1:
            maxlevel = 7
        else: 
            maxlevel = int(os.getenv("MAX_LEVEL", 0))

        # Update board size to serverside-configured size
        size = int(os.getenv("BOARD_SIZE", 6))

        # Validate level value before generating a board.
        if level > maxlevel or level < 0:
            raise ValueError("Requested level ({level}) must be greater than 0 and <= ({maxlevel})")
        
        # Create common objects for game board.
        self.board = []
        self.flip_lut = []

        for i in range(0, size):
            self.board.append([])
            self.flip_lut.append([0] * size)

        # Legacy generation code, using the original values from Voltorb Flip.
        if int(os.getenv("USE_VTFLIP_VALS", 1)) == 1: 
            print("Using Voltorb Flip values...")
            # Select variant 0-4.
            variant = random.randrange(0, 5)

            # Insert 0, 2, and 3 cards based on the difficulty table values.
            self.__insert_special(0, self._DIFFICULTY_TABLE[level][variant][0])
            self.__insert_special(2, self._DIFFICULTY_TABLE[level][variant][1])
            self.__insert_special(3, self._DIFFICULTY_TABLE[level][variant][2])

            # Set the board special count to the number of 2 and 3 cards.
            self.special_count = self._DIFFICULTY_TABLE[level][variant][1] + self._DIFFICULTY_TABLE[level][variant][2]
        
        # Generation code using limits set from environment variables.
        else:
            print("Using custom vals...")
            # Find the required number of of 0, 2, 3 cards.
            twos_threes = self.__calc_card_counts(int(os.getenv(f"L{level}_MAXSCORE", 2)), int(os.getenv(f"L{level - 1}_MAXSCORE", 2)))
            specials = [int(os.getenv(f"L{level}_ZEROS", 6)), twos_threes[0], twos_threes[1]]

            self.__insert_special(0, specials[0])
            self.__insert_special(2, specials[1])
            self.__insert_special(3, specials[2])
            
            # Sets the board special count to the number of 2 and 3 cards.
            self.special_count = twos_threes[0] + twos_threes[1]

        # Fill in the rest of the spaces with 1s.
        for row in self.board:
            while len(row) < size:
                row.insert(random.randrange(0, size), 1)

    # Inserts {value} into the game board at a random index {count} times.
    def __insert_special(self, value, count):
        size = len(self.board)

        for i in range(0, count):
            # Insert as the first element if none exist already.
            try:
                row = random.randrange(0, size)
            except ValueError:
                row = 0
            try:
                col = random.randrange(0, size)
            except ValueError:
                col = 0

            # Insert value into random index.
            if len(self.board[row]) < size:
                self.board[row].insert(col, value)
            
            # Randomly selected row is already full.
            else:
                # Continuously try all other rows before giving up.
                for j in range(1, size + 1):
                    new_row = (row + j) % size

                    # Should only occur once all other rows have been tried. Quit.
                    if row == new_row:
                        return
                    # New row with space has been found.
                    if len(self.board[new_row]) < size:
                        self.board[new_row].insert(col, value)
                        break

    # Given a score limit, gives a random number of 2s and 3s that will result
    # in a score less than or equal to maxscore, but greater than or equal to prevmax.
    def __calc_card_counts(self, maxscore, prevmax):
        # Ensure at least 1 special card is generated.
        maxscore = max(2, maxscore)
        prevmax = max(2, prevmax)

        # Array of valid [{2}, {3}] counts.
        # Accounts for all values less than maxscore, but less than prevmax.
        valid_vals = []

        max_3 = int(math.log(maxscore, 3))

        for num_3 in range(max_3 + 1):
            tot_3 = 3 ** num_3

            num_2 = int(math.log(maxscore // tot_3, 2))

            tot_score = (2 ** num_2 + 3 ** num_3)

            if (tot_score < prevmax):
                continue

            valid_vals.append([num_2, num_3])

        variant = random.randrange(0, len(valid_vals))

        return valid_vals[variant]     
        
    def __str__(self):
        return str(self.board)