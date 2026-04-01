import os
from clam_casino import ClamCasino
from flask import Flask, request, abort, make_response, jsonify
from flask_cors import CORS
import datetime
from werkzeug.security import generate_password_hash

app = Flask(__name__)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:80").split(",")
CORS(app)

games = {}

# tries to identify the user or create a new ID if unknown
@app.route("/", methods = ["GET"])
def index():
    # checks for an existing ID in the user's browser
    ccid = request.cookies.get("ccid")

    # generate a new ID if does not exist TODO: later, make this happen with an invalid ID
    if ccid == None:
        ccid = __generate_ccid(request)

    resp = make_response(jsonify({ "ccid": str(ccid) }))
    resp.set_cookie("ccid", str(ccid))

    return resp

# creates a new game instance and stores it in the hashmap
@app.route("/new", methods = ["POST"])
def new_game(level = 0, size = 6):
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

    # prepares the game for garbage collection after it has finished
    if(game.over):
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

def __generate_ccid(request):
    ip = request.remote_addr
    time = datetime.datetime.now()
    return generate_password_hash(str(ip) + str(time))