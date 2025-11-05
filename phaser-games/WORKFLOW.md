# Phaser Games - Workflow

## Struktura projektu

```
phaser-games/
└── zawomons-gt/              # Kod źródłowy gry
    ├── src/                  # TypeScript source files
    ├── public/               # Static assets
    ├── dist/                 # Build output (gitignored)
    └── scripts/              # Build scripts

frontend/public/games/
└── zawomons-gt/              # Deployed game files
    ├── index.html            # Entry point
    ├── assets/               # Bundled JS + assets
    └── thumbnail.svg         # Game thumbnail
```

## Development workflow

1. **Development mode** (with hot reload):
```bash
cd phaser-games/zawomons-gt
npm run dev
```
Gra będzie dostępna na http://localhost:3001

2. **Build + Deploy**:
```bash
cd phaser-games/zawomons-gt
npm run deploy
```
Lub z głównego folderu:
```bash
cd phaser-games
npm run build:zawomons-gt
```

3. **Manual steps**:
```bash
# Build
npm run build

# Copy to public
npm run copy-to-public
```

## Dodawanie nowej gry Phaser

1. Skopiuj folder `zawomons-gt` jako szablon
2. Zmień nazwę w `package.json`
3. Zaktualizuj `phaser-games/package.json` (dodaj nowy script)
4. Zaktualizuj `scripts/copy-build.js` (zmień ścieżkę docelową)
5. Dodaj grę do `frontend/config/games.ts`
6. Zbuduj i wdeploy: `npm run deploy`
