
DEBUG = 1

class Game:
    def __init__(self):
        self.board = Board()
        self.ended = False
        self.players = [Player(i) for i in range(2)]
        if (DEBUG): print(f"Created players: {self.players}")
        self.current_player = self.players[0]
    
    def next_turn(self):
        if (DEBUG): print(f"requesting move from: {self.current_player}")
        move = input("Whats ya move? ")
        print(move)
        move = self.validate_move(move)
    
    def validate_move(self, move):
        move_parts = move.split()
        if not (len(move_parts) == 3 or len(move_parts) == 5):
            print("Incorrect number of args")
            return 1
        if not move_parts[0] in ['place', 'move']:
            print(f"Invalid move {move_parts[0]}")
            err = 2
        try:
            pos_x_from = int(move_parts[1])
        except:
            print("pos_x_from was not an int")
            err = 1
        try:
            pos_y_from = int(move_parts[2])
        except:
            print("pos_y_from was not an int")
            err = 1
        if not err == 2 and move_parts[0] == 'move':
            try:
                pos_x_to = int(move_parts[3])
            except:
                print("pos_x_to was not an int")
                err = 1
            try:
                pos_y_to = int(move_parts[4])
            except:
                print("pos_y_to was not an int")
                err = 1
        
        if err:
            return None
        elif move_parts[2] == 'place':
            return (move_parts[2], pos_x_from, pos_y_from)
        else:
            return (move_parts[2], pos_x_from, pos_y_from, pos_x_to, pos_y_to)


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
