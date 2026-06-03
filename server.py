from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine import ChessAnalyzer
import os

app = FastAPI()

# Enable CORS so the local index.html can talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Search for stockfish binary in common locations or current dir
STOCKFISH_PATH = "stockfish.exe" if os.name == "nt" else "stockfish"

class AnalysisRequest(BaseModel):
    pgn: str

@app.post("/analyze")
async def analyze_game(request: AnalysisRequest):
    if not os.path.exists(STOCKFISH_PATH):
        raise HTTPException(status_code=500, detail=f"Stockfish binary not found at {STOCKFISH_PATH}. Please put stockfish.exe in this folder.")
    
    try:
        analyzer = ChessAnalyzer(STOCKFISH_PATH)
        results = analyzer.analyze_game(request.pgn)
        analyzer.quit()
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
