from clam_casino import ClamCasino
from flask import Flask, request, abort

games = {}
app = Flask(__name__)

# creates a new game instance and stores it in the hashmap
@app.route("/new", methods = ["POST"])
def new_game(level = 0, size = 5):
    game = ClamCasino(level, size)
    game_hash = str(hash(game))
    games[game_hash] = game
    return game_hash

# requests a card flip in a given game session
@app.route("/flip/<game_id>", methods = ["PUT"])
def flip_card(game_id):
    print(request)

    # check if game exists
    game = None
    try:
        game = games[game_id]
    except:
        abort(404)

    # parse card coords
    row = int(request.args.get("row"))
    col = int(request.args.get("col"))

    result = None

    # attempt card flip
    try:
        result = game.flip(row, col)
    except ValueError as err:
        print(err)
        abort(403)

    return {"card": result, "score": game.score, "over": game.over}
  