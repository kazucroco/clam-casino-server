from game_board import GameBoard

class ClamCasino:
    level = 0
    score = 0
    board = None
    row_totals = []
    col_totals = []
    over = False
    owner = None
    
    def __init__(self, owner, level, size = 6):
        self.owner = owner
        self.level = level
        self.board = GameBoard(self.level, size)
        self.__update_totals()

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
            self.__end_game()
        elif self.score == 0:
            self.score += value
        else:
            self.score *= value

        # update special card count
        if value > 1:
            self.board.special_count -= 1

        # end game if all special cards are turned
        if self.board.special_count <= 0:
            self.__end_game()

        return value
    
    def get_totals(self):
        totals = {"rows": self.row_totals, "cols": self.col_totals}
        return totals

    def print_solutions(self):
        for row in self.board.board:
            print(f"{row}")

    def print_lut(self):
        for row in self.board.flip_lut:
            print(f"{row}")

    def __end_game(self):
        self.over = True
        return self.score
    
    def __update_totals(self):
        row_totals = []
        col_totals = []

        # prepopulate the array of column totals [(r0 points, r0 hazards), ... ]
        for i in range(0, len(self.board.board)):
            col_totals.append([0, 0])

        # every row in the table
        for i in range(0, len(self.board.board)):
            # totals for row i: (points, zeroes)
            row = [0, 0]

            # every value in the row
            for j in range(0, len(self.board.board)):
                if self.board.board[i][j] == 0:
                    row[1] += 1
                    col_totals[j][1] += 1
                else:
                    row[0] += self.board.board[i][j]
                    col_totals[j][0] += self.board.board[i][j]
            
            row_totals.append(row)
                
        self.row_totals = row_totals
        self.col_totals = col_totals