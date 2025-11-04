import Phaser from 'phaser';

export default class JoinLobbyScene extends Phaser.Scene {
    private codeInput: HTMLInputElement | null = null;

    constructor() {
        super({ key: 'JoinLobbyScene' });
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
        const title = this.add.text(centerX, 300, 'Join Lobby by Code', {
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

        // Code input
        this.add.text(centerX - 200, 500, 'Lobby Code:', {
            fontSize: '32px',
            fontFamily: 'Arial',
            color: '#ffffff',
        });

        this.createInputField(centerX + 100, 500, 300, 'ABC123');

        // Join button
        const joinButton = this.createButton(centerX, 700, 'Join Lobby', 0x4CAF50, 400, 80);
        joinButton.on('pointerdown', () => this.joinLobby());

        // Instructions
        const instructions = this.add.text(centerX, 850, 'Enter the 6-character lobby code to join', {
            fontSize: '24px',
            fontFamily: 'Arial',
            color: '#e0e0e0',
        });
        instructions.setOrigin(0.5);
    }

    createInputField(x: number, y: number, width: number, placeholder: string) {
        const input = document.createElement('input');
        input.type = 'text';
        input.placeholder = placeholder;
        input.maxLength = 6;
        input.style.width = `${width}px`;
        input.style.height = '50px';
        input.style.fontSize = '28px';
        input.style.padding = '10px';
        input.style.border = '2px solid #4CAF50';
        input.style.borderRadius = '4px';
        input.style.backgroundColor = '#ffffff';
        input.style.textAlign = 'center';
        input.style.textTransform = 'uppercase';
        input.style.color = '#000000';

        // Use Phaser's DOM Element system so it scales with the game
        this.add.dom(x, y, input);
        this.codeInput = input;

        input.focus();
    }

    async joinLobby() {
        const code = this.codeInput?.value.toUpperCase() || '';

        if (code.length !== 6) {
            alert('Please enter a valid 6-character code');
            return;
        }

        const authToken = (window as any).authToken || '';
        // Prefer username provided by the parent (no prompt). If missing, generate a guest name.
        const username = (window as any).username || `Guest${Math.floor(Math.random() * 9000) + 100}`;
        // Ensure global username is set so UI shows it
        (window as any).username = username;
        try {
            if (typeof (window as any).updatePlayerInfo === 'function') {
                (window as any).updatePlayerInfo();
            }
        } catch (e) {}

        console.log('🎮 Joining lobby:', code);

        try {
            const response = await fetch(`http://localhost:8000/api/v1/zawomons-gt/lobbies/${code}/join/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(authToken && { 'Authorization': `Bearer ${authToken}` }),
                },
                body: JSON.stringify({
                    guest_username: authToken ? undefined : username,
                }),
            });

            if (response.ok) {
                console.log('✅ Joined lobby');
                this.cleanupInputs();
                this.registry.set('lobbyCode', code);
                this.registry.set('username', username);
                this.registry.set('isHost', false);
                this.scene.start('LobbyScene');
            } else {
                const error = await response.json();
                console.error('❌ Failed to join:', error);
                alert(error.error || 'Failed to join lobby');
            }
        } catch (error) {
            console.error('Failed to join lobby:', error);
            alert('Failed to join lobby. Please check the code and try again.');
        }
    }

    cleanupInputs() {
        // DOM elements are automatically cleaned up by Phaser scene shutdown
        this.codeInput = null;
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

    shutdown() {
        this.cleanupInputs();
    }
}
