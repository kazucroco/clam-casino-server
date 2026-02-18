from clam_casino import ClamCasino
from flask import Flask, request, abort
from debug_object import DebugObject

games = {}
app = Flask(__name__)

# creates a new game instance and stores it in the hashmap
@app.route("/new", methods = ["POST"])
def new_game(level = 0, size = 5):
    game = ClamCasino(level, size)
    game_hash = str(hash(game))
    games[game_hash] = game
    DebugObject.print_solutions(game)
    return game_hash

# requests a card flip in a given game session
@app.route("/flip/<game_id>", methods = ["POST"])
def flip_card(game_id):
    # check if game exists
    game = None
    try:
        game = games[game_id]
    except:
        abort(404)

    content = request.get_json()

    # parse card coords
    row = int(content["row"])
    col = int(content["col"])

    result = None

    # attempt card flip
    try:
        result = game.flip(row, col)
    except ValueError as err:
        print(err)
        abort(403)

    return {"card": result, "score": game.score, "over": game.over}
  
