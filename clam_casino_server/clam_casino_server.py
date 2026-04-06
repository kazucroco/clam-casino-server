import os
from clam_casino import ClamCasino
from flask import Flask, request, abort, make_response, jsonify
from flask_cors import CORS
import datetime
from werkzeug.security import generate_password_hash
import sqlite3


conn = sqlite3.connect(f"./data/pscores.sqlite")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS pscores (
    ccid TEXT PRIMARY KEY,
    pscore INTEGER
    )
''')

conn.commit()
conn.close()
print("Database initialized.")

# prepare flask (api)
app = Flask(__name__)
app.permanent_session_lifetime = True

allowed_origins = os.getenv("ALLOWED_ORIGINS", "null").split(",")
CORS(app, origins=allowed_origins, supports_credentials=True)

# list of active games on the server, accessed using the object hash as a key
games = {}

# generate and set a new cookie if none is found
@app.route("/", methods = ["GET"])
def index():
    ccid = request.cookies.get("ccid")
    if ccid == None or __get_score(ccid) == None:
        ccid = __generate_ccid(request)
    resp = make_response(jsonify({"ccid" : ccid}))

    days = int(os.getenv("COOKIE_SHELFLIFE", 30))
    max_age_seconds = days * 24 * 60 * 60

    resp.set_cookie("ccid", str(ccid), secure=True, samesite="None", partitioned=True, max_age=max_age_seconds)
    return resp

# creates a new game instance and stores it in the hashmap
@app.route("/new", methods = ["POST"])
def new_game(level = 0):
    content = request.get_json()

    # get game owner
    ccid = request.cookies.get("ccid")
    if ccid == None or __get_score(ccid) == None:
        ccid = __generate_ccid(request)
    
    # change game level if requested, otherwise use 0
    try:
        level = int(content["level"])
    except KeyError:
        pass

    try:
        game = ClamCasino(ccid, level)
    except IndexError:
        # give a bad request response if the level is out of range
        abort(400)
    except:
        # internal server error otherwise
        abort(500)

    game_hash = str(hash(game))
    games[game_hash] = game

    if os.getenv("CLAMCASINO_DEBUG") == "1":
        print(f"GAME ID: {game_hash}")
        game.print_solutions()

    resp = { "game_id": str(game_hash), "pscore": __get_score(ccid), "totals": game.get_totals(), "size": len(game.board.board), "level": level }
    # conversion to the flask response type to prepare for cookie
    resp = make_response(jsonify(resp))

    days = int(os.getenv("COOKIE_SHELFLIFE", 30))
    max_age_seconds = days * 24 * 60 * 60

    resp.set_cookie("ccid", str(ccid), secure=True, samesite="None", partitioned=True, max_age=max_age_seconds)    
    
    return resp

# requests a card flip in a given game session
@app.route("/flip/<game_id>", methods = ["POST"])
def flip_card(game_id):
    # locate the game and its owner
    game = __expect_game(game_id)
    ccid = request.cookies.get("ccid")
    solution = []
    flip_lut = game.get_lut()

    # disallow users from interacting with each others games
    if game.owner != ccid:
        abort(403)

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
    except IndexError as err:
        print(err)
        abort(404)

    if os.getenv("CLAMCASINO_DEBUG") == "1":
        solution = game.get_board()
        print(f"GAME ID: {game_id}")
        game.print_lut()

    # update the user's persistent score once the game is over
    pscore = __get_score(game.owner)
    if game.over:
        __set_score(game.owner, pscore + game.score)
        pscore = __get_score(game.owner)
        solution = game.get_board()

    # prepare the response before the game is deleted
    response = {"card": result, "score": game.score, "pscore": pscore, "over": game.over, "flip_lut": flip_lut, "solution": solution}

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
    ccid = generate_password_hash(str(ip) + str(time))
    __set_score(ccid, 0)
    return ccid

def __set_score(ccid, pscore):
    conn = sqlite3.connect("./data/pscores.sqlite")
    cursor = conn.cursor()

    query = '''
        INSERT INTO pscores (ccid, pscore) 
        VALUES (?, ?)
        ON CONFLICT(ccid) 
        DO UPDATE SET pscore = excluded.pscore
    '''
    
    try:
        cursor.execute(query, (ccid, pscore))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred modifying the database: {e}")
    finally:
        conn.close()

def __get_score(ccid):
    conn = sqlite3.connect("./data/pscores.sqlite")
    cursor = conn.cursor()

    query = f"SELECT pscore FROM pscores WHERE ccid = ?"
    
    try:
        cursor.execute(query, (ccid,))
        result = cursor.fetchone() 
        
        if result:
            return result[0] 
        else:
            return None
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()
