
import json

DEBUG = 0
PIECE_NAMES = [
    'ant',
    'spider',
    'beetle',
    'bee',
    'grasshopper',
]
RULES = """
Hey gamers! This is hive and here's the lowdown.
Place pieces on the hexagonal grid and move them around.
OBJECTIVE: Surround the other players queen bee.
PIECES: Each player has these pieces
- 1 queen bee
- 3 ants
- 3 grasshoppers
- 2 spiders
- 2 beetles
MOVES:
* bee - move one position
* ant - move anywhere around the hive
* grasshopper - jump in a straight line across any number of pieces
                (except 0 pieces) until the next empty position
* spider - move around the hive three positions
* beetle - move one space either around the hive or on top of the hive.
            The piece underneath cannot move. The piece on top will assume
            the colour of the tile.
RULES:
* You can't break the hive. Before you move a piece, if you lift it from
    the board and its splits the hive in two, you cannot move that piece.
* Must place the queen bee on or before your 4th move.
* When you place a piece, it cannot be touching the oppositions piece.
* You cannot move to a position the hexagonal piece can't slide into.

HOW TO PLAY:
You have two options, 'move' and 'place'
place piece_name x y
move x_piece y_piece x_destination y_destination
- piece_name, includes: bee, spider, grasshopper, ant, beetle
- x, y, are printed on the board with the piece
        - y is vertical
        - x is horizontal but every second position is slighty down
"""

class Game:
    def __init__(self):
        self.board = Board()
        self.ended = False
        self.players = [Player(i) for i in range(2)]
        if (DEBUG): print(f"Created players: {self.players}")
        self.current_player = self.players[0]

        # if not DEBUG: print(RULES)

    def export_json(self, return_json=False):
        game_json = {'players': []}
        for player in self.players:
            game_json['players'].append(player.export_json(return_json=True))
        game_json['ended'] = self.ended
        game_json['board'] = self.board.export_json(return_json=True)
        game_json['current_player_id'] = self.current_player.id
        if return_json:
            return game_json
        return json.dumps(game_json)

    def import_json(self, import_json):
        self.players = [Player(0).import_json(player, self) for player in import_json['players']]
        self.board = Board().import_json(import_json['board'], self)
        self.ended = import_json['ended']
        self.board = import_json['board']
        for player in self.players:
            if player.id == import_json['current_player_id']:
                self.current_player = player
                break
    
    def next_turn(self):
        valid_move = False
        while not valid_move:
            valid_move_cmd = False
            while not valid_move_cmd:
                if (DEBUG): print(f"requesting move from: {self.current_player}")
                move_input = input(f"Whats ya move ({self.current_player})? ")
                move_cmd = self.validate_move_cmd(move_input)
                if move_cmd:
                    valid_move_cmd = True
                print("")

            # The move must be valid according to game logic
            if move_cmd[0] == 'place':
                piece_type = move_cmd[1]
                x_dest = move_cmd[2]
                y_dest = move_cmd[3]

                # The board will bug if you don't place at 0 0 on the first move
                if self.current_player.turn_count == 0 and \
                        (x_dest or y_dest) and \
                        self.current_player == self.players[0]:
                    print("place at 0 0 for the first move otherwise itll bug a bit :O")
                    continue
                piece = self.current_player.get_piece_by_available(piece_type)
                if piece == None:
                    print("That player doesn't have anymore of those pieces available")
                    continue
                if self.current_player.turn_count == 3 and not self.current_player.played_queen and not piece_type == 'bee':
                    print("You need to play the queen bee on or before your 4th move.")
                    continue
                if not self.board.add_piece(piece, x_dest, y_dest, self.current_player):
                    print("Invalid move for that piece")
                    continue
                else:
                    valid_move = True
                    # Was this the queen bee
                    if piece_type == 'bee':
                        self.current_player.played_queen = True
                print(self.board)
            else:
                # 'move' was chosen
                x_init = move_cmd[1]
                y_init = move_cmd[2]
                x_dest = move_cmd[3]
                y_dest = move_cmd[4]
                piece = self.board.get_piece_at_this_position(x_init, y_init)
                if piece:
                    # This piece must below to this player
                    if not piece.player_id == self.current_player.id:
                        print("You can't move the other players piece, dude!")
                        continue
                    valid_move = self.board.move_piece(piece, x_dest, y_dest)
                    print(self.board)
                else:
                    print("There was no piece at this position")
                pass
            print("")

        # Change player
        self.current_player.turn_count += 1
        if self.current_player == self.players[0]:
            self.current_player = self.players[1]
        else:
            self.current_player = self.players[0]

        # Check game end
        # If there are any positions free around the queen bee
        # than this player has not lost the game
        game_over_directions = ['1', '2', '3', '4', '5', '6']
        player_lost = True
        surrounded_bees = []
        for player in self.players:
            for p in player.pieces:
                if p.type == 'bee':
                    for dir in game_over_directions:
                        if not p.surr_pieces[dir]:
                            player_lost = False
                            break
                    if player_lost:
                        surrounded_bees.append(player)
                    break
        if len(surrounded_bees):
            game.ended = True
            # Detect a draw
            if len(surrounded_bees) > 1:
                print("It was a draw, you both lost. iiidiots")
            else:
                print(f"Player {surrounded_bees[0]} lost")

    def validate_move_cmd(self, move):
        """
        Valid move commands:
            "place piece x0 y0"
            "move x0 y0 x1 y1"

        returns move tuple, None if invalid
        """
        move_parts = move.split()
        if not len(move_parts) in [4, 5]:
            print("Incorrect number of args")
            return None
        if not move_parts[0] in ['place', 'move']:
            print(f"Invalid move {move_parts[0]}")
            return None

        if move_parts[0] == 'place':
            if not len(move_parts) == 4:
                print("Incorrect number of args for 'place'")
                return None
            if not move_parts[1] in PIECE_NAMES:
                print(f"Invalid piece {move_parts[1]}")
                return None
            try:
                x0 = int(move_parts[2])
                y0 = int(move_parts[3])
            except ValueError:
                print("Move position must be an integer")
                return None

        if move_parts[0] == 'move':
            if not len(move_parts) == 5:
                print("Incorrect number of args for 'move'")
                return None
            try:
                x0 = int(move_parts[1])
                y0 = int(move_parts[2])
                x1 = int(move_parts[3])
                y1 = int(move_parts[4])
            except ValueError:
                print("Move position must be an integer")
                return None

        if move_parts[0] == 'place':
            return (move_parts[0], move_parts[1], x0, y0)
        return (move_parts[0], x0, y0, x1, y1)


