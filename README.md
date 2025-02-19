# D&D Sweeper

A dungeon-crawling puzzle game that combines Minesweeper mechanics with D&D elements. Navigate through a procedurally generated dungeon, avoiding monsters and collecting treasures!

## Play Online

You can play the game directly in your browser at: `https://[your-github-username].github.io/d-dsweeper/`

## Features

- Procedurally generated dungeons
- Two types of rooms: Monster (red) and Treasure (gold)
- Connected networks of same-type rooms
- Progressive room size adaptation
- Minesweeper-like number hints
- Browser-based gameplay

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

## Deployment

The game is automatically deployed to GitHub Pages when changes are pushed to the main branch. To set up deployment:

1. Fork or clone this repository
2. Enable GitHub Pages in your repository settings:
   - Go to Settings > Pages
   - Set source to "GitHub Actions"
3. Push changes to the main branch
4. The game will be automatically built and deployed

## How to Play

- Left-click to reveal cells
- Numbers indicate adjacent monsters/treasures
- Red rooms contain monsters
- Gold rooms contain treasures
- Brown paths connect rooms of the same type
- Try to find all treasures while avoiding monsters!

## License

MIT License - feel free to use and modify! 