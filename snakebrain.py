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

def get_reverse(move):
    reverse_moves = {"left":"right","right":"left","up":"down","down":"up"}
    return reverse_moves[move]

def get_safe_moves(possible_moves, body, board, squadmates = None, my_snake = None):

    safe_moves = []
    
    for guess in possible_moves:
        guess_coord = get_next(body[0], guess)
        if avoid_walls(guess_coord, board["width"], board["height"]) and avoid_snakes(guess_coord, board["snakes"]): 
            safe_moves.append(guess)
        elif len(body) > 1 and guess_coord == body[-1] and guess_coord not in body[:-1]:
           # The tail is also a safe place to go... unless there is a non-tail segment there too
           safe_moves.append(guess)
        if squadmates and my_snake:
            for snake in squadmates:
                if guess_coord in snake["body"][1:] and guess_coord not in my_snake["body"][:-1]:
                    safe_moves.append(guess)
    return safe_moves

def avoid_walls(future_head, board_width, board_height):
    result = True

    x = int(future_head["x"])
    y = int(future_head["y"])

    if x < 0 or y < 0 or x >= board_width or y >= board_height:
        result = False

    return result

def avoid_snakes(future_head, snake_bodies):
    for snake in snake_bodies:
        if future_head in snake["body"][:-1]:
            return False
    return True

def avoid_consumption(future_head, snake_bodies, my_snake):
    if len(snake_bodies) < 2:
        return True

    my_length = my_snake["length"]
    for snake in snake_bodies:
        if snake == my_snake:
            continue
        if future_head in get_all_moves(snake["head"]) and future_head not in snake["body"][1:] and my_length <= snake["length"]:
            print(f'DANGER OF EATED {my_snake["head"]}->{future_head} by {snake["name"]}')
            return False
    return True

def avoid_food(future_head, food):
    return future_head not in food

def avoid_hazards(future_head, hazards):
    # Convenience method
    return not future_head in hazards

def get_minimum_moves(start_coord, targets):
    # This could probably be a lambda but I'm not that smart
    steps = []
    for coord in targets:
        steps.append(abs(coord["x"] - start_coord["x"]) + abs(coord["y"] - start_coord["y"]))
    return min(steps)

def get_closest_enemy_head_distance(head_coord, other_snakes):
    steps = [100]
    for snake in other_snakes:
        steps.append(abs(snake["head"]["x"] - head_coord["x"]) + abs(snake["head"]["y"] - head_coord["y"]))
    return min(steps)

def get_closest_enemy(head_coord, other_snakes):
    retval = []
    distance = get_closest_enemy_head_distance(head_coord, other_snakes)
    for snake in other_snakes:
        if abs(snake["head"]["x"] - head_coord["x"]) + abs(snake["head"]["y"] - head_coord["y"]) == distance:
            retval.append(snake)
    return retval

def get_body_segment_count(coord, move, snakes):
    retval = 0
    for snake in snakes:
        for segment in snake["body"]:
            if move == 'up' and segment['y'] > coord['y']:
                retval += 1
            elif move == 'down' and segment['y'] < coord['y']:
                retval += 1
            elif move == 'right' and segment['x'] > coord['x']:
                retval += 1
            elif move == 'left' and segment['x'] < coord['x']:
                retval += 1
    print(f'{move} body weight is {retval}')
    return retval

def should_choose(moves, squad):
    if squad:
        return len(moves) >= 2
    else:
        return len(moves) == 2

def line_to_safety(direction, start, board):
    # either straight into a wall or into the safe zone
    retval = 0
    next_coord = get_next(start, direction)
    while next_coord in board["hazards"] and avoid_walls(next_coord, board["width"], board["height"]):
        next_coord = get_next(next_coord, direction)
        retval += 1
    if not avoid_walls(next_coord, board["width"], board["height"]):
        retval += max([board["width"], board["height"]]) + 1
    return retval

