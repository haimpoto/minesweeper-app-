// ברגע שהדף מסיים להיטען - מתחילים משחק חדש
document.addEventListener('DOMContentLoaded', () => {
    fetchGameState();
});

// הבאת מצב המשחק מהשרת ב-Python (קריאת GET)
async function fetchGameState() {
    try {
        const response = await fetch('/api/state');
        const data = await response.json();
        renderBoard(data);
    } catch (error) {
        console.error('שגיאה בהבאת מצב המשחק:', error);
    }
}

// התחלת משחק חדש לפי רמת הקושי שנבחרה (קריאת POST)
async function startNewGame() {
    const difficulty = document.getElementById('difficulty-select').value;

    let rows = 9, cols = 9, mines = 10;
    if (difficulty === 'medium') {
        rows = 16; cols = 16; mines = 40;
    } else if (difficulty === 'hard') {
        rows = 16; cols = 30; mines = 99;
    }

    try {
        const response = await fetch('/api/new-game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rows, cols, mines })
        });
        const data = await response.json();
        renderBoard(data);
    } catch (error) {
        console.error('שגיאה בהתחלת משחק חדש:', error);
    }
}

// לחיצה על משבצת (קליק שמאלי - חשיפה)
async function handleCellClick(row, col) {
    try {
        const response = await fetch('/api/reveal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ row, col })
        });
        const data = await response.json();
        renderBoard(data);
    } catch (error) {
        console.error('שגיאה בחשיפת משבצת:', error);
    }
}

// לחיצה ימנית על משבצת (סימון / ביטול דגל)
async function handleCellRightClick(event, row, col) {
    event.preventDefault(); // מונע את פתיחת תפריט הדפדפן הרגיל
    try {
        const response = await fetch('/api/flag', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ row, col })
        });
        const data = await response.json();
        renderBoard(data);
    } catch (error) {
        console.error('שגיאה בסימון דגל:', error);
    }
}

// --- ציור ורינדור הלוח ב-HTML ---
function renderBoard(gameState) {
    const boardElement = document.getElementById('board');
    const statusElement = document.getElementById('status-message');

    // ניקוי הלוח הישן
    boardElement.innerHTML = '';
    statusElement.innerText = '';
    statusElement.className = 'status-message';

    const board = gameState.board;
    const rows = board.length;
    const cols = board[0].length;

    // הגדרת מספר העמודות ב-CSS Grid באופן דינמי
    boardElement.style.gridTemplateColumns = `repeat(${cols}, 38px)`;

    // מעבר על כל המשבצות ויצירת האלמנטים ב-HTML
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            const cellData = board[r][c];
            const cellDiv = document.createElement('div');
            cellDiv.classList.add('cell');

            // 1. משבצת מסומנת בדגל
            if (cellData.status === 'flagged') {
                cellDiv.innerText = '🚩';
            }
            // 2. משבצת שנחשפה
            else if (cellData.status === 'revealed') {
                cellDiv.classList.add('revealed');

                if (cellData.value === -1) {
                    cellDiv.innerText = '💣';
                    cellDiv.classList.add('mine');
                } else if (cellData.value > 0) {
                    cellDiv.innerText = cellData.value;
                    cellDiv.classList.add(`val-${cellData.value}`); // הוספת מחלקת עיצוב לפי המספר
                }
            }

            // חיבור אירועי עכבר למשבצת
            cellDiv.addEventListener('click', () => handleCellClick(r, c));
            cellDiv.addEventListener('contextmenu', (e) => handleCellRightClick(e, r, c));

            boardElement.appendChild(cellDiv);
        }
    }

    // הודעות סיום משחק
    if (gameState.game_over) {
        if (gameState.won) {
            statusElement.innerText = '🏆 אלוף! ניצחת את המשחק!';
            statusElement.classList.add('win');
        } else {
            statusElement.innerText = '💥 בום! פגעת במוקש. נסה שוב!';
            statusElement.classList.add('lose');
        }
    }
}