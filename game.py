
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
            if (DEBUG): print(f"requesting move from: {self.current_player}")
            move_input = input(f"Whats ya move ({self.current_player})? ")
            move_cmd = self.validate_move_cmd(move_input)
            if move_cmd:
                valid_move = True
            print("")

        # Change player
        if self.current_player == self.players[0]:
            self.current_player = self.players[1]
        else:
            self.current_player = self.players[0]
    
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
            return (move_parts[0], x0, y0)
        return (move_parts[0], x0, y0, x1, y1)


class Board:
    def __init__(self):
        self.board = [] # [ (piece, pos_x, pos_y), ... ]

    def add_piece(self, piece, pos_x, pos_y, player):
        # Check the piece isn't already on the board
        for p in self.board:
            if p.id == piece.id:
                return 1
        
        # Check that it is next to another piece on the board
        # and that there are no pieces of the oppositie team around it
        surr_pieces = self.surrounding_pieces(self.board, piece, pos_x, pos_y)
        for p in surr_pieces:
            if len(surr_pieces) == 0:
                return 1
            if p.player != player:
                return 1
        self.board.append((piece, pos_x, pos_y))
        return 0

    def surrounding_pieces(self, board, piece, pos_x, pos_y):
        surr_positions = [
            (pos_x,     pos_y + 1),
            (pos_x + 1, pos_y    ),
            (pos_x + 1, pos_y - 1),
            (pos_x,     pos_y - 1),
            (pos_x - 1, pos_y - 1),
            (pos_x - 1, pos_y    ),
        ]
        for p in self.board:
            if p[1:] in surr_positions:
                if (DEBUG): print("Got one")
        return []


class Piece():
    def __init__(self, id):
        self.id = id
        self.name = f"Piece{self.id}"

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


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
            pieces.append(Piece(id_count)) # grasshopper 
            id_count += 1
            pieces.append(Piece(id_count)) # ant
            id_count += 1
            pieces.append(Piece(id_count)) # spider
            id_count += 1
        for _ in range(2):
            pieces.append(Piece(id_count)) # beetle
            id_count += 1
        pieces.append(Piece(id_count))     # queen bee
        id_count += 1
        return pieces


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
