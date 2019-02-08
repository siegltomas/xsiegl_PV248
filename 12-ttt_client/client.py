#!/usr/bin/env python3

import sys
import json
import aiohttp
import asyncio

import ttt


async def connect(url_address, client_session):
    async with client_session.get(url_address) as outcome:
        json_loads = json.loads(await outcome.text())
        return json_loads


async def offer_games(current_games, client_session):
    if current_games:
        print("available games to play:")
        for game in current_games:
            game_status = await connect(host + "/status?game=" +
                                        str(game["id"]), client_session)
            if "board" not in game_status:
                continue
            game_board = game_status["board"]
            if game_board == [[0,0,0], [0,0,0], [0,0,0]]:
                print(game["id"], game["name"])
        print("\nenter game id to join existing game, enter 'new <name>' to start a new game")
    else:
        print("no games available, enter 'new <name>' to start a new game")

async def print_board(id, client_session):
    game_status = await connect(host + "/status?game=" + str(id), client_session)
    game_board = game_status["board"]
    symbol_to_print = {0: "_", 1: "x", 2: "o"}

    for row in game_board:
        for element in row:
            print(symbol_to_print[element], end='')
        print()
    print()

async def play_move(id, player, client_session):
    symbol_to_print = {1: "x", 2: "o"}
    print("your turn (%s):" % symbol_to_print[player])

    while True:
        xy_coordinations_string = input()
        xy_coordinations_list = xy_coordinations_string.split(" ")
        number_of_coordinations = len(xy_coordinations_list)
        if number_of_coordinations != 2:
            print("invalid input")
            continue

        try:
            x = int(xy_coordinations_list[0])
            y = int(xy_coordinations_list[1])
        except ValueError:
            print("invalid input")
            continue

        connect_outcome = await connect(host +
                "/play?game=%s&player=%s&x=%s&y=%s" % (id, player, x, y), client_session)
        if connect_outcome["status"] == "bad":
            print("invalid input")
            continue

        await print_board(id, client_session)
        break


async def client_processing():
    async with aiohttp.ClientSession() as client_session:
        while True:
            current_games = await connect(host + "/list", client_session)

            ids = []
            for game in current_games:
                ids.append(game["id"])

            await offer_games(current_games, client_session)
            str_input = input()

            if str_input.startswith("new"):
                input_list = str_input.split(" ")
                if len(input_list) < 2:
                    name = ""
                else:
                    name = " ".join(input_list[1:])

                connect_outcome = await connect(host + "/start?name=" + name, client_session)
                id = connect_outcome["id"]
                player = 1
                break

            try:
                id = int(str_input)
                if id in ids:
                    print("joining...")
                    player = 2
                    break
                print("invalid id, try again")
            except ValueError:
                print("invalid command, try again")

        wait = True
        while True:
            game_status = await connect(host + "/status?game=" + str(id), client_session)
            if "winner" in game_status:
                if game_status["winner"] != player:
                    await print_board(id, client_session)
                if game_status["winner"] == 0:
                    print("draw")
                else:
                    if game_status["winner"] == player:
                        print("you win")
                    else:
                        print("you lose")
                break
            if game_status["next"] == player:
                await print_board(id, client_session)
                await play_move(id, player, client_session)
                wait = True
            else:
                if wait:
                    print("waiting for the other player")
                    wait = False
            await asyncio.sleep(1)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("argv error: not enough program arguments")
        print("invocation: ./client.py host port")
        sys.exit()

    str_host = sys.argv[1]
    port_number = int(sys.argv[2])
    
    if "http://" not in str_host:
        str_host = "http://" + str_host + ":" + str(port_number)
    else:
        str_host = str_host + ":" + str(port_number)

    host = str_host

    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(client_processing())
