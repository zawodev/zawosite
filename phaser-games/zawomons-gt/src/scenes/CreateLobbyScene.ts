import Phaser from 'phaser';
import { Theme, StyledUI } from '../styles/theme';

type GameMode = 'classic_1v1' | 'tournament' | 'boss_fight';

interface GameModeOption {
    key: GameMode;
    name: string;
    description: string;
    maxPlayers: number;
    enabled: boolean;
}

export default class CreateLobbyScene extends Phaser.Scene {
    private lobbyNameInput: HTMLInputElement | null = null;
    private isPublic: boolean = true;
    private selectedGameMode: GameMode = 'classic_1v1';
    private gameModeButtons: Map<GameMode, { button: Phaser.GameObjects.Rectangle; label: Phaser.GameObjects.Text; desc: Phaser.GameObjects.Text; badge?: Phaser.GameObjects.Text }> = new Map();

    private readonly gameModes: GameModeOption[] = [
        { key: 'classic_1v1', name: 'Classic 1v1', description: '2 players battle', maxPlayers: 2, enabled: true },
        { key: 'tournament', name: 'Tournament', description: '4+ players bracket', maxPlayers: 4, enabled: false },
        { key: 'boss_fight', name: 'Boss Battle', description: 'Co-op vs AI boss', maxPlayers: 4, enabled: false },
    ];

    constructor() {
        super({ key: 'CreateLobbyScene' });
    }

    create() {
        const width = 1920;
        const height = 1080;
        const centerX = width / 2;

        // Background with gradient
        const graphics = this.add.graphics();
        StyledUI.createGradientBackground(graphics, width, height, 'background');

        // Title
        const title = this.add.text(centerX, 100, 'Create Lobby', Theme.text.title);
        title.setOrigin(0.5);

        // Back button
        StyledUI.createStyledButton(
            this, 150, 80, 'Back', 'secondary', 200, 50,
            () => {
                this.cleanupInputs();
                this.scene.start('LobbyListScene');
            }
        );

        // Lobby name input
        this.add.text(centerX - 300, 300, 'Lobby Name:', Theme.text.body);
        this.createInputField(centerX + 50, 300, 400, 'My Awesome Lobby');

        // Public/Private toggle
        this.add.text(centerX - 300, 400, 'Lobby Type:', Theme.text.body);

        const publicButton = this.createToggleButton(centerX - 50, 400, 'Public', true);
        const privateButton = this.createToggleButton(centerX + 150, 400, 'Private', false);

        publicButton.on('pointerdown', () => {
            this.isPublic = true;
            this.updateToggleButtons(publicButton, privateButton);
        });

        privateButton.on('pointerdown', () => {
            this.isPublic = false;
            this.updateToggleButtons(privateButton, publicButton);
        });

        // Game mode selection
        this.add.text(centerX - 300, 500, 'Game Mode:', Theme.text.body);
        this.createGameModeSelector(centerX, 580);

        // Create button
        StyledUI.createStyledButton(
            this, centerX, 800, 'Create Lobby', 'primary', 400, 80,
            () => this.createLobby()
        );
    }

    createInputField(x: number, y: number, width: number, placeholder: string) {
        const input = document.createElement('input');
        input.type = 'text';
        input.placeholder = placeholder;
        input.value = placeholder;
        input.style.width = `${width}px`;
        input.style.height = '40px';
        input.style.fontSize = '20px';
        input.style.padding = '8px';
        input.style.border = `2px solid ${Theme.colors.primary}`;
        input.style.borderRadius = '8px';
        input.style.backgroundColor = '#ffffff';
        input.style.color = '#000000';

        this.add.dom(x, y, input);
        this.lobbyNameInput = input;
    }

    createToggleButton(x: number, y: number, text: string, active: boolean) {
        const colorHex = active ? Theme.colors.primary : Theme.colors.surface;
        const colorNum = parseInt(colorHex.replace('#', ''), 16);
        
        const button = this.add.rectangle(x, y, 180, 50, colorNum);
        const label = this.add.text(x, y, text, Theme.text.body);
        label.setOrigin(0.5);

        button.setInteractive({ useHandCursor: true });
        button.setData('active', active);

        return button;
    }

    updateToggleButtons(activeButton: Phaser.GameObjects.Rectangle, inactiveButton: Phaser.GameObjects.Rectangle) {
        const activeColor = parseInt(Theme.colors.primary.replace('#', ''), 16);
        const inactiveColor = parseInt(Theme.colors.surface.replace('#', ''), 16);
        
        activeButton.setFillStyle(activeColor);
        inactiveButton.setFillStyle(inactiveColor);
    }

