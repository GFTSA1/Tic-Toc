from representation_utils import check_turn, check_for_win, draw_board
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import time

load_dotenv()


client = MongoClient(os.getenv("cluster"))

spots = {
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
}
playing, complete = True, False
turn = 0
prev_turn = -1

db = client.tiktok
game = db.game
game_id = game.count_documents({}) + 1

while playing:
    draw_board(spots)
    if prev_turn == turn:
        print("Invalid spot selected, please pick another.")
    prev_turn = turn

    if turn % 2 == 0:
        player = "X"
    else:
        player = "O"

    print("Player " + f"{player}" + "'s turn: Pick your spot or press q to quit")

    choice = input()
    if choice == "q":
        playing = False
    try:
        int_value = int(choice)
        if int_value < 0 or int_value > 9:
            print("Invalid spot selected, please pick another.")
            continue
        if spots[choice] == "X" or spots[choice] == "O":
            print("Invalid spot selected, please pick another.")
            continue
        turn += 1
        spots[choice] = player
        if check_for_win(spots):
            playing, complete = False, True
        if turn > 8:
            playing = False

        if turn == 1:
            game.insert_one({"game_id": game_id, "spots": spots})
        else:
            game.update_one({"game_id": game_id}, {"$set": {"spots": spots}})
    except ValueError:
        print("Invalid spot selected, please pick another.")


draw_board(spots)
if complete:
    if check_turn(turn) == "X":
        print("Player 1 Wins!")
    else:
        print("Player 2 Wins!")
else:
    print("No Winner")
