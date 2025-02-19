# D&D Sweeper

A simple 2D game built with Pygame and Pygbag that combines the classic Minesweeper gameplay with D&D elements.

## Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the game locally:
```bash
python main.py
```

## Web Development and Testing

To test the web version locally:

1. Run the pygbag development server:
```bash
python -m pygbag --port 8000 .
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

The game will be compiled to WebAssembly and served through the browser. You might need to wait a few seconds for the compilation process to complete.

For easy mobile access, the game displays a QR code that you can scan with your smartphone to quickly open the game in your mobile browser. The QR code contains the local network URL of the game.

## Deployment to GitHub Pages

1. Push your changes to GitHub:
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

2. Go to your repository settings on GitHub:
   - Navigate to "Settings" > "Pages"
   - Under "Source", select "GitHub Actions"
   - Your game will be available at: `https://<your-username>.github.io/<repository-name>/`

## Game Controls

- Mouse click to interact with buttons
- More controls will be added as the game develops

## Current Features

- Welcome screen with title
- Interactive "Start Game" button
- QR code for easy mobile access
- Web browser compatibility through Pygbag
