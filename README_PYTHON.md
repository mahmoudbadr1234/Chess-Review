# Chess Review Pro — Python Engine Setup

To get professional-grade analysis (Chess.com accuracy), follow these steps:

1. **Stockfish Binary**:
   - Download Stockfish from [stockfishchess.org](https://stockfishchess.org/download/).
   - Extract the `stockfish.exe` (or name it `stockfish.exe`) and place it directly in this folder (`f:\chess\`).

2. **Run the Server**:
   - Open your terminal in this folder.
   - Run: `python server.py`
   - Keep this terminal window open while using the site.

3. **Enjoy**:
   - Open `index.html` in your browser.
   - Click "Analyze". The site will automatically detect your Python server and use it for much faster and more accurate analysis.

---
**Why is this better?**
- **Multi-PV**: It analyzes multiple moves at once to find "Only Moves" (Great Moves).
- **Speed**: It uses your computer's full power, not just the browser.
- **Accuracy**: It uses the full Stockfish 16.1 engine.
