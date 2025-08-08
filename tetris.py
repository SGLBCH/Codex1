import curses
import random
import time

TETROMINOS = {
    'I': [
        [(0,0),(1,0),(2,0),(3,0)],
        [(1,-1),(1,0),(1,1),(1,2)]
    ],
    'J': [
        [(0,0),(0,1),(1,1),(2,1)],
        [(1,0),(2,0),(1,1),(1,2)],
        [(0,0),(1,0),(2,0),(2,-1)],
        [(1,0),(1,1),(1,2),(0,2)]
    ],
    'L': [
        [(2,0),(0,1),(1,1),(2,1)],
        [(1,0),(1,1),(1,2),(2,2)],
        [(0,0),(0,1),(1,1),(2,1)],
        [(0,0),(1,0),(1,1),(1,2)]
    ],
    'O': [
        [(0,0),(1,0),(0,1),(1,1)]
    ],
    'S': [
        [(1,0),(2,0),(0,1),(1,1)],
        [(1,0),(1,1),(2,1),(2,2)]
    ],
    'T': [
        [(1,0),(0,1),(1,1),(2,1)],
        [(1,0),(1,1),(2,1),(1,2)],
        [(0,1),(1,1),(2,1),(1,2)],
        [(1,0),(0,1),(1,1),(1,2)]
    ],
    'Z': [
        [(0,0),(1,0),(1,1),(2,1)],
        [(2,0),(1,1),(2,1),(1,2)]
    ]
}

class Tetris:
    def __init__(self, stdscr, height=20, width=10):
        self.stdscr = stdscr
        self.height = height
        self.width = width
        self.board = [[0 for _ in range(width)] for _ in range(height)]
        self.score = 0
        self.next_piece()

    def next_piece(self):
        self.piece = {
            'shape': random.choice(list(TETROMINOS.keys())),
            'rot': 0,
            'x': self.width // 2 - 2,
            'y': 0
        }
        self.blocks = self.get_blocks()

    def get_blocks(self):
        shape = TETROMINOS[self.piece['shape']][self.piece['rot']]
        return [(x + self.piece['x'], y + self.piece['y']) for x, y in shape]

    def rotate(self):
        old_rot = self.piece['rot']
        self.piece['rot'] = (self.piece['rot'] + 1) % len(TETROMINOS[self.piece['shape']])
        new_blocks = self.get_blocks()
        if not self.valid(new_blocks):
            self.piece['rot'] = old_rot
        else:
            self.blocks = new_blocks

    def move(self, dx, dy):
        new_blocks = [(x + dx, y + dy) for x, y in self.blocks]
        if self.valid(new_blocks):
            self.piece['x'] += dx
            self.piece['y'] += dy
            self.blocks = new_blocks
            return True
        return False

    def valid(self, blocks):
        for x, y in blocks:
            if x < 0 or x >= self.width or y >= self.height:
                return False
            if y >= 0 and self.board[y][x]:
                return False
        return True

    def lock_piece(self):
        for x, y in self.blocks:
            if 0 <= y < self.height:
                self.board[y][x] = 1
        self.clear_lines()
        self.next_piece()
        if not self.valid(self.blocks):
            raise SystemExit

    def clear_lines(self):
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        cleared = self.height - len(new_board)
        for _ in range(cleared):
            new_board.insert(0, [0 for _ in range(self.width)])
        self.board = new_board
        self.score += cleared

    def draw(self):
        self.stdscr.clear()
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell:
                    self.stdscr.addstr(y, x*2, '[]')
        for x, y in self.blocks:
            if y >= 0:
                self.stdscr.addstr(y, x*2, '[]')
        self.stdscr.addstr(0, self.width*2 + 2, f'Score: {self.score}')
        self.stdscr.refresh()

    def game_loop(self):
        self.stdscr.nodelay(True)
        last_move = time.time()
        while True:
            key = self.stdscr.getch()
            if key == curses.KEY_LEFT:
                self.move(-1,0)
            elif key == curses.KEY_RIGHT:
                self.move(1,0)
            elif key == curses.KEY_DOWN:
                if not self.move(0,1):
                    self.lock_piece()
            elif key == curses.KEY_UP:
                self.rotate()
            elif key == ord('q'):
                break
            if time.time() - last_move > 0.5:
                if not self.move(0,1):
                    self.lock_piece()
                last_move = time.time()
            self.draw()

def main(stdscr):
    curses.curs_set(0)
    t = Tetris(stdscr)
    try:
        t.game_loop()
    except SystemExit:
        stdscr.nodelay(False)
        stdscr.addstr(t.height//2, t.width, 'Game Over')
        stdscr.getch()

if __name__ == '__main__':
    curses.wrapper(main)
