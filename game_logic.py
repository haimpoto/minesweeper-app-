import random


class Minesweeper:
    def __init__(self, rows=9, cols=9, mines=10):
        self.rows = rows
        self.cols = cols
        self.mines = mines

        # -1 מייצג מוקש, מספר חיובי (0-8) מייצג כמה מוקשים יש מסביב
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]

        # לוח המעקב אחרי מה שהשחקן רואה: 'hidden', 'revealed', או 'flagged'
        self.visible_board = [['hidden' for _ in range(cols)] for _ in range(rows)]

        self.game_over = False
        self.won = False
        self.first_click = True

    def _place_mines(self, safe_r, safe_c):
        """פיזור אקראי של המוקשים בלוח, תוך החרגת אזור הלחיצה הראשונה"""
        safe_zone = set()
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = safe_r + dr, safe_c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    safe_zone.add((nr, nc))

        available_positions = [
            (r, c) for r in range(self.rows) for c in range(self.cols)
            if (r, c) not in safe_zone
        ]

        num_mines = min(self.mines, len(available_positions))
        mine_positions = random.sample(available_positions, num_mines)

        for r, c in mine_positions:
            self.grid[r][c] = -1

    def _calculate_neighbors(self):
        """חישוב כמה מוקשים יש מסביב לכל משבצת שלא מכילה מוקש"""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == -1:
                    continue  # מדלגים על מוקש עצמו

                # בדיקת 8 השכנים מסביב
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        # גבולות המטריצה
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if self.grid[nr][nc] == -1:
                                count += 1
                self.grid[r][c] = count

    def reveal(self, r, c):
        """לחיצה על משבצת לחשיפתה"""
        if self.game_over or self.visible_board[r][c] != 'hidden':
            return

        # אם זו הלחיצה הראשונה, עכשיו מפזרים את המוקשים ומחשבים שכנים
        if getattr(self, 'first_click', False):
            self._place_mines(safe_r=r, safe_c=c)
            self._calculate_neighbors()
            self.first_click = False


        # אם פגענו במוקש - המשחק נגמר
        if self.grid[r][c] == -1:
            self.visible_board[r][c] = 'revealed'
            self.game_over = True
            self.won = False
            self._reveal_all_mines()
            return

        # חשיפת המשבצת הנוכחית (וההצפה אם היא ריקה)
        self._flood_fill(r, c)

        # בדיקה אם השחקן ניצח אחרי החשיפה
        self._check_win()

    def _flood_fill(self, r, c):
        """אלגוריתם הצפה (Flood Fill) לפתיחת רצף של משבצות ריקות (0)"""
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return
        if self.visible_board[r][c] != 'hidden':
            return

        self.visible_board[r][c] = 'revealed'

        # אם המשבצת ריקה לחלוטין (0 מוקשים מסביב), ממשיכים לחשוף את השכנים שלה בדיאלוג רקורסיבי
        if self.grid[r][c] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr != 0 or dc != 0:
                        self._flood_fill(r + dr, c + dc)

    def toggle_flag(self, r, c):
        """סימון או ביטול דגל על משבצת"""
        if self.game_over or self.visible_board[r][c] == 'revealed':
            return

        if self.visible_board[r][c] == 'hidden':
            self.visible_board[r][c] = 'flagged'
        elif self.visible_board[r][c] == 'flagged':
            self.visible_board[r][c] = 'hidden'

    def _reveal_all_mines(self):
        """פתיחת כל המוקשים במקרה של הפסד"""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == -1:
                    self.visible_board[r][c] = 'revealed'

    def _check_win(self):
        """בדיקה אם כל המשבצות שאינן מוקשים כבר נחשפו"""
        unrevealed_safe_cells = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] != -1 and self.visible_board[r][c] != 'revealed':
                    unrevealed_safe_cells += 1

        if unrevealed_safe_cells == 0:
            self.game_over = True
            self.won = True

    def get_state(self):
        """החזרת מצב הלוח העדכני בצורת מילון לשליחה ל-Frontend"""
        board_data = []
        for r in range(self.rows):
            row_data = []
            for c in range(self.cols):
                cell_info = {
                    "status": self.visible_board[r][c],  # 'hidden', 'revealed', או 'flagged'
                    "value": self.grid[r][c]  # -1 (מוקש) או 0-8
                }
                row_data.append(cell_info)
            board_data.append(row_data)

        return {
            "board": board_data,
            "game_over": self.game_over,
            "won": self.won,
            "total_mines": self.mines
        }