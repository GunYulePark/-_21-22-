import random
import sys

import pygame


CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDE_PANEL = 180
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE + SIDE_PANEL
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 60
FALL_INTERVAL_MS = 500


COLORS = {
    "I": (0, 240, 240),
    "O": (240, 240, 0),
    "T": (160, 0, 240),
    "S": (0, 240, 0),
    "Z": (240, 0, 0),
    "J": (0, 0, 240),
    "L": (240, 160, 0),
}

SHAPES = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "Z": [[1, 1, 0], [0, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]],
    "L": [[0, 0, 1], [1, 1, 1]],
}


class Piece:
    def __init__(self, shape_name):
        self.shape_name = shape_name
        self.matrix = [row[:] for row in SHAPES[shape_name]]
        self.color = COLORS[shape_name]
        self.x = GRID_WIDTH // 2 - len(self.matrix[0]) // 2
        self.y = 0

    def rotated(self):
        return [list(row) for row in zip(*self.matrix[::-1])]


class TetrisGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Python Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("malgungothic", 24)
        self.small_font = pygame.font.SysFont("malgungothic", 18)
        self.reset()

    def reset(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.current_piece = self._spawn_piece()
        self.next_piece = self._spawn_piece()
        self.last_fall_time = pygame.time.get_ticks()

    def _spawn_piece(self):
        return Piece(random.choice(list(SHAPES.keys())))

    def valid_position(self, piece, dx=0, dy=0, matrix=None):
        if matrix is None:
            matrix = piece.matrix

        for y, row in enumerate(matrix):
            for x, cell in enumerate(row):
                if not cell:
                    continue
                new_x = piece.x + x + dx
                new_y = piece.y + y + dy

                if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                    return False
                if new_y >= 0 and self.grid[new_y][new_x] is not None:
                    return False
        return True

    def lock_piece(self):
        for y, row in enumerate(self.current_piece.matrix):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = self.current_piece.x + x
                    grid_y = self.current_piece.y + y
                    if grid_y < 0:
                        self.game_over = True
                        return
                    self.grid[grid_y][grid_x] = self.current_piece.color

        cleared = self.clear_lines()
        self.score += (cleared ** 2) * 100
        self.lines += cleared
        self.level = max(1, self.lines // 10 + 1)

        self.current_piece = self.next_piece
        self.next_piece = self._spawn_piece()

        if not self.valid_position(self.current_piece):
            self.game_over = True

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell is None for cell in row)]
        lines_cleared = GRID_HEIGHT - len(new_grid)

        for _ in range(lines_cleared):
            new_grid.insert(0, [None for _ in range(GRID_WIDTH)])

        self.grid = new_grid
        return lines_cleared

    def hard_drop(self):
        while self.valid_position(self.current_piece, dy=1):
            self.current_piece.y += 1
        self.lock_piece()

    def move(self, dx):
        if self.valid_position(self.current_piece, dx=dx):
            self.current_piece.x += dx

    def rotate(self):
        rotated = self.current_piece.rotated()
        if self.valid_position(self.current_piece, matrix=rotated):
            self.current_piece.matrix = rotated

    def update(self):
        if self.game_over:
            return

        speed = max(80, FALL_INTERVAL_MS - (self.level - 1) * 40)
        now = pygame.time.get_ticks()
        if now - self.last_fall_time >= speed:
            self.last_fall_time = now
            if self.valid_position(self.current_piece, dy=1):
                self.current_piece.y += 1
            else:
                self.lock_piece()

    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                color = self.grid[y][x] if self.grid[y][x] else (30, 30, 30)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (55, 55, 55), rect, 1)

    def draw_piece(self, piece, offset_x=0, offset_y=0):
        for y, row in enumerate(piece.matrix):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        (piece.x + x) * CELL_SIZE + offset_x,
                        (piece.y + y) * CELL_SIZE + offset_y,
                        CELL_SIZE,
                        CELL_SIZE,
                    )
                    pygame.draw.rect(self.screen, piece.color, rect)
                    pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def draw_side_panel(self):
        panel_x = GRID_WIDTH * CELL_SIZE
        pygame.draw.rect(self.screen, (20, 20, 20), (panel_x, 0, SIDE_PANEL, SCREEN_HEIGHT))

        self.screen.blit(self.font.render("TETRIS", True, (255, 255, 255)), (panel_x + 30, 25))
        self.screen.blit(self.small_font.render(f"점수: {self.score}", True, (220, 220, 220)), (panel_x + 20, 75))
        self.screen.blit(self.small_font.render(f"라인: {self.lines}", True, (220, 220, 220)), (panel_x + 20, 105))
        self.screen.blit(self.small_font.render(f"레벨: {self.level}", True, (220, 220, 220)), (panel_x + 20, 135))
        self.screen.blit(self.small_font.render("다음 블록", True, (255, 255, 255)), (panel_x + 20, 185))

        preview = Piece(self.next_piece.shape_name)
        preview.x = GRID_WIDTH + 1
        preview.y = 8
        self.draw_piece(preview)

        controls = [
            "←/→: 이동",
            "↑: 회전",
            "↓: 빠르게",
            "Space: 즉시 낙하",
            "R: 재시작",
            "Esc: 종료",
        ]

        for idx, line in enumerate(controls):
            txt = self.small_font.render(line, True, (180, 180, 180))
            self.screen.blit(txt, (panel_x + 15, 320 + idx * 28))

        if self.game_over:
            over_surface = self.font.render("GAME OVER", True, (255, 80, 80))
            retry_surface = self.small_font.render("R 키로 다시 시작", True, (255, 255, 255))
            self.screen.blit(over_surface, (panel_x + 15, 250))
            self.screen.blit(retry_surface, (panel_x + 15, 280))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_r:
                        self.reset()
                        continue

                    if self.game_over:
                        continue

                    if event.key == pygame.K_LEFT:
                        self.move(-1)
                    elif event.key == pygame.K_RIGHT:
                        self.move(1)
                    elif event.key == pygame.K_UP:
                        self.rotate()
                    elif event.key == pygame.K_DOWN:
                        if self.valid_position(self.current_piece, dy=1):
                            self.current_piece.y += 1
                    elif event.key == pygame.K_SPACE:
                        self.hard_drop()

            self.update()
            self.screen.fill((10, 10, 10))
            self.draw_grid()
            if not self.game_over:
                self.draw_piece(self.current_piece)
            self.draw_side_panel()

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    TetrisGame().run()
