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
        if future_head == snake["body"][-1] and any (move in foods for move in get_all_moves(snake["body"][0])):
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

def avoid_hazards(future_head, hazards):
    # Convenience method
    return future_head not in hazards

def get_minimum_moves(start_coord, targets):
    # This could probably be a lambda but I'm nto that smart
    steps = []
    for coord in targets:
        steps.append(abs(coord["x"] - start_coord["x"]) + abs(coord["y"] - start_coord["y"]))
    return min(steps)

def get_closest_enemy(head_coord, snakes):
    if len(snakes) == 1:
        # so alone
        return -1
    steps = []
    for snake in snakes:
        if snake["head"] == head_coord:
            continue
        for body in snake["body"]:
            steps.append(abs(body["x"] - head_coord["x"]) + abs(body["y"] - head_coord["y"]))
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


def avoid_trap(possible_moves, body, board, my_snake):
    # make sure the chosen diretion has an escape route
    # is the path leading into an enclosed space smaller than us?
    smart_moves = []
    all_moves = ["up", "down", "left", "right"]
    safe_moves = get_safe_moves(possible_moves, body, board)
    safe_coords = {}
    hazard_coords = {}

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
        hazard_coords[guess] = [coord for coord in safe_coords[guess] if coord in board["hazards"]]

    for path in safe_coords.keys():
        #print (f"safe {path} coords: {safe_coords[path]}")
        guess_coord = get_next(body[0], path)
        print(f'This path will cost me {len(hazard_coords[path]) * 16} health, I have {my_snake["health"]}')
        if len(safe_coords[path]) >= len(body) and avoid_consumption(guess_coord, board["snakes"], my_snake) and len(hazard_coords[path]) * 16 < my_snake["health"]:
            smart_moves.append(path)
    
    if not smart_moves:
        # What if we try to chase our tail
        tail_neighbors = []
        tail_safe = get_safe_moves(possible_moves, [body[-1]], board)
        for tail_safe_direction in tail_safe:
            tail_neighbors.append(get_next(body[-1], tail_safe_direction))

        for path in safe_coords.keys():
            if any(coord in safe_coords[path] for coord in tail_neighbors):
                print("Chasing tail!!")
                smart_moves.append(path)

    # No clear path, try to fit ourselves in the longest one
    if safe_coords and not smart_moves:
        squeeze_move = max(safe_coords, key= lambda x: len(safe_coords[x]))
        if len(safe_coords[squeeze_move]) > 2 and avoid_consumption(get_next(body[0], squeeze_move), board["snakes"], my_snake):
            print(f'squeezing into {squeeze_move}')
            smart_moves.append(squeeze_move)


    hunger_threshold = 25

    # Seek food if there are other snakes larger than us, or if health is low
    if my_snake["health"] < hunger_threshold or any(snake["length"] >= my_snake["length"] for snake in board["snakes"] if snake["id"] != my_snake["id"]):
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

    if board["hazards"] and  len(smart_moves) > 1 and my_snake["head"] in board["hazards"]:
        # Choose the path that takes us out of hazard
        shortest_path = min([steps_to_safety(move, my_snake["head"], board) for move in smart_moves])
        smart_moves = [move for move in smart_moves if steps_to_safety(move, my_snake["head"], board) == shortest_path]
        print(f'going {shortest_path} moves towards {smart_moves} to escape hazards')


    return smart_moves

