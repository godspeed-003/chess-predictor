import chess
def evaluate_board(board):
    if board.is_checkmate():
        return -9999 if board.turn == chess.WHITE else 9999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    # Material count (centipawns)
    material = sum(
        len(board.pieces(piece_type, color)) * value
        for piece_type, value in [(chess.PAWN, 100), (chess.KNIGHT, 300), (chess.BISHOP, 300),
                                 (chess.ROOK, 500), (chess.QUEEN, 900)]
        for color in [chess.WHITE, chess.BLACK]
    )
    return material if board.turn == chess.WHITE else -material