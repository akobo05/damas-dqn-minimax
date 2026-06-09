from __future__ import annotations
from typing import Any

State  = dict[str, Any]
Action = tuple[int, ...]
 
def _build_neighbors() -> list[dict[str, int | None]]:
    """Para cada casilla devuelve sus 4 vecinos diagonales (None = fuera)."""
    neighbors: list[dict[str, int | None]] = []
    for sq in range(32):
        row = sq // 4
        col_in_row = sq % 4          # 0..3, índice dentro de la fila
        even_row = (row % 2 == 0)
 
        if row == 0:
            ul = ur = None
        elif even_row:              
            ul = sq - 4             
            ur = sq - 3
        else:                      
            ul = sq - 5
            ur = sq - 4
 
        if row == 7:
            dl = dr = None
        elif even_row:
            dl = sq + 4
            dr = sq + 5
        else:
            dl = sq + 3
            dr = sq + 4
 
        if col_in_row == 0:
            if even_row:
                pass         
            else:
                ul = None
                dl = None
        if col_in_row == 3:
            if even_row:
                ur = None
                dr = None
 
        neighbors.append({"ul": ul, "ur": ur, "dl": dl, "dr": dr})
    return neighbors
 
NEIGHBORS = _build_neighbors()
 
 
def _promotion_row(turn: int) -> set[int]:
    """Casillas de la última fila para el jugador dado."""
    if turn == 1:   
        return {28, 29, 30, 31}
    else:           
        return {0, 1, 2, 3}

def legal_moves(state: State) -> list[Action]:
    board = state["board"]
    turn  = state["turn"]
 
    moves: list[Action] = []
 
    for sq in range(32):
        piece = board[sq]
        if piece == 0 or (piece > 0) != (turn > 0):
            continue
 
        nb = NEIGHBORS[sq]
        is_king = abs(piece) == 2
 
        if turn == 1:         
            dirs = ["dl", "dr"]
        else:      
            dirs = ["ul", "ur"]
 
        if is_king:
            dirs = ["ul", "ur", "dl", "dr"]
 
        for d in dirs:
            dest = nb[d]
            if dest is not None and board[dest] == 0:
                moves.append((sq, dest))
 
    return moves

def step(state: State, action: Action) -> State:
    if action not in legal_moves(state):
        raise ValueError(f"Acción ilegal: {action}")
 
    board = list(state["board"])
    turn  = state["turn"]
    src, dst = action[0], action[-1]
 
    piece = board[src]
    board[src] = 0
 
    if dst in _promotion_row(turn) and abs(piece) == 1:
        piece = 2 * turn   # 2 o -2
 
    board[dst] = piece
 
    return {
        "board": board,
        "turn": -turn,
        "no_capture_count": state["no_capture_count"] + 1,
    }
 

def is_terminal(state: State) -> bool:
    if state["no_capture_count"] >= 80:
        return True
    return len(legal_moves(state)) == 0
 
 
def result(state: State) -> int | None:
    if not is_terminal(state):
        return None
    if state["no_capture_count"] >= 80:
        return 0
    return -state["turn"]


def encode(state: State) -> list[float]:
    board = state["board"]
    turn  = state["turn"]
    channels = [
        [1.0 if v ==  1 else 0.0 for v in board],  # piezas rojas 
        [1.0 if v ==  2 else 0.0 for v in board],  # damas rojas
        [1.0 if v == -1 else 0.0 for v in board],  # piezas negras 
        [1.0 if v == -2 else 0.0 for v in board],  # damas negras
        [float(turn)] * 32,                        # turno (1 o -1)
    ]
    return [x for ch in channels for x in ch]

def initial_state() -> State:
    board = [0] * 32
    for i in range(12):
        board[i] = 1
    for i in range(20, 32):
        board[i] = -1
    return {"board": board, "turn": 1, "no_capture_count": 0}