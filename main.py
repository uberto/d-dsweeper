import pygame
import asyncio
import platform
import hashlib
import random
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
QR_SIZE = 150  # Size of the QR code display
QR_MODULES = 21  # Number of modules (cells) in the QR code
MODULE_SIZE = QR_SIZE // QR_MODULES

# Game Grid Constants
CELL_SIZE = 20  # Reduced from 25 to fit more cells
GRID_WIDTH = 50  # Increased from 40
GRID_HEIGHT = 35  # Increased from 30
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
        self.state = CellState.REVEALED
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
        self.rooms = []  # List to store room information
        self.generate_dungeon()

    def is_room_valid(self, x, y, width, height, room_type):
        """Check if a room can be placed at the given position"""
        # Ensure room is at least 1 cell away from map borders
        if x < 2 or y < 2 or x + width > GRID_WIDTH - 2 or y + height > GRID_HEIGHT - 2:
            return False

        # For overlapping rooms, only allow if they are of the same type
        overlapping_room_found = False
        overlapping_type = None
        
        for cy in range(y - 1, y + height + 1):
            for cx in range(x - 1, x + width + 1):
                if not (0 <= cy < GRID_HEIGHT and 0 <= cx < GRID_WIDTH):
                    return False
                # Check if this cell is already part of another room
                if self.grid[cy][cx].cell_type != CellType.WALL:
                    # Find the overlapping room
                    for room in self.rooms:
                        if (room['x'] <= cx <= room['x'] + room['width'] - 1 and 
                            room['y'] <= cy <= room['y'] + room['height'] - 1):
                            if not overlapping_room_found:
                                overlapping_room_found = True
                                overlapping_type = room['type']
                            elif room['type'] != overlapping_type:
                                # Found a second room of different type
                                return False
                            break
                    
                    # If we found an overlapping room of different type, reject
                    if overlapping_room_found and overlapping_type != room_type:
                        return False
        
        return True

    def generate_dungeon(self):
        # Start with all walls
        for row in self.grid:
            for cell in row:
                cell.cell_type = CellType.WALL

        # Generate random rooms
        self.generate_rooms()
        
        # Connect rooms with corridors
        self.connect_rooms()
        
        # Calculate adjacent counts for floor cells
        self.calculate_adjacent_counts()

    def generate_rooms(self):
        attempts = 0
        max_attempts = 1000
        min_rooms = 40
        max_rooms = 60
        num_rooms = random.randint(min_rooms, max_rooms)
        
        # Calculate room type distribution (2:1 ratio of monster:treasure)
        num_treasure = num_rooms // 3
        num_monster = num_rooms - num_treasure
        
        # Create room type list with 2:1 ratio
        room_types = (["monster"] * num_monster + ["treasure"] * num_treasure)
        random.shuffle(room_types)
        
        # Ensure at least 3 treasure rooms and 6 monster rooms at the start
        start_rooms = ["treasure", "treasure", "treasure"] + ["monster"] * 6
        room_types = start_rooms + room_types[9:]
        random.shuffle(room_types)
        
        # Divide map into sectors for room placement
        sectors = [(x, y) for x in range(4) for y in range(3)]
        random.shuffle(sectors)
        sector_width = (GRID_WIDTH - 4) // 4
        sector_height = (GRID_HEIGHT - 4) // 3
        
        sector_index = 0
        consecutive_failures = 0
        max_consecutive_failures = 5  # Number of failures before reducing room size
        current_max_size = 12  # Start with maximum room size
        
        while len(self.rooms) < num_rooms and attempts < max_attempts:
            # Get current sector
            if sector_index >= len(sectors):
                random.shuffle(sectors)
                sector_index = 0
            sector_x, sector_y = sectors[sector_index]
            
            # Calculate room position within sector
            base_x = 2 + sector_x * sector_width
            base_y = 2 + sector_y * sector_height
            
            # Adjust maximum room size based on consecutive failures
            if consecutive_failures >= max_consecutive_failures:
                current_max_size = max(4, current_max_size - 1)  # Reduce size but not below 4
                consecutive_failures = 0  # Reset counter
            
            # Random room size (4 to current_max_size)
            width = random.randint(4, min(current_max_size, sector_width - 1))
            height = random.randint(4, min(current_max_size, sector_height - 1))
            
            # Random position within sector (with padding for merging)
            x = random.randint(base_x - 2, base_x + sector_width - width + 2)
            y = random.randint(base_y - 2, base_y + sector_height - height + 2)
            
            # Get room type from our prepared list
            room_type = room_types[len(self.rooms)]
            
            if self.is_room_valid(x, y, width, height, room_type):
                # Create room
                self.create_room(x, y, width, height, room_type)
                self.rooms.append({
                    'x': x,
                    'y': y,
                    'width': width,
                    'height': height,
                    'type': room_type,
                    'connected': False,
                    'doors': []
                })
                sector_index += 1
                consecutive_failures = 0  # Reset on success
                current_max_size = min(12, current_max_size + 1)  # Try to increase size again
            else:
                consecutive_failures += 1
            
            attempts += 1

    def create_room(self, x, y, width, height, room_type):
        # Create room walls only where there isn't already a floor
        for cy in range(y - 1, y + height + 1):
            for cx in range(x - 1, x + width + 1):
                if 0 <= cy < GRID_HEIGHT and 0 <= cx < GRID_WIDTH:
                    # Only place wall if the cell isn't already a floor or special cell
                    current_type = self.grid[cy][cx].cell_type
                    if current_type == CellType.WALL:
                        self.grid[cy][cx].cell_type = CellType.WALL

        # Calculate content placement with reduced density
        room_area = width * height
        # Significantly reduced content density
        min_content = max(1, room_area // 25)  # Was 15
        max_content = max(2, room_area // 20)  # Was 10
        num_content = random.randint(min_content, max_content)
        
        # Get all possible floor positions
        floor_positions = []
        for cy in range(y, y + height):
            for cx in range(x, x + width):
                current_type = self.grid[cy][cx].cell_type
                if current_type not in [CellType.MONSTER, CellType.TREASURE]:
                    floor_positions.append((cx, cy))
        
        # Place content in random positions
        for _ in range(num_content):
            if floor_positions:
                cx, cy = random.choice(floor_positions)
                floor_positions.remove((cx, cy))
                self.grid[cy][cx].cell_type = (CellType.MONSTER if room_type == "monster" 
                                             else CellType.TREASURE)
        
        # Fill remaining positions with floor
        for cx, cy in floor_positions:
            if self.grid[cy][cx].cell_type == CellType.WALL:  # Only convert walls to floor
                self.grid[cy][cx].cell_type = CellType.FLOOR

    def connect_rooms(self):
        if not self.rooms:
            return

        # Separate rooms by type
        monster_rooms = [room for room in self.rooms if room['type'] == "monster"]
        treasure_rooms = [room for room in self.rooms if room['type'] == "treasure"]

        # Connect monster rooms
        if monster_rooms:
            self._connect_room_network(monster_rooms, "monster")

        # Connect treasure rooms
        if treasure_rooms:
            self._connect_room_network(treasure_rooms, "treasure")

    def _connect_room_network(self, rooms, room_type):
        """Connect all rooms of the same type together"""
        if not rooms:
            return

        # Start with the first room as connected
        rooms[0]['connected'] = True
        
        # Keep connecting until all rooms are connected
        while not all(room['connected'] for room in rooms):
            # Find the closest pair of connected and unconnected rooms
            best_distance = float('inf')
            best_connection = None
            
            for room1 in rooms:
                if not room1['connected']:
                    continue
                    
                for room2 in rooms:
                    if room2['connected']:
                        continue
                        
                    # Calculate center points
                    c1x = room1['x'] + room1['width'] // 2
                    c1y = room1['y'] + room1['height'] // 2
                    c2x = room2['x'] + room2['width'] // 2
                    c2y = room2['y'] + room2['height'] // 2
                    
                    dist = abs(c1x - c2x) + abs(c1y - c2y)
                    if dist < best_distance:
                        best_distance = dist
                        best_connection = (room1, room2, c1x, c1y, c2x, c2y)
            
            if best_connection:
                room1, room2, x1, y1, x2, y2 = best_connection
                self.create_corridor(x1, y1, x2, y2, room_type)
                room2['connected'] = True

    def create_corridor(self, x1, y1, x2, y2, room_type):
        """Create a corridor between two points"""
        # First go horizontally, then vertically
        current_x = x1
        current_y = y1
        
        # All corridors are doors (brown color)
        corridor_type = CellType.DOOR
        
        # Place corridor at start
        if self.grid[y1][x1].cell_type == CellType.WALL:
            self.grid[y1][x1].cell_type = corridor_type
        
        # Horizontal movement
        while current_x != x2:
            step = 1 if x2 > current_x else -1
            current_x += step
            if self.grid[current_y][current_x].cell_type == CellType.WALL:
                self.grid[current_y][current_x].cell_type = corridor_type
        
        # Vertical movement
        while current_y != y2:
            step = 1 if y2 > current_y else -1
            current_y += step
            if self.grid[current_y][current_x].cell_type == CellType.WALL:
                self.grid[current_y][current_x].cell_type = corridor_type

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