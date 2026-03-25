import os
from clam_casino import ClamCasino
from flask import Flask, request, abort
from flask_cors import CORS

app = Flask(__name__)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:80").split(",")
CORS(app)

games = {}

# creates a new game instance and stores it in the hashmap
@app.route("/new", methods = ["POST"])
def new_game(level = 0, size = 5):
    game = ClamCasino(level, size)
    game_hash = str(hash(game))
    games[game_hash] = game

    if os.getenv("CLAMCASINO_DEBUG") == "1":
        print(f"GAME ID: {game_hash}")
        game.print_solutions()

    return game_hash

# requests a card flip in a given game session
@app.route("/flip/<game_id>", methods = ["POST"])
def flip_card(game_id):
    game = __expect_game(game_id)

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

    if os.getenv("CLAMCASINO_DEBUG") == "1":
        print(f"GAME ID: {game_id}")
        game.print_lut()

    response = {"card": result, "score": game.score, "over": game.over}
    games.pop(game_id)

    return response

@app.route("/totals/<game_id>", methods = ["GET"])
def get_totals(game_id):
    game = __expect_game(game_id)

    return game.get_totals()

def __expect_game(game_id):
    game = None
    try:
        game = games[game_id]
    except(KeyError):
        abort(404)

    return game
