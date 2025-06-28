class DebugObject:

    def print_solutions(game):
        for i in range(0, 5):
            for k in range(0, 5):
                print(str(game.board.board[i][k]), end=" ")
            print("| " + str(game.row_totals[i]))

        for i in range(0, 5):
            print(str(game.col_totals[i]), end=" ")