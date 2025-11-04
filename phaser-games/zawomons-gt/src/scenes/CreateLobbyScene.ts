import Phaser from 'phaser';

export default class CreateLobbyScene extends Phaser.Scene {
    private lobbyNameInput: HTMLInputElement | null = null;
    private isPublic: boolean = true;
    private maxPlayers: number = 2;
    private roundDuration: number = 60;
    private cardsPerTurn: number = 5;

    constructor() {
        super({ key: 'CreateLobbyScene' });
    }

    create() {
        const width = 1920;
        const height = 1080;
        const centerX = width / 2;

        // Background
        const graphics = this.add.graphics();
        graphics.fillGradientStyle(0x667eea, 0x667eea, 0x764ba2, 0x764ba2, 1);
        graphics.fillRect(0, 0, width, height);

        // Title
        const title = this.add.text(centerX, 100, 'Create Lobby', {
            fontSize: '64px',
            fontFamily: 'Arial',
            color: '#ffffff',
            fontStyle: 'bold',
            stroke: '#000000',
            strokeThickness: 6,
        });
        title.setOrigin(0.5);

        // Back button
        const backButton = this.createButton(150, 80, 'Back', 0x757575, 200, 50);
        backButton.on('pointerdown', () => {
            this.cleanupInputs();
            this.scene.start('LobbyListScene');
        });

        // Lobby name input
        this.add.text(centerX - 300, 250, 'Lobby Name:', {
            fontSize: '28px',
            fontFamily: 'Arial',
            color: '#ffffff',
        });

        this.createInputField(centerX + 50, 250, 400, 'My Awesome Lobby');

        // Public/Private toggle
        this.add.text(centerX - 300, 350, 'Lobby Type:', {
            fontSize: '28px',
            fontFamily: 'Arial',
            color: '#ffffff',
        });

        const publicButton = this.createToggleButton(centerX - 50, 350, 'Public', true);
        const privateButton = this.createToggleButton(centerX + 150, 350, 'Private', false);

        publicButton.on('pointerdown', () => {
            this.isPublic = true;
            this.updateToggleButtons(publicButton, privateButton);
        });

        privateButton.on('pointerdown', () => {
            this.isPublic = false;
            this.updateToggleButtons(privateButton, publicButton);
        });

        // Settings
        this.add.text(centerX - 600, 500, 'Game Settings', {
            fontSize: '36px',
            fontFamily: 'Arial',
            color: '#ffeb3b',
            fontStyle: 'bold',
        });

        // Max players
        this.createSettingSlider(centerX - 600, 600, 'Max Players:', 2, 8, 2, (value) => {
            this.maxPlayers = value;
        });

        // Round duration
        this.createSettingSlider(centerX - 600, 700, 'Round Duration (s):', 30, 300, 60, (value) => {
            this.roundDuration = value;
        });

        // Cards per turn
        this.createSettingSlider(centerX - 600, 800, 'Cards per Turn:', 1, 10, 5, (value) => {
            this.cardsPerTurn = value;
        });

        // Create button
        const createButton = this.createButton(centerX, 950, 'Create Lobby', 0x4CAF50, 400, 80);
        createButton.on('pointerdown', () => this.createLobby());
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
        input.style.border = '2px solid #4CAF50';
        input.style.borderRadius = '4px';
        input.style.backgroundColor = '#ffffff';
        input.style.color = '#000000';

        // Use Phaser's DOM Element system so it scales with the game
        this.add.dom(x, y, input);
        this.lobbyNameInput = input;
    }    createToggleButton(x: number, y: number, text: string, active: boolean) {
        const button = this.add.rectangle(x, y, 180, 50, active ? 0x4CAF50 : 0x757575);
        const label = this.add.text(x, y, text, {
            fontSize: '24px',
            fontFamily: 'Arial',
            color: '#ffffff',
            fontStyle: 'bold',
        });
        label.setOrigin(0.5);

        button.setInteractive({ useHandCursor: true });
        button.setData('active', active);
        button.setData('label', label);

        return button;
    }

