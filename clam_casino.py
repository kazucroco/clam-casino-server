from game_board import GameBoard

class ClamCasino:
    level = 0
    score = 0
    remaining_cards = None
    board = None
    over = False
    flipped_lut = [[0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0]]
    
    def __init__(self, level, size = 5):
        self.level = level
        self.board = GameBoard(self.level, size)
        self.remaining_cards = self.board.special_count

    def flip(self, row, col):
        # cancel the flip if the card is already flipped or game is over
        if self.over or self.flipped_lut[row][col] == 1:
            return -1
        
        # mark the card as flipped on the LUT
        self.flipped_lut[row][col] = 1

        # retreive card value
        value = self.board.board[row][col]

        # update score
        if value == 0:
            self.score = 0
            self._end_game()
        elif self.score == 0:
            self.score += value
        else:
            self.score *= value

        # update special card count
        if value > 1:
            self.remaining_cards -= 1

        # end game if all special cards are turned
        if self.remaining_cards <= 0:
            self._end_game()

        return value
        
    def _end_game(self):
        self.over = True
        return self.score