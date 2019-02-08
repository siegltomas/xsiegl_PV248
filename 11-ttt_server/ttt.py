#!/usr/bin/env python3

import sys
import json
import urllib.parse
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler

ENCODING = "utf-8"

START = "/start"
STATUS = "/status"
PLAY = "/play"
LIST = "/list"

count = 0
game = dict()

class ServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        event = parsed_url.path
        event_parameters = parsed_url.query
        event_parameters = urllib.parse.parse_qs(event_parameters)

        if event == START:
            self.start(event_parameters)
        elif event == STATUS:
            self.status(event_parameters)
        elif event == PLAY:
            self.play(event_parameters)
        elif event == LIST:
            self.list()
        else:
            self.send_error(400, "400 Bad Request error")

    def start(self, event_parameters):
        global count
        global game

        name = event_parameters["name"][0] if "name" in event_parameters else ""
        game[count] = {"name": name,
                              "board": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                              "next": 1,
                              "winner": None}
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        json_dict = {"id": count}
        json_string = str(json.dumps(json_dict))
        json_string = bytes(json_string, ENCODING)
        self.wfile.write(json_string)
        count += 1

    def status(self, event_parameters):
        global count
        global game

        try:
            if "game" not in event_parameters:
                raise KeyError
            id = int(event_parameters["game"][0])
            our_game = game[id]
            if our_game["winner"] is not None:
                json_dict = {"board": our_game["board"],
                             "winner": our_game["winner"]}
            else:
                json_dict = {"board": our_game["board"],
                             "next": our_game["next"]}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            json_string = str(json.dumps(json_dict))
            json_string = bytes(json_string, ENCODING)
            self.wfile.write(json_string)
        except ValueError:
            self.send_error(404, "id of the game is invalid")
        except KeyError:
            self.send_error(404, "id of the game not found")

    def play(self, event_parameters):
        global count
        global game

        try:
            id = int(event_parameters["game"][0])
            x = int(event_parameters["x"][0])
            y = int(event_parameters["y"][0])
            player = int(event_parameters["player"][0])
            if id not in game:
                self.send_error(404, "there is not such game")
                return

            json_dict = dict()
            our_game = game[id]
            if player != our_game["next"]:
                json_dict["status"] = "bad"
                json_dict["message"] = "another player should play"
            elif x < 0 or y < 0 or x > 2 or y > 2:
                json_dict["status"] = "bad"
                json_dict["message"] = "impossible move: move out of range (3x3)"
            elif our_game["board"][y][x] != 0:
                json_dict["status"] = "bad"
                json_dict["message"] = "impossible move: square is already taken"
            elif our_game["winner"] is not None:
                json_dict["status"] = "bad"
                json_dict["message"] = "game is over"
            else:
                our_game["board"][y][x] = player

                if player == 1:
                    our_game["next"] = 2
                else:
                    our_game["next"] = 1

                our_game["winner"] = self.winner(our_game["board"])
                json_dict["status"] = "ok"

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            json_string = str(json.dumps(json_dict))
            json_string = bytes(json_string, ENCODING)
            self.wfile.write(json_string)
        except KeyError:
            self.send_error(400, "missing parameters")
        except ValueError:
            self.send_error(400, "numeric parameters expected")

    def list(self):
        global game

        my_list = []
        for key, value in game.items():
            my_list.append({"id": key, "name": value["name"]})
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        json_string = str(json.dumps(my_list))
        json_string = bytes(json_string, ENCODING)
        self.wfile.write(json_string)

    def winner(self, playing_board):
        if 0 not in playing_board[0] and 0 not in playing_board[1] and 0 not in playing_board[2]:
            return 0 # draw
        for player in [1, 2]:
            # diagonals
            if (playing_board[0][0] == player and playing_board[1][1] == player and playing_board[2][2] == player) or \
                    (playing_board[0][2] == player and playing_board[1][1] == player and playing_board[2][0] == player):
                return player
            for rc in range(3):
                # rows and cols
                if (playing_board[rc][0] == player and playing_board[rc][1] == player and playing_board[rc][2] == player) or \
                        (playing_board[0][rc] == player and playing_board[1][rc] == player and playing_board[2][rc] == player):
                    return player
        return None


class ThreadedHTTP(ThreadingMixIn, HTTPServer):
    pass

def main():
    if len(sys.argv) < 2:
        print("argv error: not enough program arguments")
        print("invocation: ./ttt.py port")
        sys.exit()

    host_name = "127.0.0.1"

    ttt_server = ThreadedHTTP((host_name, 
                              int(sys.argv[1])), 
                              ServerHandler)
    ttt_server.serve_forever()

if __name__ == '__main__':
    main()