def steps_to_safety(direction, start, board):
    # Trace a path to safety
    escape_route = [get_next(start, direction)]
    next_coord = escape_route[0]
    extra_cost = 0
    while next_coord in board["hazards"] and avoid_walls(next_coord, board["width"], board["height"]) and extra_cost == 0 and len(escape_route) < 100:
        costs = {}
        # Really need to choose a new direction now
        for choice in get_safe_moves([move for move in ["up", "down", "left", "right"] if move != get_reverse(direction)], escape_route, board):
            costs[choice] = line_to_safety(choice, get_next(next_coord, choice), board)
        if costs:
            bestway = min(costs.values())
            for choice in costs.keys():
                if costs[choice] == bestway:
                    direction = choice
        next_coord = get_next(next_coord, direction)
        if next_coord in escape_route:
            extra_cost += len(escape_route)
        else:
            escape_route.insert(0, next_coord)
    if not avoid_walls(next_coord, board["width"], board["height"]):
        extra_cost += max([board["width"], board["height"]])
#    print(f'in hazard, overhead to explore {direction} is {extra_cost}, path is {escape_route}')
    return len(escape_route) + extra_cost

def at_wall(coord, board):
    return coord["x"] == 0 or coord["y"] == 0 or coord["x"] == board["width"] - 1 or coord["y"] == board["height"] - 1

def avoid_crowd(moves, enemy_snakes, my_snake):
    crowd_cost = {}
    
    # Perhaps there's a clever way to create a dictionary of functions, but I want to be able to read this tomorrow
    if 'up' in moves:
        others = [snake for snake in enemy_snakes if snake['head']['y'] > my_snake['head']['y']]
        threats = [snake for snake in others if snake['length'] > my_snake['length'] and get_minimum_moves(my_snake['head'], [snake['head']]) <= 4]
        crowd_cost['up'] = len(others) + (len(threats) * 3)
    if 'down' in moves:
        others = [snake for snake in enemy_snakes if snake['head']['y'] < my_snake['head']['y']]
        threats = [snake for snake in others if snake['length'] > my_snake['length'] and get_minimum_moves(my_snake['head'], [snake['head']]) <= 4]
        crowd_cost['down'] = len(others) + (len(threats) * 3)
    if 'left' in moves:
        others = [snake for snake in enemy_snakes if snake['head']['x'] < my_snake['head']['x']]
        threats = [snake for snake in others if snake['length'] > my_snake['length'] and get_minimum_moves(my_snake['head'], [snake['head']]) <= 4]
        crowd_cost['left'] = len(others) + (len(threats) * 3)
    if 'right' in moves:
        others = [snake for snake in enemy_snakes if snake['head']['x'] > my_snake['head']['x']]
        threats = [snake for snake in others if snake['length'] > my_snake['length'] and get_minimum_moves(my_snake['head'], [snake['head']]) <= 4]
        crowd_cost['right'] = len(others) + (len(threats) * 3)
    
    print(f'Crowd control: {crowd_cost}')
    return [move for move in moves if crowd_cost[move] == min(crowd_cost.values())]

def is_drafting(my_snake, other_snake):
    neck = my_snake["body"][1]
    if abs(other_snake["head"]["x"] - my_snake["head"]["x"]) > 1:
        return False
    if abs(other_snake["head"]["y"] - my_snake["head"]["y"]) > 1:
        return False
    return other_snake["head"]["x"] == neck["x"] or other_snake["head"]["y"] == neck["y"]

def continue_draft(moves, my_snake, other_snake):
    retval = []
    neck = my_snake["body"][1]
    if other_snake["head"]["x"] < my_snake["head"]["x"] and neck["x"] == other_snake["head"]["x"]:
        retval.append("right")
    if other_snake["head"]["x"] > my_snake["head"]["x"] and neck["x"] == other_snake["head"]["x"]:
        retval.append("left")
    if other_snake["head"]["y"] < my_snake["head"]["y"] and neck["y"] == other_snake["head"]["y"]:
        retval.append("up")
    if other_snake["head"]["y"] > my_snake["head"]["y"] and neck["y"] == other_snake["head"]["y"]:
        retval.append("down")
    return [move for move in moves if move in retval]

