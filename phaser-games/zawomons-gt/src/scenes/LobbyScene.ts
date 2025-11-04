import Phaser from 'phaser';

interface Player {
    id: number;
    display_name: string;
    avatar_url: string | null;
    is_ready: boolean;
}

interface LobbyData {
    id: number;
    code: string;
    name: string;
    host_username: string;
    game_mode: string;
    is_public: boolean;
    max_players: number;
    current_players_count: number;
    round_duration: number;
    cards_per_turn: number;
    players: Player[];
    can_start: boolean;
}

export default class LobbyScene extends Phaser.Scene {
    private ws: WebSocket | null = null;
    private lobbyCode: string = '';
    private username: string = '';
    private isHost: boolean = false;
    private lobbyData: LobbyData | null = null;
    private playerContainer!: Phaser.GameObjects.Container;
    private settingsContainer!: Phaser.GameObjects.Container;
    private startButton!: Phaser.GameObjects.Rectangle;
    private readyButton!: Phaser.GameObjects.Rectangle;
    private isReady: boolean = false;

    constructor() {
        super({ key: 'LobbyScene' });
    }

    create() {
        this.lobbyCode = this.registry.get('lobbyCode');
        this.username = this.registry.get('username') || (window as any).username;
        this.isHost = this.registry.get('isHost') || false;

        const width = 1920;
        const height = 1080;
        const centerX = width / 2;

        // Background
        const graphics = this.add.graphics();
        graphics.fillGradientStyle(0x667eea, 0x667eea, 0x764ba2, 0x764ba2, 1);
        graphics.fillRect(0, 0, width, height);

        // Title
        const title = this.add.text(centerX, 80, 'Lobby', {
            fontSize: '64px',
            fontFamily: 'Arial',
            color: '#ffffff',
            fontStyle: 'bold',
            stroke: '#000000',
            strokeThickness: 6,
        });
        title.setOrigin(0.5);

        // Lobby code
        const codeText = this.add.text(centerX, 160, `Code: ${this.lobbyCode}`, {
            fontSize: '36px',
            fontFamily: 'Arial',
            color: '#4CAF50',
            fontStyle: 'bold',
        });
        codeText.setOrigin(0.5);

        // Leave button
        const leaveButton = this.createButton(150, 80, 'Leave', 0xF44336, 200, 50);
        leaveButton.on('pointerdown', () => this.leaveLobby());

        // Players section
        this.add.text(300, 250, 'Players', {
            fontSize: '42px',
            fontFamily: 'Arial',
            color: '#ffeb3b',
            fontStyle: 'bold',
        });

        this.playerContainer = this.add.container(0, 0);

        // Settings section (right side)
        this.add.text(1100, 250, 'Settings', {
            fontSize: '42px',
            fontFamily: 'Arial',
            color: '#ffeb3b',
            fontStyle: 'bold',
        });

        this.settingsContainer = this.add.container(0, 0);

        // Ready/Start buttons
        if (this.isHost) {
            this.startButton = this.createButton(centerX, 950, 'Start Game', 0x4CAF50, 400, 80);
            this.startButton.on('pointerdown', () => this.startGame());
            this.startButton.setAlpha(0.5);
            this.startButton.disableInteractive();
        } else {
            this.readyButton = this.createButton(centerX, 950, 'Ready', 0x2196F3, 400, 80);
            this.readyButton.on('pointerdown', () => this.toggleReady());
        }

        // Connect WebSocket
        this.connectWebSocket();
    }

    connectWebSocket() {
        const wsUrl = `ws://localhost:8000/ws/zawomons-gt/lobby/${this.lobbyCode}/`;
        console.log('🔌 Connecting to WebSocket:', wsUrl);
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('✅ WebSocket connected');
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('📨 WebSocket message:', data.type);
            this.handleWebSocketMessage(data);
        };

        this.ws.onerror = (error) => {
            console.error('❌ WebSocket error:', error);
        };

