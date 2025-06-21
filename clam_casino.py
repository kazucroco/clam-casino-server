from game_board import GameBoard

class ClamCasino:
    level = 0
    score = 0
    board = None
    over = False
    
    def __init__(self, level, size = 5):
        self.level = level
        self.board = GameBoard(self.level, size)

    def flip(self, row, col):
        # cancel the flip if the card is already flipped or game is over
        if self.board.flip_lut[row][col] == 1:
            raise ValueError("Card is already flipped.")
        elif self.over:
            raise Exception("Game is over.")
        
        # mark the card as flipped on the LUT
        self.board.flip_lut[row][col] = 1

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
            self.board.special_count -= 1

        # end game if all special cards are turned
        if self.board.special_count <= 0:
            self._end_game()

        return value
        
    def _end_game(self):
        self.over = True
        return self.score