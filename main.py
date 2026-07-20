from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from game_logic import Minesweeper

app = FastAPI()

# יצירת מופע יחיד של המשחק בזיכרון של השרת
game = Minesweeper(rows=9, cols=9, mines=10)

# חיבור תיקיית static כדי שהשרת יוכל להגיש קבצי HTML, CSS ו-JS
app.mount("/static", StaticFiles(directory="static"), name="static")


# מודלים של Pydantic לווידוא תקינות הנתונים הנכנסים בבקשות HTTP
class CellAction(BaseModel):
    row: int
    col: int

class NewGameConfig(BaseModel):
    rows: int = 9
    cols: int = 9
    mines: int = 10


# --- הגדרת ה-Endpoints (נקודות הקצה של ה-API) ---

@app.get("/")
def read_root():
    """הגשת דף ה-HTML הראשי כשנכנסים לכתובת הבית"""
    return FileResponse("static/index.html")

@app.get("/api/state")
def get_state():
    """מחזיר את המצב הנוכחי של הלוח"""
    return game.get_state()

@app.post("/api/reveal")
def reveal_cell(action: CellAction):
    """מבצע חשיפה של משבצת ומחזיר את הלוח המעודכן"""
    game.reveal(action.row, action.col)
    return game.get_state()

@app.post("/api/flag")
def toggle_flag(action: CellAction):
    """מסמן או מבטל דגל על משבצת"""
    game.toggle_flag(action.row, action.col)
    return game.get_state()

@app.post("/api/new-game")
def new_game(config: NewGameConfig):
    """מאתחל משחק חדש לפי גודל ולוח מוקשים מבוקשים"""
    global game
    game = Minesweeper(rows=config.rows, cols=config.cols, mines=config.mines)
    return game.get_state()