from threading import Thread, RLock
from random import randrange
import json
import time
import copy


# Class that holds game data, progresses game, sends updates to players
class Snek:

    # Snek class constructor
    def __init__(self):
        # Initialize rlock,
        self.rlock = RLock()
        # Create world dict
        self.world = [100]
        # Initialize world dict
        self.world = [[{'state': 'empty', 'x': x, 'y': y} for x in range(100)] for y in range(100)]
        # Initialize list of players
        self.players = dict()
        # Initialize list of food
        self.food = []
        # Add 10 foods to the world
        for _ in range(10):
            self.add_food()
        # Start game thread
        Thread(target=self.tick).start()

    # Add player to game
    def add_player(self, connection, id, username):
        # Create player object
        player = dict()
        player['id'] = id
        player['connection'] = connection
        player['username'] = username
        player['direction'] = 'right'
        player['score'] = 5
        # Add player to players dict
        with self.rlock:
            self.players[username] = player
            # Initialize the players snek
            self.init_player_snek(username)

    # Remove player from game
    def remove_player(self, connection):
        with self.rlock:
            # Find player's segments
            segments_to_remove = None
            for player in self.players.values():
                if player['connection'] == connection:
                    segments_to_remove = player['segments']

            # Remove segments from world
            if segments_to_remove is not None:
                for segment in segments_to_remove:
                    self.world[segment['x']][segment['y']]['state'] = 'empty'

            # remove player from players list
            new_players = {k: v for k, v in self.players.items()
                           if v['connection'] != connection}
            self.players = new_players

    # Player lost so remove them and redirect to the losing screen
    def player_lost(self, id, scenario):
        if scenario == 0: # Player ran into the edge of the world
            msg = "You ran your snek into the edge of the world!"
        elif scenario == 1:  # Player ran into another snake
            msg = "You got SNEK-ed!"

        with self.rlock:
            self.players[id]['connection'].write_message(json.dumps({'lost': True, 'message': msg}))
            self.remove_player(self.players[id]['connection'])


    # Check if a player is in the game
    def player_is_in_game(self, username):
        with self.rlock:
            if username in self.players:
                return True
            else:
                return False

    # Add new player''s snek to world
    def init_player_snek(self, username):
        # Initialize snake:
        # - 5 segements long
        # - Location not near edge
        # - Traveling right
        # Redo until snake is not created on top of another snake

        bad_start = True
        while bad_start:
            start_x = randrange(10, 91)
            start_y = randrange(10, 91)

            with self.rlock:
                self.players[username]['direction'] = 'right'
                self.players[username]['segments'] = [
                    {
                        'x': start_x,
                        'y': start_y,
                    },
                    {
                        'x': start_x + 1,
                        'y': start_y,
                    },
                    {
                        'x': start_x + 2,
                        'y': start_y,
                    },
                    {
                        'x': start_x + 3,
                        'y': start_y,
                    },
                    {
                        'x': start_x + 4,
                        'y': start_y,
                    }
                ]

            # Check if snake is created on top of another snake or food
            bad_start = False
            with self.rlock:
                for segment in self.players[username]['segments']:
                    if self.world[segment['x']][segment['y']]['state'] != 'empty':
                        bad_start = True

        # After good start location is found, add player to world
        with self.rlock:
            for segment in self.players[username]['segments']:
                self.world[segment['x']][segment['y']]['state'] = self.players[username]['username']

    # Add a new food object to the game in an empty space away from the world edge
    def add_food(self):
        bad_start = True
        while bad_start:
            start_x = randrange(10, 91)
            start_y = randrange(10, 91)
            new_food = {'x': start_x,
                        'y': start_y}

            # Check if food is created on top of another snake or food
            bad_start = False
            with self.rlock:
                if self.world[new_food['x']][new_food['y']]['state'] != 'empty':
                    bad_start = True

        # After good location is found, add food to the world
        with self.rlock:
            self.world[new_food['x']][new_food['y']]['state'] = 'food'
            self.food.append(new_food)

    # Remove a food object from food list
    def remove_food(self, nx, ny):
        for f in self.food:
            with self.rlock:
                if f['x'] == nx and f['y'] == ny:
                    self.food.remove(f)

    # Progress game one cycle
    def tick(self):
        # continously update all players
        while True:
                # update the world
                self.progress_world()

                # send updates to all players
                for id, player in self.players.items():
                    with self.rlock:
                        try:
                            # Add all players to update message
                            data = {'players': {}, 'food': {}}
                            for p in self.players.values():
                                data['players'][p['id']] = {}
                                data['players'][p['id']]['username'] = p['username']
                                data['players'][p['id']]['segments'] = p['segments']
                                data['players'][p['id']]['direction'] = p['direction']
                                data['players'][p['id']]['score'] = p['score']

                            # Add all food to update message
                            data['food'] = self.food

                            # Send message
                            player['connection'].write_message(json.dumps(data))
                        except Exception as e:
                            print(e)

                # Wait before updating again
                time.sleep(.2)

    # Move all players snakes forward and handle collisions
    def progress_world(self):
        with self.rlock:
            # Grab old world status
            old_world = copy.copy(self.world)

        # Move each players snake
        for id, player in self.players.items():
            with self.rlock:
                direction = player['direction']

                # get head segment and its cords
                first_segment = player['segments'][-1]
                fx = first_segment['x']
                fy = first_segment['y']

            # create new segment to add to snake
            if (direction == 'up'):
                new_segment = {
                    'x': fx,
                    'y': fy-1,
                }
            elif(direction == 'right'):
                new_segment = {
                    'x': fx+1,
                    'y': fy,
                }
            elif (direction == 'down'):
                new_segment = {
                    'x': fx,
                    'y': fy+1,
                }
            elif (direction == 'left'):
                new_segment = {
                    'x': fx-1,
                    'y': fy,
                }

            # Grab new segments x and y cords
            nx = new_segment['x']
            ny = new_segment['y']

            # Player loses if they go out of bounds
            if nx == -1 or nx == 100 \
            or ny == -1 or ny == 100:
                self.player_lost(id, 0)
                return

            # The section the snek is going into
            section = old_world[nx][ny]['state']

            with self.rlock:
                # Player loses if they run into another snake
                # Check old world that was copied before snakes started moving in this tick
                if section is not 'empty' and section is not 'food':
                    self.player_lost(id, 1)
                    return

                # Player's snake gets longer if they eat food and the player gets another point
                get_longer = False
                if section is 'food':
                    get_longer = True
                    # increment player score
                    player['score'] += 1
                    self.remove_food(nx, ny)
                    self.add_food()

                if not get_longer:
                    # remove tail segment of players snake from their segments and the world
                    self.world[player['segments'][0]['x']][player['segments'][0]['y']]['state'] = 'empty'
                    player['segments'].pop(0)

                # Else player is good add there head segment to world
                self.world[nx][ny]['state'] = player['username']
                # Add new segment to players segments
                new_segments = player['segments'] + [new_segment]
                player['segments'] = new_segments

    # Handle message from client
    def receive_message(self, message):
        # Parse into json object
        json_msg = json.loads(message)

        # If direction update and player is in game, set new direction
        if json_msg['direction'] and self.player_is_in_game(json_msg['username']):
            with self.rlock:
                self.players[json_msg['username']]['direction'] = json_msg['direction']

