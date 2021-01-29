import pytest
import game

def test_true():
    assert True


@pytest.fixture
def new_game():
    return game.Game()


def save_board_into_file(filename, board_string):
    with open(filename, 'w') as f:
        f.write(board_string)


def compare_files(expected, actual):
    with open(expected, 'r') as f:
        text_expected = f.read()
    with open(actual, 'r') as f:
        text_actual = f.read()
    assert text_expected == text_actual


@pytest.mark.parametrize("expected_file,moves_list", [
    (
        "simple_moving_ant.test",
        [
            ['place', 'player0', 0 ,  0, 11],
            ['place', 'player1', 0 , -1, 11],
            ['place', 'player0', 0 ,  1,  0],
            ['place', 'player0', 1 ,  2,  1],
            ['move' , 'player0', 0 , -2,  1],
        ]
    ),
    (
        "ant_out_of_gap.test",
        [
            ['place', 'player0', 0 ,  0, 11],
            ['place', 'player1', 0 , -1, 11],
            ['place', 'player0', 0 ,  1,  0],
            ['place', 'player0', 1 ,  2,  1],
            ['place', 'player0', 1 ,  3,  2],
            ['place', 'player0', 0 ,  3,  3],
            ['place', 'player0', 0 ,  2,  4],
            ['place', 'player0',-1 ,  3,  5],
            ['move' , 'player0', 0 , -2,  4],
        ]
    ),
    (
        "ant_across_gap.test",
        [
            ['place', 'player0', 0 ,  0, 11],
            ['place', 'player1', 0 , -1, 11],
            ['place', 'player0', 0 ,  1,  0],
            ['place', 'player0', 1 ,  2,  1],
            ['place', 'player0', 1 ,  3,  2],
            ['place', 'player0', 0 ,  3,  3],
            ['place', 'player0', 0 ,  4,  4],
            ['place', 'player0',-1 ,  3,  5],
            ['move' , 'player0', 0 , -2,  4],
        ]
    ),
    (
        "spider.test",
        [
            ['place', 'player0', 0 ,  0, 11],
            ['place', 'player1', 0 , -1, 11],
            ['place', 'player0', 0 ,  1,  0],
            ['place', 'player0', 1 ,  2,  1],
            ['place', 'player0', 1 ,  3,  2],
            ['place', 'player0', 0 ,  3,  3],
            ['place', 'player0', 0 ,  4,  8],
            ['place', 'player0',-1 ,  3,  5],
            ['move' , 'player0', 0 , -2,  8],
        ]
    ),
    (
        "grasshopper_moves_3_times.test",
        [
            ['place', 'player0', 0 ,  0, 11],
            ['place', 'player1', 0 , -1, 11],
            ['place', 'player0', 0 ,  1,  0],
            ['place', 'player0', 1 ,  1,  8],
            ['place', 'player0', 2 ,  0,  9],
            ['move' , 'player0', 0 , -2,  0],
            ['move' , 'player0', 0 ,  1,  0],
            ['move' , 'player0', 3 ,  0,  0],
        ]
    ),
    (
        "queen_bee.test",
        [
            ['place', 'player0', 0 ,  0, 11],
            ['place', 'player1', 0 , -1, 11],
            ['place', 'player0', 0 ,  1,  0],
            ['place', 'player0', 1 ,  1,  8],
            ['place', 'player0', 2 ,  0,  9],
            ['move' , 'player1', 1 ,  0, 11],
        ]
    ),
    (
        "beetle_move.test",
        [
            ['place', 'player0', 0 ,  0, 11],
            ['place', 'player1', 0 , -1, 11],
            ['place', 'player0', 0 ,  1,  0],
            ['place', 'player0', 1 ,  1,  8],
            ['place', 'player0', 2 ,  0, 10],
            ['move' , 'player0', 1 ,  0, 10],
            ['move' , 'player0', 1 ,  1, 10],
            ['move' , 'player0', 0 ,  1, 10],
            ['move' , 'player0', -1,  2, 10],
        ]
    ),
    (
        "spider_2.test",
        [
            ['place', 'player0', 0 ,  0, 11],
            ['place', 'player1', 1 ,  0, 11],
            ['place', 'player0', 0 ,  1,  8],
            ['place', 'player1', 2 , -1,  2],
        ]
    ),
    (
        "beetle_stack.test",
        [
            ['place', 'player0', 0 ,  0, 10],
            ['place', 'player1', 1 ,  0, 10],
            ['place', 'player0', 0 ,  1,  9],
            ['place', 'player1', 2 , -1,  9],
            ['move' , 'player0', 0 ,  0,  9],
            ['move' , 'player1', 1 ,  0,  9],
            ['move' , 'player0', 1 ,  0,  9],
            ['place', 'player0', 2 ,  0,  8],
            ['place', 'player1', 1 , -1,  8],
        ]
    ),
    (
        "player_loses.test",
        [
            ['place', 'player0', 0 ,  0, 10],
            ['place', 'player1', 1 ,  0, 10],
            ['place', 'player0', -1,  1, 11],
            ['place', 'player0', 0 ,  1,  9],
            ['place', 'player0', -1,  2,  8],
            ['place', 'player0', -2,  1,  7],
            ['place', 'player0', -2,  0,  6],
            ['place', 'player0', -1 , 0,  5],
        ]
    )
], ids=["simple_moving_ant", "ant_out_of_gap", "ant_across_gap",
        "spider", "grasshopper_moves_3_times", "queen_bee", "beetle_move", "spider_2",
        "beetle_stack", "player_loses"])
def test_moves(new_game, expected_file, moves_list):
    for move_type, player, x, y, piece_no in moves_list:
        player_object = new_game.players[{"player0": 0, "player1": 1}[player]]
        if move_type == 'place':
            new_game.board.add_piece(player_object.pieces[piece_no], x, y, player_object)
        else:
            new_game.board.move_piece(player_object.pieces[piece_no], x, y)
    save_board_into_file(expected_file + '.actual', str(new_game.board))
    compare_files(expected_file, expected_file + '.actual')