class Board:
    """                     
                 (0,1)   (2,1)
            (-1,1)   (1,1)   (3,1)
       (-2,0)    (0,0)   (2,0)
            (-1,0)   (1,0)   (3,0)
      (-2,-1)   (0,-1)   (2,-1)
                     (1,-1)
    """
    def __init__(self):
        self.board = [] # [ [piece, pos_x, pos_y], ... ]

    def export_json(self, return_json=False):
        board_json = []
        for piece_status in self.board:
            board_json.append({
                                'piece_id': piece_status[0].id,
                                'x': piece_status[1],
                                'y': piece_status[2],
                            })
        if return_json:
            return board_json
        return json.dumps(board_json)

    def import_json(self, board_json, game):
        self.board = []
        for piece_status in board_json:
            self.board.append([None, piece_status['x'], piece_status['y']])
            for player in game.players:
                for piece in player.pieces:
                    if piece.id == piece_status['piece_id']:
                        self.board[-1][0] = piece
                        break

    def add_piece(self, piece, pos_x, pos_y, player):
        # Check the piece isn't already on the board
        for p in self.board:
            if p[0].id == piece.id:
                print("Piece is already on the board")
                return False

        # Check the position is available
        if self.piece_at_this_position(pos_x, pos_y):
            print("This position isn't available")
            return False
        
        # Check that it is next to another piece on the board
        # and that there are no pieces of the opposite team around it
        # Special cases are:
        # - this is the first piece placed therfore doesn't require
        #   another piece next to it
        # - this is the second piece placed therefore it can be next to
        #   another players piece
        surr_pieces = self.surrounding_pieces(pos_x, pos_y)
        if len(surr_pieces) == 0 and len(self.board) > 0:
            print("There are no surrounding pieces")
            return False
        if len(self.board) > 1:
            for p in surr_pieces:
                if p.player_id != player.id or p.surr_pieces['top']:
                    # If the top piece is this players piece, then it can be placed here
                    # Also, if the top piece isn't this players piece, then it can't be
                    # played here
                    top_piece = p
                    while not top_piece.surr_pieces['top'] is None:
                        top_piece = top_piece.surr_pieces['top']
                    if top_piece.player_id != player.id:
                        print("You can't place your piece next to the opponents piece")
                        return False

        # Update piece, surrounding pieces, and board
        self.board.append([piece, pos_x, pos_y])
        piece.pos_x = pos_x
        piece.pos_y = pos_y
        piece.in_play = True
        for p in surr_pieces:
            p.add_piece_to_surr_pieces(piece, vice_versa=True)
        return True

    def move_piece(self, piece, dest_x, dest_y):        
        if DEBUG: print(f"Moving {piece} to ({dest_x},{dest_y})")
        new_surr_pieces = self.surrounding_pieces(dest_x, dest_y, include_vertical=True, exclude_pieces=[piece])
        # Moving this piece cannot break the hive
        if not piece.surr_pieces['bottom'] and self.check_break_hive(piece):
            print("Broke the hive")
            return False
        # Must not break away from the hive
        if not len(new_surr_pieces):
            print("Cannot move away from hive")
            return False
        # A beetle on top will prevent it from moving
        if not piece.surr_pieces['top'] is None:
            print("You have a beetle on you, no way you can move!")
            return False
        
        # See if this new position is possible for the piece
        # print(f"Going to move {piece} with surr_pieces {piece.surr_pieces}")
        if piece.valid_move(self, dest_x, dest_y):
            # Unlink this piece from its current pieces
            piece.detach_surr_pieces()
            # Update position
            piece.pos_x = dest_x
            piece.pos_y = dest_y
            # Link this piece with its new pieces
            for p in new_surr_pieces:
                # We need to know if any of these new pieces are on top
                # or even on the bottom
                # If this piece has a piece on top then we won't be able
                # to attach to this piece
                # Any other instance we may as well place_on_bottom because
                # only a beetle will be able to use this function for on
                # top of another piece.
                if p.surr_pieces['top']: continue
                p.add_piece_to_surr_pieces(piece, vice_versa=True, place_on_bottom=True)
        else:
            print(f"Cannot move {piece} from ({piece.pos_x},{piece.pos_y}) to ({dest_x},{dest_y})")
            return False
            
        return True

    def check_break_hive(self, piece):
        # Each surrounding piece must be able to reach each other surrounding piece
        for _, piece_start in piece.surr_pieces.items():
            if piece_start == None: continue
            for _, piece_end in piece.surr_pieces.items():
                if piece_end == None: continue
                # print(f"BreakHive: Can {piece_start} make it to {piece_end}")
                if not self.breadth_first_search(piece, piece_start, piece_end):
                    return True
        return False

    def breadth_first_search(self, missing_piece, piece_start, piece_end):
        # List of pieces already checked. The missing piece should not be included.
        checked_pieces = [missing_piece]
        # Queue for the breadth first search. First in last out.
        queue = [piece_start]

        # End once we've found the end piece
        while True:
            if len(queue):
                target_piece = queue.pop()
            else:
                return False
            if target_piece.id == piece_end.id:
                return True
            else:
                # This piece has now been checked
                checked_pieces.append(target_piece)
                # Add all the surrounding pieces to the queue
                for _, val in target_piece.surr_pieces.items():
                    if not val == None and not val in checked_pieces:
                        queue = [val] + queue

    def surrounding_pieces(self, pos_x, pos_y, include_vertical=False, exclude_pieces=None):
        # This is beetle compatible IF include_vertical is correctly chosen
        if not pos_x % 2:
            surr_positions = [
                [pos_x,     pos_y + 1],
                [pos_x + 1, pos_y + 1],
                [pos_x + 1, pos_y    ],
                [pos_x,     pos_y - 1],
                [pos_x - 1, pos_y    ],
                [pos_x - 1, pos_y + 1],
            ]
        else:
            surr_positions = [
                [pos_x,     pos_y + 1],
                [pos_x + 1, pos_y    ],
                [pos_x + 1, pos_y - 1],
                [pos_x,     pos_y - 1],
                [pos_x - 1, pos_y - 1],
                [pos_x - 1, pos_y    ],
            ]
        # If we are checking vertical pieces then we need to check this position
        if include_vertical:
            surr_positions.append([pos_x, pos_y])

        surr_pieces = []
        for p, _, _ in self.board:
            if [p.pos_x, p.pos_y] in surr_positions:
                if (DEBUG): print(f"{p} is a surrounding piece")
                if not exclude_pieces is None and p in exclude_pieces: continue
                surr_pieces.append(p)
        return surr_pieces

    def piece_at_this_position(self, pos_x, pos_y):
        for p in self.board:
            if p[1:] == [pos_x, pos_y]: # p[1:] -> [pos_x, pos_y]
                if (DEBUG): print("This place is taken")
                return True
        return False

    def get_piece_at_this_position(self, pos_x, pos_y):
        for p, _, _ in self.board:
            if [p.pos_x, p.pos_y] == [pos_x, pos_y]:
                if (DEBUG): print("This place is taken")
                # We shouldn't return a piece which has something above it
                if p.surr_pieces['top']: continue
                return p
        return False

    def __repr__(self):
        # Find max and min x and y coords
        x_min, x_max, y_min, y_max = (self.board[0][0].pos_x, self.board[0][0].pos_x, self.board[0][0].pos_y, self.board[0][0].pos_y)
        for p, _, _ in self.board:
            if p.pos_x < x_min:
                x_min = p.pos_x
            if p.pos_x > x_max:
                x_max = p.pos_x
            if p.pos_y < y_min:
                y_min = p.pos_y
            if p.pos_y > y_max:
                y_max = p.pos_y

        width = x_max - x_min + 1
        height = y_max - y_min + 1
        # Width - 1 + 4 * pieces
        # Height - 1 + 2 * pieces
        def print_around(board, pos_x, pos_y, token, x_val=None, y_val=None, under_piece=None):
            #  01234
            # 0 ___
            # 1/ P \ 
            # 2\___/
            border = [
                ['/' , pos_x    , pos_y + 1],
                ['_' , pos_x + 1, pos_y    ],
                ['_' , pos_x + 2, pos_y    ],
                ['_' , pos_x + 3, pos_y    ],
                ['\\', pos_x + 4, pos_y + 1],
                ['/' , pos_x + 4, pos_y + 2],
                ['_' , pos_x + 1, pos_y + 2],
                ['_' , pos_x + 2, pos_y + 2],
                ['_' , pos_x + 3, pos_y + 2],
                ['\\', pos_x    , pos_y + 2],
                [token, pos_x +2 , pos_y + 1],
            ]

            # Print negative positions as blue
            if not x_val is None:
                if x_val < 0:
                    border[6][0] = '\033[36m' + str(x_val)[-1] + '\033[37m'
                else:
                    border[6][0] = str(x_val)[-1]
            if not y_val is None:
                if y_val < 0:
                    border[8][0] = '\033[36m' + str(y_val)[-1] + '\033[37m'
                else:
                    border[8][0] = str(y_val)[-1]
            if under_piece:
                border[7][0] = under_piece.token
            for char, x, y in border:
                if board[y][x] in [' ','_']: board[y][x] = char
            return board

        board_width = 1 + width * 4
        board_height = 2 + 2 * height
        board = []
        for i in range(board_height):
            board.append([])
            for _ in range(board_width):
                board[i].append(" ")

        for p, _, _ in self.board:
            y = (p.pos_y - y_max) * -2 + p.pos_x % 2
            x = (p.pos_x - x_min) * 4
            if not p.surr_pieces['top']:
                print_around(board, x, y, p.token, x_val=p.pos_x, y_val=p.pos_y, under_piece=p.surr_pieces['bottom'])
        
        return '\n'.join(''.join(line) for line in board) + '\n'

    def __str__(self):
        return self.__repr__()


