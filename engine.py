import chess
import chess.engine
import math
import os
from io import StringIO
import chess.pgn
from typing import List, Dict, Any

class ChessAnalyzer:
    def __init__(self, stockfish_path: str):
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        self.engine.configure({"Hash": 256, "Threads": 2})

    def cp_to_win_pct(self, cp: int) -> float:
        """Chess.com's official Win Probability formula."""
        return 100 / (1 + math.exp(-0.00368208 * cp))

    def get_material_score(self, board: chess.Board):
        values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3.1, chess.ROOK: 5, chess.QUEEN: 9}
        w = 0
        b = 0
        for pt, val in values.items():
            w += len(board.pieces(pt, chess.WHITE)) * val
            b += len(board.pieces(pt, chess.BLACK)) * val
        return {"w": w, "b": b}

    def analyze_game(self, pgn_string: str, depth: int = 14) -> Dict[str, Any]:
        game = chess.pgn.read_game(StringIO(pgn_string))
        if not game:
            return {"evals": [], "classifications": []}
            
        board = game.board()
        moves = list(game.mainline_moves())
        
        # Initial evaluation
        info = self.engine.analyse(board, chess.engine.Limit(depth=depth))
        prev_cp = info["score"].white().score(mate_score=99999)
        
        evals = []
        classifications = []
        
        for move in moves:
            # 1. Material before
            mat_before = self.get_material_score(board)
            
            # 2. Top moves evaluation
            analysis_before = self.engine.analyse(board, chess.engine.Limit(depth=depth), multipv=3)
            # Ensure we have scores
            top_scores = [m["score"].white().score(mate_score=99999) for m in analysis_before]
            top_moves = [m["pv"][0].uci() for m in analysis_before]
            
            best_uci = top_moves[0] if top_moves else ""
            actual_uci = move.uci()
            
            # 3. Make move and get new score
            board.push(move)
            analysis_after = self.engine.analyse(board, chess.engine.Limit(depth=depth))
            curr_cp = analysis_after["score"].white().score(mate_score=99999)
            mat_after = self.get_material_score(board)
            
            # 4. Classification
            is_white = not board.turn
            p_win = self.cp_to_win_pct(prev_cp) if is_white else (100 - self.cp_to_win_pct(prev_cp))
            c_win = self.cp_to_win_pct(curr_cp) if is_white else (100 - self.cp_to_win_pct(curr_cp))
            loss = p_win - c_win
            gain = c_win - p_win
            
            m_loss = (mat_before["w"] - mat_after["w"]) if is_white else (mat_before["b"] - mat_after["b"])
            
            cls = self.classify(p_win, c_win, loss, gain, top_scores, actual_uci, top_moves, is_white, m_loss)
            
            evals.append(curr_cp)
            classifications.append(cls)
            prev_cp = curr_cp
            
        return {"evals": evals, "classifications": classifications}

    def classify(self, p_win, c_win, loss, gain, top_scores, actual_uci, top_moves, is_white, m_loss):
        is_best = (actual_uci == top_moves[0]) if top_moves else False
        
        # BRILLIANT
        if loss <= 4.0 and c_win > 40 and m_loss >= 0.9:
            return "brilliant"

        # GREAT
        # Only Move Logic
        if len(top_scores) > 1 and is_best:
            b_p = self.cp_to_win_pct(top_scores[0]) if is_white else (100 - self.cp_to_win_pct(top_scores[0]))
            s_p = self.cp_to_win_pct(top_scores[1]) if is_white else (100 - self.cp_to_win_pct(top_scores[1]))
            if (b_p - s_p) > 15.0 and b_p > 50:
                return "great"
        
        if gain > 12.0 and c_win > 45: return "great"

        # STANDARD
        if is_best and loss < 0.5: return "best"
        if loss <= 2.2:  return "excellent"
        if loss <= 5.5:  return "good"
        if loss <= 11:   return "inaccuracy"
        if loss <= 22:   return "mistake"
        return "blunder"

    def quit(self):
        self.engine.quit()

if __name__ == "__main__":
    pass