    createGameModeSelector(centerX: number, startY: number) {
        const cardWidth = 350;
        const cardHeight = 120;
        const spacing = 30;

        this.gameModes.forEach((mode, index) => {
            const x = centerX - (this.gameModes.length - 1) * (cardWidth + spacing) / 2 + index * (cardWidth + spacing);
            const y = startY;

            // Card background
            const isSelected = mode.key === this.selectedGameMode;
            const isEnabled = mode.enabled;
            
            let cardColor: number;
            if (!isEnabled) {
                cardColor = parseInt(Theme.colors.surface.replace('#', ''), 16);
            } else if (isSelected) {
                cardColor = parseInt(Theme.colors.primary.replace('#', ''), 16);
            } else {
                cardColor = parseInt(Theme.colors.card.replace('#', ''), 16);
            }

            const card = this.add.rectangle(x, y, cardWidth, cardHeight, cardColor, isEnabled ? 1 : 0.4);
            card.setStrokeStyle(3, parseInt(Theme.colors.primary.replace('#', ''), 16), isSelected ? 1 : 0.3);

            if (isEnabled) {
                card.setInteractive({ useHandCursor: true });
                card.on('pointerdown', () => this.selectGameMode(mode.key));
                
                // Hover effect
                card.on('pointerover', () => {
                    if (this.selectedGameMode !== mode.key) {
                        card.setFillStyle(parseInt(Theme.colors.card.replace('#', ''), 16), 0.8);
                    }
                });
                card.on('pointerout', () => {
                    if (this.selectedGameMode !== mode.key) {
                        card.setFillStyle(parseInt(Theme.colors.card.replace('#', ''), 16), 1);
                    }
                });
            }

            // Mode name
            const nameText = this.add.text(x, y - 30, mode.name, {
                ...Theme.text.subtitle,
                fontSize: '24px',
                color: isEnabled ? Theme.colors.text : Theme.colors.textSecondary,
            });
            nameText.setOrigin(0.5);
            nameText.setAlpha(isEnabled ? 1 : 0.5);

            // Description
            const descText = this.add.text(x, y + 5, mode.description, {
                ...Theme.text.body,
                fontSize: '18px',
                color: Theme.colors.textSecondary,
            });
            descText.setOrigin(0.5);
            descText.setAlpha(isEnabled ? 1 : 0.5);

            // Players info
            const playersText = this.add.text(x, y + 35, `${mode.maxPlayers} Players`, {
                ...Theme.text.body,
                fontSize: '16px',
                color: Theme.colors.accent,
            });
            playersText.setOrigin(0.5);
            playersText.setAlpha(isEnabled ? 1 : 0.5);

            // "Coming Soon" badge for disabled modes
            let badge: Phaser.GameObjects.Text | undefined;
            if (!isEnabled) {
                badge = this.add.text(x, y - 50, 'COMING SOON', {
                    fontFamily: 'Arial, sans-serif',
                    fontSize: '14px',
                    color: Theme.colors.warning,
                    fontStyle: 'bold',
                });
                badge.setOrigin(0.5);
                badge.setAlpha(0.8);
            }

            this.gameModeButtons.set(mode.key, { button: card, label: nameText, desc: descText, badge });
        });
    }

    selectGameMode(mode: GameMode) {
        const modeOption = this.gameModes.find(m => m.key === mode);
        if (!modeOption || !modeOption.enabled) return;

        this.selectedGameMode = mode;

        // Update all cards
        this.gameModeButtons.forEach((elements, key) => {
            const isSelected = key === mode;
            const modeData = this.gameModes.find(m => m.key === key)!;
            
            if (modeData.enabled) {
                const cardColor = isSelected 
                    ? parseInt(Theme.colors.primary.replace('#', ''), 16)
                    : parseInt(Theme.colors.card.replace('#', ''), 16);
                elements.button.setFillStyle(cardColor);
                elements.button.setStrokeStyle(3, parseInt(Theme.colors.primary.replace('#', ''), 16), isSelected ? 1 : 0.3);
            }
        });
    }

    async createLobby() {
        const lobbyName = this.lobbyNameInput?.value || 'My Lobby';
        const authToken = (window as any).authToken || '';
        const username = (window as any).username || `Guest${Math.floor(Math.random() * 9000) + 1000}`;
        const selectedMode = this.gameModes.find(m => m.key === this.selectedGameMode)!;

        console.log('🎮 Creating lobby...');
        console.log('  Lobby name:', lobbyName);
        console.log('  Game mode:', this.selectedGameMode);
        console.log('  Max players:', selectedMode.maxPlayers);
        console.log('  Auth token:', authToken ? `Present (${authToken.length} chars)` : '❌ None (guest mode)');
        console.log('  Username:', username);

        try {
            console.log('📡 Sending request to backend...');
            const response = await fetch('http://localhost:8000/api/v1/zawomons-gt/lobbies/create_lobby/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(authToken && { 'Authorization': `Token ${authToken}` }),
                },
                body: JSON.stringify({
                    name: lobbyName,
                    game_mode: this.selectedGameMode,
                    is_public: this.isPublic,
                    max_players: selectedMode.maxPlayers,
                    guest_username: authToken ? undefined : username,
                }),
            });

            console.log('📡 Response status:', response.status);

            if (response.ok) {
                const lobby = await response.json();
                console.log('✅ Lobby created:', lobby);
                this.cleanupInputs();
                this.registry.set('lobbyCode', lobby.code);
                this.registry.set('username', username);
                this.registry.set('isHost', true);
                this.scene.start('LobbyScene');
            } else {
                const error = await response.json();
                console.error('❌ Failed to create lobby:', error);
                alert(error.error || 'Failed to create lobby');
            }
        } catch (error) {
            console.error('❌ Exception while creating lobby:', error);
            alert('Failed to create lobby');
        }
    }

    cleanupInputs() {
        this.lobbyNameInput = null;
    }

    shutdown() {
        this.cleanupInputs();
    }
}