def get_smart_moves(possible_moves, body, board, my_snake):
    # the main function of the snake - choose the best move based on the information available
    smart_moves = []
    food_avoid = []
    enemy_snakes = []
    squadmates = []
    all_moves = ["up", "down", "left", "right"]
    other_snakes = [snake for snake in board["snakes"] if snake["id"] != my_snake["id"]]
    if my_snake.get("squad"):
        enemy_snakes = [snake for snake in other_snakes if snake["squad"] != my_snake["squad"]]
        squadmates = [snake for snake in other_snakes if snake["squad"] == my_snake["squad"]]
    else:
        enemy_snakes = other_snakes
    safe_moves = get_safe_moves(possible_moves, body, board, squadmates, my_snake)

    # enemy_threats = [snake for snake in other_snakes if snake["length"] >= my_sname["length"]]
    eating_snakes = []
    safe_coords = {}
    head_distance = {}
    next_coords = {}

    hunger_threshold = 35

    # We know these directions are safe... for now
    for guess in safe_moves:
        #print(f"exploring {guess}")
        safe_coords[guess] = []
        guess_coord = get_next(body[0], guess)
        next_coords[guess] = guess_coord
        explore_edge = [guess_coord]
        all_coords = [guess_coord]
        next_explore = []
        explore_step = 0

        for segments in body[:-1]:
            next_explore.clear()
            explore_step += 1
            for explore in explore_edge:
                safe = get_safe_moves(all_moves, [explore], board, squadmates, my_snake)
                #print(f"Safe moves: {safe}")
                for safe_move in safe:
                    guess_coord_next = get_next(explore, safe_move)
                    if guess_coord_next not in all_coords:
                        next_explore.append(guess_coord_next)
                
                # Consider how other snakes move
                # TODO: Handle when other snakes could eat
                snake_collide = [coord for coord in get_all_moves(explore) if not avoid_snakes(coord, enemy_snakes)]
                if snake_collide:
                    for coord in snake_collide:
                        for snake in enemy_snakes:
                            if coord in snake["body"] and snake["body"].index(coord) + explore_step >= len(snake["body"]):
                                start_segment = snake["body"].index(coord)
                                all_coords += snake["body"][start_segment:]
                self_collide = [coord for coord in get_all_moves(explore) if not avoid_snakes(coord, [my_snake])]
                if self_collide:
                    for coord in self_collide:
                        if coord in my_snake['body'] and my_snake['body'].index(coord) + explore_step >= len(my_snake['body']):
                            start_segment = my_snake["body"].index(coord)
                            all_coords += my_snake['body'][start_segment:]
                all_coords += next_explore.copy() 
                all_coords.append(explore)
            explore_edge = next_explore.copy()

        safe_coords[guess] += list(map(dict, frozenset(frozenset(i.items()) for i in all_coords)))

    for path in safe_coords.keys():
        guess_coord = get_next(body[0], path)
        #print(f'considering {path}, {len(safe_coords[path])} safe coords, {len(body)} body length, consumption {avoid_consumption(guess_coord, board["snakes"], my_snake)} hazards {avoid_hazards(guess_coord, board["hazards"])}')
        # TODO: also consider tails that are overlapping bodies, but more than 1 step away
        if ((len(safe_coords[path]) >= len(body) or 
                any(snake["body"][-1] in safe_coords[path] for snake in board["snakes"])) and 
                avoid_consumption(guess_coord, board["snakes"], my_snake) and
                avoid_hazards(guess_coord, board["hazards"])
            ):
            smart_moves.append(path)
    
    # check if other snakes are being forced to move into a square we can occupy.  
    # We don't need to determine if this is a safe move since we can use the freed-up
    # space for future moves
    for snake in other_snakes:
        enemy_options = get_safe_moves(all_moves, snake['body'], board)
        if len(enemy_options) == 1:
            enemy_must = get_next(snake['body'][0], enemy_options[0])
            if snake['length'] < my_snake['length'] and enemy_must in next_coords.values():
                for move, coord in next_coords.items():
                    if coord == enemy_must:
                        print(f'Eating {snake["name"]} by going {move} to {coord}')
                        eating_snakes.append(move)
        elif len(enemy_options) >= 2:
            for enemy_move in enemy_options:
                enemy_may = get_next(snake['body'][0], enemy_move)
                if snake['length'] < my_snake['length'] and enemy_may in next_coords.values():
                    for move, coord in next_coords.items():
                        if coord == enemy_may and len(get_safe_moves(all_moves, [coord], board)) > 0 and not at_wall(coord, board) and len(safe_coords[move]) > my_snake['length']:
                            print(f'Trying to eat {snake["name"]} by going {move}')
                            eating_snakes.append(move)

    if not smart_moves and my_snake['head'] not in board['hazards']:
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
                for snake in other_snakes:
                    if test_move == snake["body"][-1] and test_move not in body[:-1] and not any(coord in board["food"] for coord in get_all_moves(snake["body"][0])):
                        smart_moves.append(move)

    # No clear path, try to fit ourselves in the longest one
    if safe_coords and not smart_moves and my_snake['head'] not in board ['hazards']:
        if other_snakes:
            # consider enemies
            escape_plan = {}
            for snake in other_snakes:
                if abs(my_snake['head']['x'] - snake['head']['x']) <= 2 and abs(my_snake['head']['y'] - snake['head']['y']) <= 2:
                    for move in safe_coords.keys():
                        escape_plan[move] = len(get_safe_moves(all_moves, [get_next(my_snake['head'], move)], board))
            if escape_plan:
                for move in escape_plan.keys():
                    if escape_plan[move] == max(escape_plan.values()) and move not in smart_moves:
                        print(f'going {move}, there are {escape_plan[move]} options')
                        smart_moves.append(move)
        if not smart_moves:
            # TODO: find the longest contiguous path in the safe zones to decide which way to squeeze
            squeeze_move = max(safe_coords, key= lambda x: len(safe_coords[x]))
            if len(safe_coords[squeeze_move]) > 2 and avoid_consumption(get_next(body[0], squeeze_move), board["snakes"], my_snake):
                print(f'squeezing into {squeeze_move} {safe_coords}')
                smart_moves.append(squeeze_move)

    # tiebreakers when there are two paths, three in squads.  Skop if begin of game and we're short
    if not eating_snakes and len(board['snakes']) > 1 and should_choose(smart_moves, my_snake.get("squad")) and len(my_snake['body']) > 3:
        body_weight = {}
        for move in smart_moves:
            next_coord = get_next(body[0], move)
            head_distance[move] = get_closest_enemy_head_distance(next_coord, enemy_snakes)
            body_weight[move] = get_body_segment_count(next_coord, move, board['snakes'])

        if min(head_distance.values()) <= 3:
            if at_wall(my_snake["head"], board) and not at_wall(my_snake["body"][1], board):
                if board["hazards"]:
                    hazard_avoid = [move for move in smart_moves if not any(coord in board["hazards"] for coord in safe_coords[move])]
                    if hazard_avoid:
                        smart_moves = hazard_avoid
                        print(f'avoiding hazards {hazard_avoid}')
                if len(smart_moves) > 1:
                    smart_moves = avoid_crowd(smart_moves, enemy_snakes, my_snake)
            else:
                enemy_threats = get_closest_enemy(my_snake["head"], [snake for snake in other_snakes if snake['length'] > my_snake['length']])
                if len(enemy_threats) == 1 and is_drafting(my_snake, enemy_threats[0]):
                    # Try to push enemy into wall, hopefully corner
                    eating_snakes = continue_draft(smart_moves, my_snake, enemy_threats[0])
                    print(f'Drafting {enemy_threats[0]["name"]} {smart_moves}')
                else:
                    smart_moves = [move for move in smart_moves if head_distance[move] == max(head_distance.values())]
                    print(f'choosing {smart_moves} to avoid heads {head_distance}')
                    if len(smart_moves) > 1 and at_wall(my_snake["head"], board):
                        smart_moves = [move for move in smart_moves if not at_wall(get_next(body[0], move), board)]
                        print(f'choosing {smart_moves} to bump self off wall')
                    if len(smart_moves) > 1:
                        escape_plan = {}
                        for move in smart_moves:
                            escape_plan[move] = len(get_safe_moves(all_moves, [get_next(my_snake['head'], move)], board))
                        smart_moves = [move for move in escape_plan.keys() if escape_plan[move] == max(escape_plan.values())]
                        print(f'choosing {smart_moves} because there are {max(escape_plan.values())} ways out')
                    if len(smart_moves) > 1:
                        smart_moves = [move for move in smart_moves if body_weight[move] == min(body_weight.values())]
                        print(f'choosing {smart_moves} to avoid bodies {body_weight}')


    # Seek food if there are other snakes larger than us, or if health is low
    if len(smart_moves) > 1 and board['food'] and not eating_snakes and (my_snake["health"] < hunger_threshold or any(snake["length"] >= my_snake["length"] for snake in enemy_snakes)):
        print("Hungry!")
        food_choices = smart_moves 
        food_moves = {}
        closest_food = []
        greed_moves = []
        avoid_moves = []
        food_targets = [food for food in board["food"] if food not in board["hazards"]]
        print(f'food is {food_targets}')
        if not food_targets:
            food_targets = board["food"]
            print (f'no food outside hazards, now considering {food_targets}')

        if my_snake['health'] < hunger_threshold or my_snake["length"] < board['width']:
            food_choices = safe_coords.keys()

        for path in food_choices:
            if any(food in safe_coords[path] for food in food_targets):
                food_moves[path] = get_minimum_moves(get_next(body[0], path), food_targets)

        if food_moves:
            closest_food_distance = min(food_moves.values())
            food_considerations = other_snakes
            if squadmates and my_snake['name'] == min([snake['name'] for snake in board['snakes'] if snake['squad'] == my_snake['squad']]):
                print("short snake takes the food")
                food_considerations = enemy_snakes
            for path in food_moves.keys():
                if food_moves[path] <= closest_food_distance:
                    print(f"safe food towards {path} is {closest_food_distance} or less")
                    closest_food.append(path)
                    # see if we're the closest to the food
                    #if head_distance.get(path) and food_moves[path] < head_distance[path]:
                    for food in food_targets:
                        distance_to_me = get_minimum_moves(food, [my_snake["head"]])
                        if distance_to_me == food_moves[path] + 1:
                            for snake in food_considerations:
                                if get_minimum_moves(food, [snake["head"]]) <= distance_to_me and get_minimum_moves(snake["head"], [my_snake["head"]]) <= 4 and snake["length"] >= my_snake["length"]:
                                    # Don't
                                    print(f'Avoiding food towards {path} because of {snake["name"]}')
                                    avoid_moves.append(path)
                    if not (path in avoid_moves):
                        greed_moves.append(path)
        else:
            for path in food_choices:
                food_moves[path] = get_minimum_moves(get_next(body[0], path), food_targets)
            if food_moves:
                closest_food_distance = min(food_moves.values())
                for path in food_moves.keys():
                    if food_moves[path] <= closest_food_distance:
                        print(f"unsafe food towards {path} is {closest_food_distance} or less")
                        closest_food.append(path)
        
        if closest_food:

            if my_snake["health"] < hunger_threshold or greed_moves:
                print("Blinded by hunger or greed")
                hazard_avoid = [move for move in closest_food if get_next(body[0], move) not in board['hazards']]
                if hazard_avoid:
                    if greed_moves:
                        # should probably intersect hazard_avoid and greed_moves
                        print(f"choosing greed: {greed_moves}")
                        smart_moves = greed_moves
                    else:
                        print("but staying safe")
                        smart_moves = hazard_avoid
                else:
                    smart_moves = closest_food
            else:
                food_intersect = [move for move in smart_moves if move in closest_food and move not in avoid_moves] 
                print(f'Smart food is {food_intersect}')
                if food_intersect:
                    smart_moves = food_intersect
                elif avoid_moves:
                    smart_moves = [move for move in smart_moves if move not in avoid_moves]
                elif min(food_moves.values()) * 16 < my_snake["health"]: #and if path in hazard
                    # we're gonna make it, chief
                    hazard_pay = [move for move in closest_food if get_next(body[0], move) in board['hazards']]
                    if hazard_pay:
                        print('Diving into danger!')
                        smart_moves = hazard_pay
    else:
        # avoid food if it's there to avoid
        if len(smart_moves) > 1 and board["food"]:
            food_avoid = [move for move in smart_moves if get_next(body[0], move) not in board["food"]]
            print(f'Not hungry, avoiding food! moves are {food_avoid}')

    if board["hazards"] and my_snake["head"] in board["hazards"]:
        # Choose the path that takes us out of hazard
        if not smart_moves:
            print(f'no moves, using {safe_coords.keys()}')
            smart_moves = list(safe_coords.keys())
        if smart_moves and len(smart_moves) > 1:
            shortest_path = min([steps_to_safety(move, my_snake["head"], board) for move in smart_moves])
            smart_moves = [move for move in smart_moves if steps_to_safety(move, my_snake["head"], board) == shortest_path]
            print(f'smartly going {shortest_path} {smart_moves} steps to escape hazards')
    elif eating_snakes:
        smart_moves = eating_snakes
    elif food_avoid:
        smart_moves = food_avoid


    return smart_moves

