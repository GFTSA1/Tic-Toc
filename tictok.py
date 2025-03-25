from representation_utils import check_for_win, draw_board
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import time

load_dotenv()


client = MongoClient(os.getenv("cluster"))
db = client.tiktok
game = db.game


def connect_or_start_a_game(choice, game_id):
    if choice == 2:
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
        game_id = game.count_documents({}) + 1
    else:
        spots = game.find_one({"game_id": game_id})["spots"]
    return spots, game_id


def play(spots, game_id, choice_round):
    playing, complete = True, False

    if choice_round == 2:
        turn = 0
        prev_turn = -1
    else:
        draw_board(spots)
        turn = 2
        prev_turn = 0

    # Цикл гри
    while playing:
        # Чи хід перший?
        if turn != 0:
            # Очікування на хід суперника
            while True:
                sho = game.find_one({"game_id": game_id})
                if sho["turn"] == turn:
                    print('Waiting for the opponent turn')
                    time.sleep(5)
                else:
                    turn = sho["turn"]
                    spots = sho["spots"]
                    playing = sho["playing"]
                    complete = sho["complete"]
                    break
        # Чи інший гравець не вийшов?
        if playing is False:
            break
        # Чи інший гравець не виграв?
        if complete:
            break


        #

        if prev_turn == turn:
            print("Invalid spot selected, please pick another.")
        prev_turn = turn

        # Перевіряємо, хто грає
        if turn % 2 == 0:
            player = "X"
        else:
            player = "O"
        print("Player " + f"{player}" + "'s turn: Pick your spot or press q to quit")

        choice_round = input()
        if choice_round == "q":
            playing = False
        try:
            int_value = int(choice_round)
            if int_value < 0 or int_value > 9:
                print("Invalid spot selected, please pick another.")
                continue
            if spots[choice_round] == "X" or spots[choice_round] == "O":
                print("Invalid spot selected, please pick another.")
                continue
            turn += 1
            spots[choice_round] = player
            if check_for_win(spots):
                playing, complete = False, True
            if turn > 8:
                playing = False

            if turn == 1:
                game.insert_one(
                    {
                        "game_id": game_id,
                        "turn": turn,
                        "spots": spots,
                        "playing": playing,
                        "complete": complete,
                    }
                )
            else:
                game.update_one(
                    {"game_id": game_id},
                    {
                        "$set": {
                            "turn": turn,
                            "spots": spots,
                            "playing": playing,
                            "complete": complete,
                        }
                    },
                )
        except ValueError:
            print("Invalid spot selected, please pick another.")


choice = input(
    "Do you want to join a game or start a new one?\n1-Join\n2-Start a new one\n"
)

try:
    choice = int(choice)
    if choice == 1:
        game_id_input = input(
            "Please provide the game id of the game you want to join: "
        )
        game_id = int(game_id_input)
    else:
        game_id = 0
    spots, game_id = connect_or_start_a_game(choice, game_id)

except ValueError:
    raise ValueError("Invalid choice selected, please start again.")


play(spots, game_id, choice)

# draw_board(spots)
# if complete:
#     if player == "X":
#         print("Player 1 Wins!")
#     else:
#         print("Player 2 Wins!")
# else:
#     print("No Winner")
