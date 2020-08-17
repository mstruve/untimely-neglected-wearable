MOVE_LOOKUP = {"left":-1, "right": 1, "up": 1, "down":-1}

def get_next(current_head, next_move):
    """
    return the coordinate of the head if our snake goes that way
    """
    # Copy first
    future_head = current_head.copy()

    if next_move in ["left", "right"]:
        # X-axis
        future_head["x"] = current_head["x"] + MOVE_LOOKUP[next_move]
    elif next_move in ["up", "down"]:
        future_head["y"] = current_head["y"] + MOVE_LOOKUP[next_move]

    return future_head

def get_all_moves(coord):
    choices = ["left", "right", "up", "down"]
    return [get_next(coord, choice) for choice in choices]

def get_safe_moves(possible_moves, body, board):

    safe_moves = []

    for guess in possible_moves:
        guess_coord = get_next(body[0], guess)
        if avoid_walls(guess_coord, board["width"], board["height"]) and avoid_snakes(guess_coord, board["snakes"], board["food"]): 
            safe_moves.append(guess)
        elif guess_coord == body[-1] and guess_coord not in body[:-1]:
            # The tail is also a safe place to go... unless we have just eaten food
            # This is only valid after turn 3, if there's a non-tail segmenet in the square we terminate
            safe_moves.append(guess)

    return safe_moves

def avoid_walls(future_head, board_width, board_height):
    result = True

    x = int(future_head["x"])
    y = int(future_head["y"])

    if x < 0 or y < 0 or x >= board_width or y >= board_height:
        result = False

    return result

def avoid_snakes(future_head, snake_bodies, foods):
    for snake in snake_bodies:
        if future_head in snake["body"][:-1]:
            return False
        if future_head == snake["body"][-1] and any(move in foods for move in get_all_moves(snake["body"][0])):
            # if this snake eats, its tail will not move
            return False
    return True

def avoid_consumption(future_head, snake_bodies, my_snake):
    if len(snake_bodies) < 2:
        return True

    my_length = my_snake["length"]
    for snake in snake_bodies:
        if snake == my_snake:
            continue
        if future_head in get_all_moves(snake["head"]) and my_length <= snake["length"]:
            print(f'DANGER OF EATED {my_snake["head"]}->{future_head} by {snake["name"]}')
            return False
    return True

def avoid_food(future_head, food):
    return future_head not in food

def avoid_hazards(future_head, hazards):
    # Convenience method
    return future_head not in hazards

def get_minimum_moves(start_coord, targets):
    # This could probably be a lambda but I'm not that smart
    steps = []
    for coord in targets:
        steps.append(abs(coord["x"] - start_coord["x"]) + abs(coord["y"] - start_coord["y"]))
    return min(steps)

def get_closest_enemy_head(head_coord, other_snakes):
    steps = [100]
    for snake in other_snakes:
        steps.append(abs(snake["head"]["x"] - head_coord["x"]) + abs(snake["head"]["y"] - head_coord["y"]))
    return min(steps)

def steps_to_safety(direction, start, board):
    # There must be a better way to do this
    retval = 0
    next_coord = get_next(start, direction)
    while next_coord in board["hazards"] and avoid_walls(next_coord, board["width"], board["height"]):
        next_coord = get_next(next_coord, direction)
        retval += 1
    if not avoid_walls(next_coord, board["width"], board["height"]):
        retval += max([board["width"], board["height"]])
    return retval

def at_wall(coord, board):
    return coord["x"] == 0 or coord["y"] == 0 or coord["x"] == board["width"] - 1 or coord["y"] == board["height"] - 1

def avoid_crowd(moves, board, my_snake):
    crowd_cost = {}
    
    # Perhaps there's a clever way to create a dictionary of functions, but I want to be able to read this tomorrow
    if 'up' in moves:
        crowd_cost['up'] = len([snake for snake in board["snakes"] if snake["id"] != my_snake["id"] and snake['head']['y'] > my_snake['head']['y']])
    if 'down' in moves:
        crowd_cost['down'] = len([snake for snake in board["snakes"] if snake["id"] != my_snake["id"] and snake['head']['y'] < my_snake['head']['y']])
    if 'left' in moves:
        crowd_cost['left'] = len([snake for snake in board["snakes"] if snake["id"] != my_snake["id"] and snake['head']['x'] < my_snake['head']['x']])
    if 'right' in moves:
        crowd_cost['right'] = len([snake for snake in board["snakes"] if snake["id"] != my_snake["id"] and snake['head']['x'] > my_snake['head']['x']] )
 
    
    print(f'Crowd control: {crowd_cost}')
    return [move for move in moves if crowd_cost[move] == min(crowd_cost.values())]


