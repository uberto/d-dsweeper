import pygame
import asyncio
import platform
import hashlib
import random
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
QR_SIZE = 150  # Size of the QR code display
QR_MODULES = 21  # Number of modules (cells) in the QR code
MODULE_SIZE = QR_SIZE // QR_MODULES

# Game Grid Constants
CELL_SIZE = 30
GRID_WIDTH = 20
GRID_HEIGHT = 15
GRID_OFFSET_X = (WINDOW_WIDTH - GRID_WIDTH * CELL_SIZE) // 2
GRID_OFFSET_Y = (WINDOW_HEIGHT - GRID_HEIGHT * CELL_SIZE) // 2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
DARK_GRAY = (64, 64, 64)
LIGHT_BROWN = (205, 133, 63)
GOLD = (255, 215, 0)
RED = (255, 0, 0)

# Game States
WELCOME_SCREEN = "welcome"
GAME_SCREEN = "game"

class CellType(Enum):
    WALL = "wall"
    FLOOR = "floor"
    DOOR = "door"
    MONSTER = "monster"
    TREASURE = "treasure"

class CellState(Enum):
    HIDDEN = "hidden"
    REVEALED = "revealed"
    FLAGGED = "flagged"

class Cell:
    def __init__(self, x, y, cell_type=CellType.WALL):
        self.x = x
        self.y = y
        self.cell_type = cell_type
        self.state = CellState.HIDDEN
        self.adjacent_count = 0  # Number of adjacent monsters or treasures

    def draw(self, surface):
        rect = pygame.Rect(
            GRID_OFFSET_X + self.x * CELL_SIZE,
            GRID_OFFSET_Y + self.y * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
        
        # Draw the cell based on its state
        if self.state == CellState.HIDDEN:
            pygame.draw.rect(surface, GRAY, rect)
            pygame.draw.rect(surface, DARK_GRAY, rect, 1)
        elif self.state == CellState.REVEALED:
            if self.cell_type == CellType.WALL:
                pygame.draw.rect(surface, DARK_GRAY, rect)
            elif self.cell_type == CellType.FLOOR:
                pygame.draw.rect(surface, LIGHT_BROWN, rect)
                if self.adjacent_count > 0:
                    font = pygame.font.Font(None, 24)
                    text = font.render(str(self.adjacent_count), True, BLACK)
                    text_rect = text.get_rect(center=rect.center)
                    surface.blit(text, text_rect)
            elif self.cell_type == CellType.DOOR:
                pygame.draw.rect(surface, BROWN, rect)
            elif self.cell_type == CellType.MONSTER:
                pygame.draw.rect(surface, RED, rect)
            elif self.cell_type == CellType.TREASURE:
                pygame.draw.rect(surface, GOLD, rect)
        
        pygame.draw.rect(surface, BLACK, rect, 1)

class DungeonMap:
    def __init__(self):
        self.grid = [[Cell(x, y) for x in range(GRID_WIDTH)] for y in range(GRID_HEIGHT)]
        self.generate_dungeon()

    def generate_dungeon(self):
        # Start with all walls
        for row in self.grid:
            for cell in row:
                cell.cell_type = CellType.WALL

        # Create a central corridor
        corridor_y = GRID_HEIGHT // 2
        for x in range(GRID_WIDTH):
            self.grid[corridor_y][x].cell_type = CellType.FLOOR
            self.grid[corridor_y][x].state = CellState.REVEALED

        # Add rooms
        self.add_rooms()

    def add_rooms(self):
        # Add 4 rooms along the corridor
        room_positions = [
            (3, GRID_HEIGHT//2 - 4),  # Top left
            (12, GRID_HEIGHT//2 - 4),  # Top right
            (3, GRID_HEIGHT//2 + 1),   # Bottom left
            (12, GRID_HEIGHT//2 + 1)   # Bottom right
        ]

        for pos_x, pos_y in room_positions:
            room_width = 5
            room_height = 4
            room_type = random.choice(["monster", "treasure"])
            
            # Create room walls
            for y in range(pos_y - 1, pos_y + room_height + 1):
                for x in range(pos_x - 1, pos_x + room_width + 1):
                    if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                        self.grid[y][x].cell_type = CellType.WALL

            # Fill room with floor and add content
            for y in range(pos_y, pos_y + room_height):
                for x in range(pos_x, pos_x + room_width):
                    if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                        self.grid[y][x].cell_type = CellType.FLOOR
                        # Add some monsters or treasure
                        if random.random() < 0.2:  # 20% chance
                            if room_type == "monster":
                                self.grid[y][x].cell_type = CellType.MONSTER
                            else:
                                self.grid[y][x].cell_type = CellType.TREASURE

            # Add door connecting to corridor
            door_x = pos_x + room_width // 2
            door_y = GRID_HEIGHT // 2
            if pos_y < GRID_HEIGHT // 2:  # Room is above corridor
                door_y = pos_y + room_height
            else:  # Room is below corridor
                door_y = pos_y - 1
            self.grid[door_y][door_x].cell_type = CellType.DOOR
            self.grid[door_y][door_x].state = CellState.REVEALED

        # Calculate adjacent counts for floor cells
        self.calculate_adjacent_counts()

    def calculate_adjacent_counts(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x].cell_type == CellType.FLOOR:
                    count = 0
                    # Check all 8 adjacent cells
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            new_x, new_y = x + dx, y + dy
                            if 0 <= new_y < GRID_HEIGHT and 0 <= new_x < GRID_WIDTH:
                                cell_type = self.grid[new_y][new_x].cell_type
                                if cell_type in [CellType.MONSTER, CellType.TREASURE]:
                                    count += 1
                    self.grid[y][x].adjacent_count = count

    def draw(self, surface):
        for row in self.grid:
            for cell in row:
                cell.draw(surface)

    def handle_click(self, pos):
        # Convert screen coordinates to grid coordinates
        grid_x = (pos[0] - GRID_OFFSET_X) // CELL_SIZE
        grid_y = (pos[1] - GRID_OFFSET_Y) // CELL_SIZE
        
        if 0 <= grid_y < GRID_HEIGHT and 0 <= grid_x < GRID_WIDTH:
            cell = self.grid[grid_y][grid_x]
            if cell.state == CellState.HIDDEN:
                cell.state = CellState.REVEALED
                if cell.cell_type == CellType.FLOOR:
                    self.flood_fill_reveal(grid_x, grid_y)

    def flood_fill_reveal(self, x, y):
        """Reveal connected floor cells with no adjacent monsters/treasures"""
        if not (0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH):
            return
        
        cell = self.grid[y][x]
        if cell.state == CellState.REVEALED or cell.cell_type == CellType.WALL:
            return
            
        cell.state = CellState.REVEALED
        
        # If it's a floor cell with no adjacent monsters/treasures, reveal neighbors
        if cell.cell_type == CellType.FLOOR and cell.adjacent_count == 0:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    self.flood_fill_reveal(x + dx, y + dy)

# Create the window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("D&D Sweeper")

def draw_qr_pattern(surface, x, y, url):
    """Draw a simple QR-like pattern based on URL hash"""
    # Create a hash of the URL to generate a unique pattern
    hash_obj = hashlib.sha256(url.encode())
    hash_bytes = hash_obj.digest()
    
    # Draw white background
    pygame.draw.rect(surface, WHITE, (x, y, QR_SIZE, QR_SIZE))
    
    # Draw black border
    border_size = MODULE_SIZE * 2
    pygame.draw.rect(surface, BLACK, (x, y, QR_SIZE, QR_SIZE), border_size)
    
    # Draw position detection patterns (corners)
    for corner_x, corner_y in [(0, 0), (0, QR_MODULES-7), (QR_MODULES-7, 0)]:
        # Outer square
        pygame.draw.rect(surface, BLACK, 
                        (x + corner_x * MODULE_SIZE, 
                         y + corner_y * MODULE_SIZE, 
                         7 * MODULE_SIZE, 
                         7 * MODULE_SIZE))
        # Inner white square
        pygame.draw.rect(surface, WHITE, 
                        (x + (corner_x + 1) * MODULE_SIZE, 
                         y + (corner_y + 1) * MODULE_SIZE, 
                         5 * MODULE_SIZE, 
                         5 * MODULE_SIZE))
        # Center black square
        pygame.draw.rect(surface, BLACK, 
                        (x + (corner_x + 2) * MODULE_SIZE, 
                         y + (corner_y + 2) * MODULE_SIZE, 
                         3 * MODULE_SIZE, 
                         3 * MODULE_SIZE))
    
    # Use hash to generate pattern
    for i in range(len(hash_bytes)):
        byte = hash_bytes[i]
        row = (i * 8) // QR_MODULES
        col = (i * 8) % QR_MODULES
        
        # Skip if we're in the position detection patterns
        if (row < 7 and col < 7) or \
           (row < 7 and col > QR_MODULES-8) or \
           (row > QR_MODULES-8 and col < 7):
            continue
            
        # Draw up to 8 modules based on the byte value
        for bit in range(8):
            if row >= QR_MODULES or col >= QR_MODULES:
                break
            if byte & (1 << bit):
                pygame.draw.rect(surface, BLACK,
                               (x + col * MODULE_SIZE,
                                y + row * MODULE_SIZE,
                                MODULE_SIZE,
                                MODULE_SIZE))
            col += 1
            if col >= QR_MODULES:
                col = 0
                row += 1

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.font = pygame.font.Font(None, 36)

    def draw(self, surface):
        color = GRAY if self.is_hovered else BLACK
        pygame.draw.rect(surface, color, self.rect)
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Game:
    def __init__(self):
        self.state = WELCOME_SCREEN
        self.setup_welcome_screen()
        self.setup_game_screen()

    def setup_welcome_screen(self):
        self.start_button = Button(
            WINDOW_WIDTH // 2 - BUTTON_WIDTH // 2,
            WINDOW_HEIGHT // 2,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Start Game"
        )
        self.title_font = pygame.font.Font(None, 48)
        self.title_text = self.title_font.render("Welcome to D&D Sweeper", True, BLACK)
        self.title_rect = self.title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))

        # URL setup for QR code
        self.url_font = pygame.font.Font(None, 24)
        self.url = "http://localhost:8000"  # Default URL
        self.url_text = self.url_font.render(self.url, True, BLACK)
        self.url_rect = self.url_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        
        # QR code position
        self.qr_x = WINDOW_WIDTH // 2 - QR_SIZE // 2
        self.qr_y = WINDOW_HEIGHT - 150 - QR_SIZE // 2

    def setup_game_screen(self):
        self.dungeon_map = DungeonMap()

    def handle_event(self, event):
        if self.state == WELCOME_SCREEN:
            if self.start_button.handle_event(event):
                self.state = GAME_SCREEN
        elif self.state == GAME_SCREEN:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.dungeon_map.handle_click(event.pos)

    def draw(self):
        screen.fill(WHITE)
        
        if self.state == WELCOME_SCREEN:
            # Draw welcome screen with QR code
            screen.blit(self.title_text, self.title_rect)
            self.start_button.draw(screen)
            draw_qr_pattern(screen, self.qr_x, self.qr_y, self.url)
            screen.blit(self.url_text, self.url_rect)
        elif self.state == GAME_SCREEN:
            self.dungeon_map.draw(screen)

async def main():
    game = Game()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            game.handle_event(event)

        game.draw()
        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main()) 