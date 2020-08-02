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

def get_safe_moves(possible_moves, body, board):

    safe_moves = []

    for guess in possible_moves:
        guess_coord = get_next(body[0], guess)
        if avoid_walls(guess_coord, board["width"], board["height"]) and avoid_snakes(guess_coord, board["snakes"]):
            safe_moves.append(guess)
        elif guess_coord == body[-1]:
            # The tail is also a safe place to go
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
        if future_head in snake["body"]:
            return False
    return True

def avoid_trap(possible_moves, body, board):
    # make sure the chosen diretion has an escape route
    # is the path leading into an enclosed space smaller than us?
    smart_moves = []
    safe_moves = get_safe_moves(possible_moves, body, board)
    safe_coords = {}

    # We know these directions are safe... for now
    for guess in safe_moves:
        safe_coords[guess] = []
        guess_coord = get_next(body[0], guess)

        for segments in body:
            safe = get_safe_moves(possible_moves, [guess_coord], board)
            for safe_move in safe:
                guess_coord_next = get_next(guess_coord, safe_move)
                if guess_coord_next not in safe_coords[guess]:
                    safe_coords[guess].append(guess_coord_next)

            for safe_coord in safe_coords[guess]:
                safe = get_safe_moves(possible_moves, [safe_coord], board)
                for safe_move in safe:
                    guess_coord = get_next(safe_coord, safe_move)
                    if guess_coord not in safe_coords[guess]:
                        safe_coords[guess].append(guess_coord)


    for path in safe_coords.keys():
        if len(safe_coords[path]) >= len(body):
            smart_moves.append(path)

    if not smart_moves:
        # Uh oh, we're out of good ideas.  What if we try to chase our tail
        tail_neighbors = []
        tail_safe = get_safe_moves(possible_moves, [body[-1]], board)
        for tail_safe_direction in tail_safe:
            tail_neighbors.append(get_next(body[-1], tail_safe_direction))

        for path in safe_coords.keys():
            if any(coord in safe_coords[path] for coord in tail_neighbors):
                print("Chasing tail!!")
                smart_moves.append(path)


    print(f"Safe Coords: {safe_coords}")
    print(f"Are we smart? {smart_moves}")

    return smart_moves

