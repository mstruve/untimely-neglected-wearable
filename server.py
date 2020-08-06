import os
import random
import time

import snakebrain

import cherrypy
#import cProfile

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""


class Battlesnake(object):
    game_id = ""
    turn = -1

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        return {
            "apiversion": "1",
            "author": "altersaddle",  
            "color": "#306448",  # TODO: create function to generate
            "head": "tongue",  # TODO: Personalize
            "tail": "sharp",  # TODO: Personalize
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        # TODO: Use this function to decide how your snake is going to look on the board.
        data = cherrypy.request.json

        self.turn = data["turn"]
        self.game_id = data["game"]["id"]

        self.log("START")
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        begin_time = time.perf_counter()
        data = cherrypy.request.json
        parse_time = time.perf_counter() - begin_time

        self.turn = data["turn"]
        self.game_id = data["game"]["id"]
        body = data["you"]["body"]
        snakes = data["board"]["snakes"]

        # Choose a direction to move in
        possible_moves = ["up", "down", "left", "right"]

        safe_moves = snakebrain.get_safe_moves(possible_moves, body, data["board"])
        safe_time = time.perf_counter() - begin_time
 #       pr = cProfile.Profile()
 #       pr.enable()
        smart_moves = snakebrain.avoid_trap(safe_moves, body, data["board"], data["you"])
 #       pr.disable()
 #       pr.print_stats()
        smart_time = time.perf_counter() - begin_time
    
        move = random.choice(possible_moves)

        if smart_moves:
            self.log (f"Smart! {smart_moves}")
            move = random.choice(smart_moves)

        elif safe_moves:
            self.log (f"Safe! {safe_moves}")
            move = random.choice(safe_moves)

        total_time = time.perf_counter() - begin_time
        self.log(f"MOVE: {move} parse_time {parse_time} safe_time {safe_time} smart_time {smart_time} total_time {total_time}")
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        self.log("END")
        return "ok"

    def log(self, message):
        # output message iwth globals
        print(f"{self.game_id} [{self.turn}] {message}")


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
