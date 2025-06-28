from game_board import GameBoard

class ClamCasino:
    level = 0
    score = 0
    board = None
    row_totals = []
    col_totals = []
    over = False
    
    def __init__(self, level, size = 5):
        self.level = level
        self.board = GameBoard(self.level, size)
        self._get_totals()

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
    
    def _get_totals(self):
        col_totals = []

        # every row in the table
        for i in range(0, len(self.board.board)):
            row = self.board.board[i]
            row_point_total = 0
            row_bomb_count = 0

            # every value in the row
            for j in range(0, len(row)):
                val = row[j]
                # add to the row / col BOMB count
                if val == 0:
                    row_bomb_count += 1

                    # creates table for col totals or increases count
                    if i == 0:
                        col_totals.append([0, 1])
                    else:
                        col_totals[j][1] += 1
                    
                # add to the row / col SCORE total
                else:
                    row_point_total += val

                    # creates table for col totals or increases count
                    if i == 0:
                        col_totals.append([val, 0])
                    else:
                        col_totals[j][0] += val

            self.row_totals.append([row_point_total, row_bomb_count])
            
        self.col_totals = col_totals