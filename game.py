
DEBUG = 1
PIECE_NAMES = [
    'ant',
    'spider',
    'beetle',
    'bee',
    'grasshopper',
]

class Game:
    def __init__(self):
        self.board = Board()
        self.ended = False
        self.players = [Player(i) for i in range(2)]
        if (DEBUG): print(f"Created players: {self.players}")
        self.current_player = self.players[0]
    
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
            if self.validate_move():
                if move_cmd[0] == 'place':
                    piece = self.current_player.get_piece_by_available(move_cmd[1])
                    if piece == None:
                        print("That player doesn't have anymore of those pieces available")
                        continue
                    if not self.board.add_piece(piece, move_cmd[2], move_cmd[3], self.current_player):
                        print("Invalid move for that piece")
                        continue
                    else:
                        valid_move = True
                    # print(self.board)
                else:
                    # 'move' the piece
                    pass
            print("")

        # Change player
        if self.current_player == self.players[0]:
            self.current_player = self.players[1]
        else:
            self.current_player = self.players[0]
    
    def validate_move(self):
        return True

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
        # and that there are no pieces of the oppositie team around it
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
                if p.player_id != player.id:
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

    def surrounding_pieces(self, pos_x, pos_y):
        surr_positions = [
            [pos_x,     pos_y + 1],
            [pos_x + 1, pos_y    ],
            [pos_x + 1, pos_y - 1],
            [pos_x,     pos_y - 1],
            [pos_x - 1, pos_y - 1],
            [pos_x - 1, pos_y    ],
        ]
        surr_pieces = []
        for p in self.board:
            if p[1:] in surr_positions: # p[1:] -> [pos_x, pos_y]
                if (DEBUG): print(f"{p} is a surrounding piece")
                surr_pieces.append(p[0])
        return surr_pieces         

    def piece_at_this_position(self, pos_x, pos_y):
        for p in self.board:
            print(p)
            if p[1:] == [pos_x, pos_y]: # p[1:] -> [pos_x, pos_y]
                if (DEBUG): print("This place is taken")
                return True
        return False

    def __repr__(self):
        # Find max and min x and y coords
        x_min, x_max, y_min, y_max = (self.board[0][1], self.board[0][1], self.board[0][2], self.board[0][2])
        board = ""
        for p in self.board:
            if p[1] < x_min:
                x_min = p[1]
            if p[1] > x_max:
                x_max = p[1]
            if p[2] < y_min:
                y_min = p[1]
            if p[2] > y_max:
                y_max = p[1]

        board_x_list = [5*' '] * (x_max - x_min + 1)
        board_list = [[]] * (y_max - y_min + 1)
        for i in board_list: board_list[i] = board_x_list
        for p in self.board:
            board_list[p[1] - x_min][p[2] - y_min] = p[0].name[0]
        """
        B   Q   G
          A   S
        """
        for j in range(y_min, y_max + 1):
            for i in range(x_min, x_max + 1):
                # Space at the beginning to offset the hex shape
                board += 5 * ' ' * (y_max - j)
                board += board_list[i][j]
                

            board += 'END\n'
        print (x_min, x_max, y_min, y_max)
        # print(board)
        return board

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
        }
        self.pos_x = None
        self.pos_y = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def add_piece_to_surr_pieces(self, piece, vice_versa=False):
        """                     
                  (0,1)   (2,1)
             (-1,1)   (1,1)   (3,1)
        (-2,0)    (0,0)   (2,0)
             (-1,0)   (1,0)   (3,0)
        (-2,-1)   (0,-1)   (2,-1)
                      (1,-1)
        """
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
        print("THIS PIECE", [piece.pos_x, piece.pos_y])
        for pos in surr_positions:
            print("SEARCHING FOR", pos[0:2])
            if pos[0:2] == [piece.pos_x, piece.pos_y]:
                self.surr_pieces[pos[2]] = piece
                print(self.surr_pieces)
                print("Found it ", pos[2])
                if vice_versa:
                    
                    piece.add_piece_to_surr_pieces(self, vice_versa=False)
                return


class Player:
    def __init__(self, id):
        self.name = f"Player{id}"
        self.id = id
        self.pieces = self.init_pieces()
        if (DEBUG): print(f"Created pieces for {self.name}: {self.pieces}")

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
    debug_count = 3
    while not game.ended and debug_count:
        game.next_turn()
        debug_count -= 1
    
    return 0


if __name__ == "__main__":
    game = Game()
    ret_code = game_loop(game)
    exit(ret_code)