    updateToggleButtons(activeButton: Phaser.GameObjects.Rectangle, inactiveButton: Phaser.GameObjects.Rectangle) {
        activeButton.setFillStyle(0x4CAF50);
        inactiveButton.setFillStyle(0x757575);
    }

    createSettingSlider(x: number, y: number, label: string, min: number, max: number, initial: number, callback: (value: number) => void) {
        this.add.text(x, y, label, {
            fontSize: '24px',
            fontFamily: 'Arial',
            color: '#ffffff',
        });

        const valueText = this.add.text(x + 500, y, `${initial}`, {
            fontSize: '24px',
            fontFamily: 'Arial',
            color: '#ffeb3b',
            fontStyle: 'bold',
        });

        const minusButton = this.createSmallButton(x + 300, y, '-', 0xF44336);
        const plusButton = this.createSmallButton(x + 400, y, '+', 0x4CAF50);

        let currentValue = initial;

        minusButton.on('pointerdown', () => {
            if (currentValue > min) {
                currentValue--;
                valueText.setText(`${currentValue}`);
                callback(currentValue);
            }
        });

        plusButton.on('pointerdown', () => {
            if (currentValue < max) {
                currentValue++;
                valueText.setText(`${currentValue}`);
                callback(currentValue);
            }
        });
    }

    createSmallButton(x: number, y: number, text: string, color: number) {
        const button = this.add.rectangle(x, y, 50, 50, color);
        const label = this.add.text(x, y, text, {
            fontSize: '32px',
            fontFamily: 'Arial',
            color: '#ffffff',
            fontStyle: 'bold',
        });
        label.setOrigin(0.5);

        button.setInteractive({ useHandCursor: true });
        button.on('pointerover', () => button.setScale(1.1));
        button.on('pointerout', () => button.setScale(1));

        return button;
    }

    async createLobby() {
        const lobbyName = this.lobbyNameInput?.value || 'My Lobby';
        const gameMode = this.registry.get('selectedGameMode') || 'classic_1v1';
        const authToken = (window as any).authToken || '';

        console.log('🎮 Creating lobby...');
        console.log('  Lobby name:', lobbyName);
        console.log('  Game mode:', gameMode);
        console.log('  Auth token:', authToken ? `Present (${authToken.length} chars)` : '❌ MISSING');

        if (!authToken) {
            alert('You must be logged in to create a lobby. Token is missing!');
            console.error('❌ Cannot create lobby - no auth token');
            return;
        }

        try {
            console.log('📡 Sending request to backend...');
            const response = await fetch('http://localhost:8000/api/v1/zawomons-gt/lobbies/create_lobby/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`,
                },
                body: JSON.stringify({
                    name: lobbyName,
                    game_mode: gameMode,
                    is_public: this.isPublic,
                    max_players: this.maxPlayers,
                    round_duration: this.roundDuration,
                    cards_per_turn: this.cardsPerTurn,
                }),
            });

            console.log('📡 Response status:', response.status);

            if (response.ok) {
                const lobby = await response.json();
                console.log('✅ Lobby created:', lobby);
                this.cleanupInputs();
                this.registry.set('lobbyCode', lobby.code);
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
        // DOM elements are automatically cleaned up by Phaser scene shutdown
        this.lobbyNameInput = null;
    }

    createButton(x: number, y: number, text: string, color: number, width: number = 300, height: number = 60) {
        const button = this.add.rectangle(x, y, width, height, color);
        const label = this.add.text(x, y, text, {
            fontSize: '28px',
            fontFamily: 'Arial',
            color: '#ffffff',
            fontStyle: 'bold',
        });
        label.setOrigin(0.5);

        button.setInteractive({ useHandCursor: true });
        button.on('pointerover', () => button.setScale(1.05));
        button.on('pointerout', () => button.setScale(1));

        return button;
    }
}
