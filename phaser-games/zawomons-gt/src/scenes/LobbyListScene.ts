import Phaser from 'phaser';

interface Lobby {
    id: number;
    code: string;
    name: string;
    host_username: string;
    game_mode: string;
    current_players_count: number;
    max_players: number;
    is_public: boolean;
}

export default class LobbyListScene extends Phaser.Scene {
    private lobbies: Lobby[] = [];
    private lobbyContainer!: Phaser.GameObjects.Container;

    constructor() {
        super({ key: 'LobbyListScene' });
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
        const title = this.add.text(centerX, 80, 'Public Lobbies', {
            fontSize: '64px',
            fontFamily: 'Arial',
            color: '#ffffff',
            fontStyle: 'bold',
            stroke: '#000000',
            strokeThickness: 6,
        });
        title.setOrigin(0.5);

        // Create lobby button (top left)
        const createButton = this.createButton(180, 80, 'Create Lobby', 0x4CAF50, 250, 50);
        createButton.on('pointerdown', () => this.scene.start('CreateLobbyScene'));

        // Join by code button (top left, next to create)
        const joinButton = this.createButton(460, 80, 'Join by Code', 0x2196F3, 250, 50);
        joinButton.on('pointerdown', () => this.scene.start('JoinLobbyScene'));

        // Refresh button (top right)
        const refreshButton = this.createButton(1740, 80, 'Refresh', 0x757575, 200, 50);
        refreshButton.on('pointerdown', () => this.fetchLobbies());

        // Lobby list container (scrollable area)
        this.lobbyContainer = this.add.container(0, 0);

        // Fetch lobbies
        this.fetchLobbies();
    }

    async fetchLobbies() {
        try {
            console.log('📡 Fetching lobbies...');
            // By default show public lobbies that are waiting
            const response = await fetch('http://localhost:8000/api/v1/zawomons-gt/lobbies/?status=waiting');
            
            if (!response.ok) {
                console.error('❌ Failed to fetch lobbies:', response.status);
                return;
            }

            const data = await response.json();
            this.lobbies = data.results || data;
            console.log(`✅ Loaded ${this.lobbies.length} lobbies`);
            this.displayLobbies();
        } catch (error) {
            console.error('❌ Exception fetching lobbies:', error);
        }
    }

    displayLobbies() {
        this.lobbyContainer.removeAll(true);

        if (this.lobbies.length === 0) {
            const noLobbies = this.add.text(960, 500, 'No lobbies available', {
                fontSize: '32px',
                fontFamily: 'Arial',
                color: '#ffffff',
            });
            noLobbies.setOrigin(0.5);
            this.lobbyContainer.add(noLobbies);
            return;
        }

        this.lobbies.forEach((lobby, index) => {
            const lobbyCard = this.createLobbyCard(lobby, 200, 180 + index * 120);
            this.lobbyContainer.add(lobbyCard);
        });
    }

    createLobbyCard(lobby: Lobby, x: number, y: number) {
        const container = this.add.container(x, y);

        const bg = this.add.rectangle(0, 0, 1520, 100, 0x424242, 0.9);
        bg.setOrigin(0, 0);

        const name = this.add.text(20, 20, lobby.name, {
            fontSize: '28px',
            fontFamily: 'Arial',
            color: '#ffffff',
            fontStyle: 'bold',
        });

        const host = this.add.text(20, 55, `Host: ${lobby.host_username}`, {
            fontSize: '20px',
            fontFamily: 'Arial',
            color: '#e0e0e0',
        });

        const players = this.add.text(800, 35, `Players: ${lobby.current_players_count}/${lobby.max_players}`, {
            fontSize: '24px',
            fontFamily: 'Arial',
            color: '#ffeb3b',
        });

        const code = this.add.text(1100, 35, `Code: ${lobby.code}`, {
            fontSize: '24px',
            fontFamily: 'Arial',
            color: '#4CAF50',
            fontStyle: 'bold',
        });

        const joinButton = this.add.rectangle(1400, 50, 100, 60, 0x4CAF50);
        const joinText = this.add.text(1400, 50, 'Join', {
            fontSize: '24px',
            fontFamily: 'Arial',
            color: '#ffffff',
            fontStyle: 'bold',
        });
        joinText.setOrigin(0.5);

        joinButton.setInteractive({ useHandCursor: true });
        joinButton.on('pointerover', () => joinButton.setFillStyle(0x66BB6A));
        joinButton.on('pointerout', () => joinButton.setFillStyle(0x4CAF50));
        joinButton.on('pointerdown', () => this.joinLobby(lobby.code));

        container.add([bg, name, host, players, code, joinButton, joinText]);

        return container;
    }

    async joinLobby(code: string) {
    const authToken = (window as any).authToken || '';
    const username = (window as any).username || `Guest${Math.floor(Math.random() * 9000) + 100}`;

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
                this.registry.set('lobbyCode', code);
                this.registry.set('username', username);
                this.scene.start('LobbyScene');
            } else {
                const error = await response.json();
                alert(error.error || 'Failed to join lobby');
            }
        } catch (error) {
            console.error('Failed to join lobby:', error);
            alert('Failed to join lobby');
        }
    }

    createButton(x: number, y: number, text: string, color: number, width: number = 300, height: number = 60) {
        const button = this.add.rectangle(x, y, width, height, color);
        const label = this.add.text(x, y, text, {
            fontSize: '24px',
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
