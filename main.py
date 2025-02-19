import pygame
import asyncio
import qrcode
from PIL import Image
import io
import socket

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
QR_SIZE = 150  # Size of the QR code display

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# Create the window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("D&D Sweeper")

def get_local_ip():
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to an external server (doesn't actually send any data)
        s.connect(("8.8.8.8", 80))
        # Get the local IP address
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "localhost"

def generate_qr_code(url):
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create PIL image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Resize the image
    img = img.resize((QR_SIZE, QR_SIZE), Image.Resampling.LANCZOS)
    
    # Convert PIL image to pygame surface
    byte_io = io.BytesIO()
    img.save(byte_io, format='PNG')
    byte_io.seek(0)
    
    return pygame.image.load(byte_io)

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
    # Generate QR code for local URL
    local_ip = get_local_ip()
    url = f"http://{local_ip}:8000"
    qr_surface = generate_qr_code(url)
    
    # Create URL text
    url_font = pygame.font.Font(None, 24)
    url_text = url_font.render(url, True, BLACK)
    url_rect = url_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
    
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

    # Position QR code
    qr_rect = qr_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 150))

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
        screen.blit(qr_surface, qr_rect)
        screen.blit(url_text, url_rect)
        
        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main()) 