class Piece():
    def __init__(self, id, type, player_id):
        self.player_id = player_id
        self.id = id + player_id * 100
        self.name = f"Piece{self.id}"
        if type in PIECE_NAMES:
            self.type = type
        else:
            print("Wrong piece type. this object is invalid")
        self.in_play = False
        self.surr_pieces = {
            '1': None,
            '2': None,
            '3': None,
            '4': None,
            '5': None,
            '6': None,
            'top': None,
            'bottom': None,
        }
        self.pos_x = None
        self.pos_y = None
        self.assign_board_token()

    def export_json(self, return_json=False):
        piece_json = {
            'player_id': self.player_id,
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'in_play': self.in_play,
            'surr_pieces_ids': {},
            'pos_x': self.pos_x,
            'pos_y': self.pos_y,
            'token': self.token,
        }
        for surr_position, piece in self.surr_pieces.items():
            piece_json['surr_pieces_ids'][surr_position] = None if piece == None else piece.id
        if return_json:
            return piece_json
        return json.dumps(piece_json)

    def import_json(self, piece_json, game, link_piece_objects=False):
        self.player_id = piece_json['player_id']
        self.id = piece_json['id']
        self.name = piece_json['name']
        self.type = piece_json['type']
        self.in_play = piece_json['in_play']
        for surr_position, piece_id in piece_json['surr_pieces_ids'].items():
            self.surr_pieces[surr_position] = None if piece_id == None else piece_id
        if link_piece_objects:
            for key, piece_id in self.surr_pieces.items():
                for player in game.players:
                        for piece in player.pieces:
                            if piece.id == piece_id:
                                self.surr_pieces[key] = piece
                                break
        self.pos_x = piece_json['pos_x']
        self.pos_y = piece_json['pos_y']
        self.token = piece_json['token']
        return self

    def __str__(self):
        return f"{self.name}:{self.type}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if type(other) == type(self):
            if other.id == self.id:
                return True
        return False
    
    def assign_board_token(self):
        if self.player_id == 0:
            self.token = '\033[37m'
        else:
            self.token = '\033[31m'
        if   self.type == 'bee':
            self.token += 'Q'
        elif self.type == 'spider':
            self.token += 'S'
        elif self.type == 'beetle':
            self.token += 'B'
        elif self.type == 'grasshopper':
            self.token += 'G'
        elif self.type == 'ant':
            self.token += 'A'
        
        self.token += '\033[37m'

    def add_piece_to_surr_pieces(self, piece, vice_versa=False, place_on_bottom=False):
        """                     
                  (0,1)   (2,1)
             (-1,1)   (1,1)   (3,1)
        (-2,0)    (0,0)   (2,0)
             (-1,0)   (1,0)   (3,0)
        (-2,-1)   (0,-1)   (2,-1)
                      (1,-1)
        """
        # This is beetle compatible BUT you must check specifically
        # if the piece you are attaching is not on the bottom of another
        # piece and that this piece is meant to be on the top of the
        # target piece 'piece'.
        pos_x = self.pos_x
        pos_y = self.pos_y
        if not pos_x % 2:
            surr_positions = [  # [pos_x_relative, pos_y_relative, key]
                [pos_x,     pos_y + 1, '1'], # position 1
                [pos_x + 1, pos_y + 1, '2'], # position 2
                [pos_x + 1, pos_y    , '3'], # position 3
                [pos_x,     pos_y - 1, '4'], # position 4
                [pos_x - 1, pos_y    , '5'], # position 5
                [pos_x - 1, pos_y + 1, '6'], # position 6
                [pos_x,     pos_y    , 'top'], # position top
            ]
        else:
            surr_positions = [  # [pos_x_relative, pos_y_relative, key]
                [pos_x,     pos_y + 1, '1'], # position 1
                [pos_x + 1, pos_y    , '2'], # position 2
                [pos_x + 1, pos_y - 1, '3'], # position 3
                [pos_x,     pos_y - 1, '4'], # position 4
                [pos_x - 1, pos_y - 1, '5'], # position 5
                [pos_x - 1, pos_y    , '6'], # position 6
                [pos_x,     pos_y    , 'top'], # position top
            ]
        for pos in surr_positions:
            if pos[0:2] == [piece.pos_x, piece.pos_y]:
                # We want to place this piece on top of the other
                # piece. Otherwise treat it as normal.
                if place_on_bottom and pos[2] == 'top':
                    self.surr_pieces['top'] = piece
                    piece.surr_pieces['bottom'] = self
                    return
                else:
                    self.surr_pieces[pos[2]] = piece
                if vice_versa:
                    piece.add_piece_to_surr_pieces(self, vice_versa=False)
                return

    def detach_surr_pieces(self):
        # This is beetle compatible

        # First check if this piece has a top and bottom piece.
        # In this case we want to attach these pieces together
        # before complete seperation.
        if self.surr_pieces['top'] and self.surr_pieces['bottom']:
            self.surr_pieces['top'].surr_pieces['bottom'] = self.surr_pieces['bottom'].surr_pieces['top']
            self.surr_pieces['bottom'].surr_pieces['top'] = self.surr_pieces['top'].surr_pieces['bottom']
            self.surr_pieces['top'] = None
            self.surr_pieces['bottom'] = None
        # Go through each surrounding piece and remove the link
        for dir, p in self.surr_pieces.items():
            if p is None: continue
            # Now get the surrounding piece and remove its reference
            # to this piece
            for dir_other, p_other in p.surr_pieces.items():
                if p_other is None: continue
                if p_other.id == self.id:
                    # print(f'Detaching {self} from {p}')
                    p.surr_pieces[dir_other] = None
            self.surr_pieces[dir] = None

    
    def valid_move(self, board, dest_x, dest_y):

        # Keep the pieces location saved just in case it is changed
        # through validation
        init_pos_x = self.pos_x
        init_pos_y = self.pos_y
        init_surr_pieces = self.surr_pieces
        def revert_to_init():
            self.pos_x = init_pos_x
            self.pos_y = init_pos_y
            self.surr_pieces = init_surr_pieces

        # This will let you know if the move isn't valid.
        # If it is, it will also move there and there is no follow up action.
        if self.type == 'ant':
            valid = self.move_along_board(board, dest_x=dest_x, dest_y=dest_y)
        elif self.type == 'spider':
            valid = self.move_along_board(board, count=3, dest_x=dest_x, dest_y=dest_y)
        elif self.type == 'grasshopper':
            valid = self.jump_across_board(board)
        elif self.type == 'bee':
            valid = self.move_along_board(board, count=1, dest_x=dest_x, dest_y=dest_y)
        elif self.type == 'beetle':
            valid = self.move_across_board(board, dest_x=dest_x, dest_y=dest_y)
                
        revert_to_init()
        return valid

    def can_move_out(self, move_out_dir_key):
        side_combinations = { # target key: [left key, right key]
            '1': ['6', '2'],
            '2': ['1', '3'],
            '3': ['2', '4'],
            '4': ['3', '5'],
            '5': ['4', '6'],
            '6': ['1', '5'],
        }
        dir_key = side_combinations[move_out_dir_key]
        if self.surr_pieces[dir_key[0]] is None or \
                self.surr_pieces[dir_key[1]] is None:
            return True
        else:
            return False

    def possible_moves(self):
        # This is beetle compatible because this should never
        # need to know what piece is on top of other pieces.
        side_combinations = { # target key: [left key, right key]
            '1': ['6', '2'],
            '2': ['1', '3'],
            '3': ['2', '4'],
            '4': ['3', '5'],
            '5': ['4', '6'],
            '6': ['5', '1'],
            'top': ['1', '2', '3', '4', '5', '6'], # Unneeded
        }
        move_locations = []
        # Go through surrounding pieces
        # print("surr pieces", self.surr_pieces)
        for dir, p in self.surr_pieces.items():
            if not p is None and not dir == 'top':
                # Check either side of this piece to see if you can move there
                for adjacent_position in side_combinations[dir]:
                    if self.surr_pieces[adjacent_position] is None:
                        if DEBUG: print(f"Found a possible position to move attached to piece {dir} and empty space {adjacent_position}")
                        # This place is vacant. Can I fit here?
                        if self.can_move_out(adjacent_position):
                            move_locations.append(adjacent_position)
        return list(set(move_locations))

    def move_along_board(self, board, count=None, dest_x=None, dest_y=None):
        """
        Find whether you can reach your end destination.
        If you are looking for a count, returns a list of possible positions.
        If you are looking for a destination, will return bool, True if reachable.
        """
        # This is beetle compatible because it doesn't need to know top pieces.

        def temp_move_pos(board, position):
            #DEBUG stuff
            tmp_x = self.pos_x
            tmp_y = self.pos_y

            # Set new position
            self.pos_x = position.x
            self.pos_y = position.y

            # Reset the pieces to none
            for key, _ in self.surr_pieces.items():
                self.surr_pieces[key] = None

            # Add the surrounding pieces for the new position
            new_surr_pieces = board.surrounding_pieces(position.x, position.y)

            if DEBUG: print(f"Moving around board from ({tmp_x},{tmp_y}) to ({self.pos_x},{self.pos_y})")
            if DEBUG: print(f"Now surrounded by {new_surr_pieces}")
            for p in new_surr_pieces:
                self.add_piece_to_surr_pieces(p, vice_versa=False)
            return new_surr_pieces

        # To navigate around the board we need to do a depth first search
        # until we find the destination position. A stack (list) will contain
        # the positions travelled to and the depth in their search. The depth
        # is required because we need to know when a spider has moved three
        # space.
        move_stack = [(Position(self.pos_x, self.pos_y), 0)]
        checked_positions = []
        stack_depth = 0
        count_positions = []

        def found_dest(position, stack_depth):
            # Are we going a specific number of steps?
            # Or until we reach a specific position?
            if count and count > 0:
                if DEBUG: print(f"The piece has moved {stack_depth} times")
                if stack_depth == count:
                    count_positions.append(Position(self.pos_x, self.pos_y))
                    # We want to find all other possible positions for this count
                    # So never return True for when we have count
                    return None
            elif not dest_x is None and not dest_y is None and count is None:
                # Is this the destination?
                return position.x == dest_x and position.y == dest_y
            return False
        
        # Depth first search
        # Each loop will check the last element in the stack for the destination.
        # If it isn't found, all surrounding positions for that piece which haven't
        # already been checked are added to the stack.
        while len(move_stack):
            # Pop the last position and move there
            tmp_x = self.pos_x
            tmp_y = self.pos_y
            last_position, stack_depth = move_stack.pop()
            if DEBUG: print(f"Around the board moving from ({tmp_x},{tmp_y}) to {last_position}, now at stack depth {stack_depth}")
            temp_move_pos(board, last_position)
            if DEBUG: print(board)
            # Check the position of the last element in the stack
            dest = found_dest(last_position, stack_depth)
            if dest:
                return dest
            else:
                # Add this position to the checked list
                checked_positions.append(last_position)
                # Add all possible surrounding movements
                next_moves = self.possible_moves()
                if not len(next_moves):
                    print("It would be a bug to get here as you cannot move \
                        into a spot you cant get out of")
                    return False
                else:
                    # Add each move if it hasn't already been checked
                    if not count is None and count <= stack_depth:
                        if DEBUG: print(f"The positions after {last_position} will exceed the move count, {count} <= {stack_depth}")
                        continue
                    for dir in next_moves:
                        next_x, next_y = self.direction_position(dir)
                        if DEBUG: print(f"Have I checked {Position(next_x, next_y)}. Is it in:\n{checked_positions}")
                        if not Position(next_x, next_y) in checked_positions:
                            move_stack.append((Position(next_x, next_y), stack_depth + 1))
        
        # Return final validation result
        if count is None:
            return False
        else:
            if DEBUG: print(f"Validation result: is ({dest_x}, {dest_y}) in {count_positions}")
            return Position(dest_x, dest_y) in count_positions

    def jump_across_board(self, board):
        """
        Can jump in six directions. Can only jump in a direction if there
        is a piece there. Has to jump to the next available location.
        """
        # This is beetle compatible because it doesn't need to know top pieces.

        # Save the possible positions
        viable_jump = []
        # Check each surrounding position
        for dir, piece in self.surr_pieces.items():
            if dir == 'top': continue
            # Keep finding an opposite piece until there is an empty space
            previous_piece = None
            while True:
                # Is this spot empty
                if piece is None:
                    # If it had no piece before it then it isn't a valid move
                    if previous_piece == None:
                        if DEBUG: print(f"Cannot move in this direction {dir}")
                        break
                    else:
                        viable_jump.append(Position(previous_piece.pos_x, previous_piece.pos_y))
                        break
                # Find the next piece along
                previous_piece = piece
                piece = piece.surr_pieces[dir]
        return viable_jump

    def move_across_board(self, board, dest_x=None, dest_y=None):
        """
        Can move in any direction one place. Can move on top another piece.
        Can move on top a piece which is already on top another piece.
        """
        # It has already been checked that the move doesn't break the hive
        # meaning that we just need to move the piece to where it needs to go.
        print("Trying to go to", (dest_x, dest_y))
        for dir, _ in self.surr_pieces.items():
            # print("Position around beetle", self.direction_position(dir))
            if self.direction_position(dir) == (dest_x, dest_y):
                # print(f"Beetle can move here {piece}")
                return True
        return False


    def direction_position(self, dir):
        # This is beetle compatible because it returns surrounding coords.
        pos_x = self.pos_x
        pos_y = self.pos_y
        if not pos_x % 2:
            surr_positions = [  # [pos_x_relative, pos_y_relative, key]
                [pos_x,     pos_y + 1, '1'], # position 1
                [pos_x + 1, pos_y + 1, '2'], # position 2
                [pos_x + 1, pos_y    , '3'], # position 3
                [pos_x,     pos_y - 1, '4'], # position 4
                [pos_x - 1, pos_y    , '5'], # position 5
                [pos_x - 1, pos_y + 1, '6'], # position 6
                [pos_x,     pos_y    , 'top'], # position top
            ]
        else:
            surr_positions = [  # [pos_x_relative, pos_y_relative, key]
                [pos_x,     pos_y + 1, '1'], # position 1
                [pos_x + 1, pos_y    , '2'], # position 2
                [pos_x + 1, pos_y - 1, '3'], # position 3
                [pos_x,     pos_y - 1, '4'], # position 4
                [pos_x - 1, pos_y - 1, '5'], # position 5
                [pos_x - 1, pos_y    , '6'], # position 6
                [pos_x,     pos_y    , 'top'], # position top
            ]
        for x, y, direction in surr_positions:
            if direction == dir:
                return (x, y)


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return f"({self.x},{self.y})"
    def __eq__(self, other):
        if not type(other) == type(self):
            return False
        return self.x == other.x and self.y == other.y

