import pygame
import asyncio
import platform
import hashlib

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

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

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

async def main():
    # Create start button
    start_button = Button(
        WINDOW_WIDTH // 2 - BUTTON_WIDTH // 2,
        WINDOW_HEIGHT // 2,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
        "Start Game"
    )

    # Title font
    title_font = pygame.font.Font(None, 48)
    title_text = title_font.render("Welcome to D&D Sweeper", True, BLACK)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))

    # URL setup
    url_font = pygame.font.Font(None, 24)
    url = "http://localhost:8000"  # Default URL
    url_text = url_font.render(url, True, BLACK)
    url_rect = url_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))

    # QR code position
    qr_x = WINDOW_WIDTH // 2 - QR_SIZE // 2
    qr_y = WINDOW_HEIGHT - 150 - QR_SIZE // 2

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if start_button.handle_event(event):
                print("Start button clicked!")  # For now, just print to console

        screen.fill(WHITE)
        
        # Draw title
        screen.blit(title_text, title_rect)
        
        # Draw button
        start_button.draw(screen)
        
        # Draw QR code and URL
        draw_qr_pattern(screen, qr_x, qr_y, url)
        screen.blit(url_text, url_rect)
        
        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main()) 