        this.ws.onclose = () => {
            console.log('🔌 WebSocket disconnected');
        };
    }

    handleWebSocketMessage(data: any) {
        console.log('📨 Processing message:', data);
        switch (data.type) {
            case 'lobby_state':
                this.lobbyData = data.lobby;
                console.log('📊 Lobby state:', this.lobbyData);
                this.updateLobbyUI();
                break;
            case 'player_joined':
                console.log('👤 Player joined:', data.player);
                break;
            case 'player_left':
                console.log('👤 Player left:', data.player_id);
                break;
            case 'game_started':
                console.log('🎮 Game started!');
                this.startGameplay();
                break;
            case 'chat':
                console.log(`💬 ${data.username}: ${data.message}`);
                break;
        }
    }

    updateLobbyUI() {
        if (!this.lobbyData) return;

        // Update players list
        this.updatePlayersList();

        // Update settings
        this.updateSettings();

        // Update start button
        if (this.isHost && this.startButton) {
            if (this.lobbyData.can_start) {
                this.startButton.setAlpha(1);
                this.startButton.setInteractive({ useHandCursor: true });
            } else {
                this.startButton.setAlpha(0.5);
                this.startButton.disableInteractive();
            }
        }
    }

    updatePlayersList() {
        if (!this.lobbyData) return;

        this.playerContainer.removeAll(true);

        this.lobbyData.players.forEach((player, index) => {
            const playerCard = this.createPlayerCard(player, 300, 320 + index * 120);
            this.playerContainer.add(playerCard);
        });
    }

    createPlayerCard(player: Player, x: number, y: number) {
        const container = this.add.container(x, y);

        // Background
        const bg = this.add.rectangle(0, 0, 700, 100, 0x424242, 0.9);
        bg.setOrigin(0, 0);

        // Avatar placeholder
        const avatar = this.add.circle(50, 50, 35, 0x2196F3);

        // Name
        const name = this.add.text(100, 25, player.display_name, {
            fontSize: '28px',
            fontFamily: 'Arial',
            color: '#ffffff',
            fontStyle: 'bold',
        });

        // Ready status
        const readyBg = this.add.rectangle(550, 50, 120, 50, player.is_ready ? 0x4CAF50 : 0x757575);
        const readyText = this.add.text(550, 50, player.is_ready ? 'Ready' : 'Not Ready', {
            fontSize: '20px',
            fontFamily: 'Arial',
            color: '#ffffff',
        });
        readyText.setOrigin(0.5);

        // Host badge
        if (this.lobbyData && player.display_name === this.lobbyData.host_username) {
            const hostBadge = this.add.text(100, 60, '👑 Host', {
                fontSize: '18px',
                fontFamily: 'Arial',
                color: '#FFD700',
            });
            container.add(hostBadge);
        }

        container.add([bg, avatar, name, readyBg, readyText]);

        return container;
    }

    updateSettings() {
        if (!this.lobbyData) return;

        this.settingsContainer.removeAll(true);

        const settings = [
            { label: 'Game Mode:', value: this.formatGameMode(this.lobbyData.game_mode) },
            { label: 'Max Players:', value: `${this.lobbyData.max_players}` },
            { label: 'Players:', value: `${this.lobbyData.current_players_count}/${this.lobbyData.max_players}` },
            { label: 'Round Duration:', value: `${this.lobbyData.round_duration}s` },
            { label: 'Cards per Turn:', value: `${this.lobbyData.cards_per_turn}` },
            { label: 'Lobby Type:', value: this.lobbyData.is_public ? 'Public' : 'Private' },
        ];

        settings.forEach((setting, index) => {
            const y = 320 + index * 70;
            
            const label = this.add.text(1100, y, setting.label, {
                fontSize: '24px',
                fontFamily: 'Arial',
                color: '#e0e0e0',
            });

            const value = this.add.text(1100, y + 30, setting.value, {
                fontSize: '28px',
                fontFamily: 'Arial',
                color: '#ffffff',
                fontStyle: 'bold',
            });

            this.settingsContainer.add([label, value]);
        });
    }

    formatGameMode(mode: string): string {
        const modes: { [key: string]: string } = {
            'classic_1v1': 'Classic 1v1',
            'tournament': 'Tournament',
            'boss_fight': 'Boss Fight',
        };
        return modes[mode] || mode;
    }

    toggleReady() {
        this.isReady = !this.isReady;

        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'player_ready',
                is_ready: this.isReady,
                guest_username: this.username,
            }));
        }

        // Update button appearance
        if (this.readyButton) {
            this.readyButton.setFillStyle(this.isReady ? 0x4CAF50 : 0x2196F3);
            const label = this.children.getByName('readyLabel') as Phaser.GameObjects.Text;
            if (label) {
                label.setText(this.isReady ? 'Not Ready' : 'Ready');
            }
        }
    }

    async startGame() {
        const authToken = (window as any).authToken || '';

        try {
            const response = await fetch(`http://localhost:8000/api/v1/zawomons-gt/lobbies/${this.lobbyCode}/start/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`,
                },
            });

            if (response.ok) {
                // Game will start via WebSocket message
            } else {
                const error = await response.json();
                alert(error.error || 'Failed to start game');
            }
        } catch (error) {
            console.error('Failed to start game:', error);
            alert('Failed to start game');
        }
    }

    async leaveLobby() {
        const authToken = (window as any).authToken || '';

        try {
            await fetch(`http://localhost:8000/api/v1/zawomons-gt/lobbies/${this.lobbyCode}/leave/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(authToken && { 'Authorization': `Bearer ${authToken}` }),
                },
                body: JSON.stringify({
                    guest_username: this.username,
                }),
            });
        } catch (error) {
            console.error('Failed to leave lobby:', error);
        }

        this.closeWebSocket();
        this.scene.start('MenuScene');
    }

    startGameplay() {
        this.closeWebSocket();
        // TODO: Start actual game
        alert('Game starting! (Gameplay not yet implemented)');
        this.scene.start('MenuScene');
    }

    closeWebSocket() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
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
        label.setName('readyLabel');

        button.setInteractive({ useHandCursor: true });
        button.on('pointerover', () => button.setScale(1.05));
        button.on('pointerout', () => button.setScale(1));

        return button;
    }

    shutdown() {
        this.closeWebSocket();
    }
}
