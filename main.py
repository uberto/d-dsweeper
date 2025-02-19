import pygame
import asyncio

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# Create the window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("D&D Sweeper")

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
        
        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main()) 