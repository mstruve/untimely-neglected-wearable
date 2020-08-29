import json

def to_new_api(old, dimension):
    return {"x":old["X"], "y": (dimension - 1) - old["Y"]}

with open('./boardstate.raw') as f:
    boardstate = json.load(f)

move = {}
board = {}
boardsize = 11
snake_names = ['Untimely Neglected Wearable', 'Untimely Neglected Embedded Device', 'Snakeberry P2i']

# TODO: make this an argument
if len(boardstate["Hazards"]) > 0:
    boardsize = 19

move["game"] = {"id":"transform", "timeout": 500}
move["turn"] = boardstate["Turn"]
board["snakes"] = []
board["width"] = boardsize
board["height"] = boardsize

for Snake in boardstate["Snakes"]:
    new_snake = {}
    if Snake["Death"]:
        continue
    new_snake["id"] = Snake["ID"]
    new_snake["name"] = Snake["Name"]
    new_snake["health"] = Snake["Health"]
    new_snake["body"] = [to_new_api(segment, boardsize) for segment in Snake["Body"]]
    new_snake["shout"] = Snake["Shout"]
    new_snake["squad"] = Snake["Squad"]

    new_snake["length"] = len(new_snake["body"])
    new_snake["head"] = new_snake["body"][0]

    if new_snake["name"] in snake_names:
        move["you"] = new_snake.copy()
    
    board["snakes"].append(new_snake)

board["food"] = [to_new_api(chonk, boardsize) for chonk in boardstate["Food"]]
board["hazards"] = [to_new_api(yikes, boardsize) for yikes in boardstate["Hazards"]]

move["board"] = board

print (json.dumps(move, indent=4))