class Player:
    def __init__(self, id):
        self.name = f"Player{id}"
        self.id = id
        self.pieces = self.init_pieces()
        if (DEBUG): print(f"Created pieces for {self.name}: {self.pieces}")
        self.turn_count = 0
        self.played_queen = False

    def export_json(self, return_json=False):
        player_json = {}
        player_json['name'] = self.name
        player_json['id'] = self.id
        player_json['turn_count'] = self.turn_count
        player_json['played_queen'] = self.played_queen
        player_json['pieces'] = [p.export_json(return_json=True) for p in self.pieces]
        if return_json:
            return player_json
        return json.dumps(player_json)

    def import_json(self, import_json, game):
        self.name = import_json['name']
        self.id = import_json['id']
        self.turn_count = import_json['turn_count']
        self.played_queen = import_json['played_queen']
        self.pieces = []
        for piece_json in import_json['pieces']:
            self.pieces.append(Piece(0, 'bee', 0).import_json(piece_json, None, link_piece_objects=False))
        for piece_json in import_json['pieces']:
            self.pieces.append(Piece(0, 'bee', 0).import_json(piece_json, game, link_piece_objects=True))
        return self

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def init_pieces(self):
        pieces = []
        id_count = 0
        for _ in range(3):
            pieces.append(Piece(id_count, 'grasshopper', self.id)) # grasshopper 
            id_count += 1
            pieces.append(Piece(id_count, 'ant', self.id)) # ant
            id_count += 1
            pieces.append(Piece(id_count, 'spider', self.id)) # spider
            id_count += 1
        for _ in range(2):
            pieces.append(Piece(id_count, 'beetle', self.id)) # beetle
            id_count += 1
        pieces.append(Piece(id_count, 'bee', self.id))     # queen bee
        id_count += 1
        return pieces

    def get_piece_by_available(self, piece_type):
        for piece in self.pieces:
            if piece.type == piece_type:
                if piece.in_play:
                    continue
                else:
                    return piece
        return None


def game_loop(game):
    debug_count = 7
    while not game.ended and debug_count:
        game.next_turn()
        game.board.export_json()
        # debug_count -= 1
    
    return 0


if __name__ == "__main__":
    game = Game()
    ret_code = game_loop(game)
    exit(ret_code)