def avoid_trap(possible_moves, body, board, my_snake):
    # make sure the chosen diretion has an escape route
    # is the path leading into an enclosed space smaller than us?
    smart_moves = []
    food_avoid = []
    all_moves = ["up", "down", "left", "right"]
    safe_moves = get_safe_moves(possible_moves, body, board)
    enemy_snakes = [snake for snake in board["snakes"] if snake["id"] != my_snake["id"]]
    safe_coords = {}

    # We know these directions are safe... for now
    for guess in safe_moves:
        #print(f"exploring {guess}")
        safe_coords[guess] = []
        guess_coord = get_next(body[0], guess)
        explore_edge = [guess_coord]
        all_coords = [guess_coord]
        next_explore = []

        for segments in body[:-1]:
            next_explore.clear()
            for explore in explore_edge:
                safe = get_safe_moves(all_moves, [explore], board)
                #print(f"Safe moves: {safe}")
                for safe_move in safe:
                    guess_coord_next = get_next(explore, safe_move)
                    if guess_coord_next not in all_coords:
                        next_explore.append(guess_coord_next)

                all_coords += next_explore.copy() 
                all_coords.append(explore)
            explore_edge = next_explore.copy()

        #print(f"{all_coords}")
        safe_coords[guess] += list(map(dict, frozenset(frozenset(i.items()) for i in all_coords)))

    for path in safe_coords.keys():
        guess_coord = get_next(body[0], path)

        if len(safe_coords[path]) >= len(body) and avoid_consumption(guess_coord, board["snakes"], my_snake) and avoid_hazards(guess_coord, board["hazards"]):
            smart_moves.append(path)
    
    if not smart_moves:
        # What if we try to chase our tail
        tail_neighbors = []
        tail_safe = get_safe_moves(all_moves, [body[-1]], board)
        for tail_safe_direction in tail_safe:
            tail_neighbors.append(get_next(body[-1], tail_safe_direction))

        for path in safe_coords.keys():
            if any(coord in safe_coords[path] for coord in tail_neighbors):
                print(f"Chasing tail {path}!")
                smart_moves.append(path)
        if not smart_moves:
            # tail might be right beside head
            for move in all_moves:
                test_move = get_next(body[0], move)
                if test_move == body[-1] and test_move not in body[:-1]:
                    smart_moves.append(move)
        if not smart_moves:
            # maybe an enemy tail?
            for move in safe_coords.keys():
                test_move = get_next(body[0], move)
                for snake in enemy_snakes:
                    if test_move == snake["body"][-1] and test_move not in body[:-1] and not any(coord in board["food"] for coord in get_all_moves(snake["body"][0])):
                        smart_moves.append(move)

    # No clear path, try to fit ourselves in the longest one
    if safe_coords and not smart_moves:
        squeeze_move = max(safe_coords, key= lambda x: len(safe_coords[x]))
        if len(safe_coords[squeeze_move]) > 2 and avoid_consumption(get_next(body[0], squeeze_move), board["snakes"], my_snake):
            print(f'squeezing into {squeeze_move}')
            smart_moves.append(squeeze_move)

    # make a conservative choice when at a wall
    if len(smart_moves) == 2 and len(board['snakes']) > 1:
        if at_wall(my_snake["head"], board) and not at_wall(my_snake["body"][1], board):
            smart_moves = avoid_crowd(smart_moves, board, my_snake)
        else:
            head_distance = {}
            for move in smart_moves:
                head_distance[move] = get_closest_enemy_head(get_next(body[0], move), enemy_snakes)

            if min(head_distance.values() <= 3):
                print(f'choosing to avoid heads {head_distance}')
                smart_moves = [move for move in smart_moves if head_distance[move] == max(head_distance.values())]

    hunger_threshold = 35

    # Seek food if there are other snakes larger than us, or if health is low
    if my_snake["health"] < hunger_threshold or any(snake["length"] >= my_snake["length"] for snake in enemy_snakes):
        print("Hungry!")
        food_choices = safe_coords.keys() 
        food_moves = {}
        closest_food = []

        for path in food_choices:
            if any(food in safe_coords[path] for food in board["food"]):
                food_moves[path] = get_minimum_moves(get_next(body[0], path), board["food"])

        if food_moves:
            closest_food_distance = min(food_moves.values())
            for path in food_moves.keys():
                if food_moves[path] <= closest_food_distance:
                    print(f"safe food towards {path} is {closest_food_distance} or less")
                    closest_food.append(path)
        elif board["food"]:
            for path in food_choices:
                food_moves[path] = get_minimum_moves(get_next(body[0], path), board["food"])
            if food_moves:
                closest_food_distance = min(food_moves.values())
                for path in food_moves.keys():
                    if food_moves[path] <= closest_food_distance:
                        print(f"unsafe food towards {path} is {closest_food_distance} or less")
                        closest_food.append(path)
        
        if closest_food:
            if my_snake["health"] < hunger_threshold:
                print("Blinded by hunger")
                smart_moves = closest_food
            else:
                food_intersect = [move for move in smart_moves if move in closest_food] 
                print(f'Smart food is {food_intersect}')
                if food_intersect:
                    smart_moves = food_intersect
    else:
        # avoid food if it's there to avoid
        if len(smart_moves) > 1 and board["food"]:
            food_avoid = [move for move in smart_moves if get_next(body[0], move) not in board["food"]]
            print(f'Avoiding food! {food_avoid}')

    if board["hazards"] and  len(smart_moves) > 1 and my_snake["head"] in board["hazards"]:
        # Choose the path that takes us out of hazard
        shortest_path = min([steps_to_safety(move, my_snake["head"], board) for move in smart_moves])
        smart_moves = [move for move in smart_moves if steps_to_safety(move, my_snake["head"], board) == shortest_path]
        print(f'going {shortest_path} moves towards {smart_moves} to escape hazards')
    elif food_avoid:
        smart_moves = food_avoid


    return smart_moves

