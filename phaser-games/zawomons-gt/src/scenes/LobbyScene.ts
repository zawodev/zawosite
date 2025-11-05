import Phaser from 'phaser';
import { Theme, StyledUI } from '../styles/theme';

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
    private readyButtonLabel!: Phaser.GameObjects.Text;
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

        // Background with gradient
        const graphics = this.add.graphics();
        StyledUI.createGradientBackground(graphics, width, height, 'background');

        // Title
        const title = this.add.text(centerX, 80, 'Lobby', Theme.text.title);
        title.setOrigin(0.5);

        // Lobby code with copy button
        const codeText = this.add.text(centerX - 100, 160, `Code: ${this.lobbyCode}`, {
            ...Theme.text.heading,
            color: Theme.colors.primary,
        });
        codeText.setOrigin(0.5);

        // Copy code button
        StyledUI.createStyledButton(
            this, centerX + 150, 160, '📋 Copy', 'secondary', 150, 50,
            () => {
                navigator.clipboard.writeText(this.lobbyCode).then(() => {
                    console.log('✅ Code copied to clipboard:', this.lobbyCode);
                    const feedback = this.add.text(centerX + 150, 220, 'Copied!', {
                        fontSize: '20px',
                        color: Theme.colors.primary,
                    });
                    feedback.setOrigin(0.5);
                    this.time.delayedCall(2000, () => feedback.destroy());
                }).catch(err => {
                    console.error('❌ Failed to copy:', err);
                });
            }
        );

        // Leave button
        StyledUI.createStyledButton(
            this, 150, 80, 'Leave', 'danger', 200, 50,
            () => this.leaveLobby()
        );

        // Players section
        this.add.text(300, 250, 'Players', {
            ...Theme.text.subtitle,
            color: Theme.colors.accent,
        });

        this.playerContainer = this.add.container(0, 0);

        // Settings section (right side)
        this.add.text(1100, 250, 'Settings', {
            ...Theme.text.subtitle,
            color: Theme.colors.accent,
        });

        this.settingsContainer = this.add.container(0, 0);

        // Ready/Start buttons
        if (this.isHost) {
            this.startButton = this.createButton(centerX, 950, 'Start Game', 0x4CAF50, 400, 80);
            this.startButton.on('pointerdown', () => this.startGame());
            this.startButton.setAlpha(0.5);
            this.startButton.disableInteractive();
        } else {
            const result = this.createButtonWithLabel(centerX, 950, 'Ready', 0x2196F3, 400, 80);
            this.readyButton = result.button;
            this.readyButtonLabel = result.label;
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
            
            // Send guest_username immediately after connection to identify player
            const authToken = (window as any).authToken || '';
            if (!authToken && this.username) {
                console.log('👤 Sending guest identification:', this.username);
                this.ws?.send(JSON.stringify({
                    type: 'identify',
                    guest_username: this.username
                }));
            }
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
            case 'lobby_closed':
                console.log('🚪 Lobby closed:', data.reason);
                this.handleLobbyClosed(data.reason);
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

    handleLobbyClosed(reason: string) {
        // Show notification
        const notification = this.add.text(960, 540, reason, {
            fontSize: '32px',
            color: Theme.colors.danger,
            backgroundColor: Theme.colors.background,
            padding: { x: 30, y: 20 },
        });
        notification.setOrigin(0.5);
        notification.setDepth(1000);

        // Close WebSocket
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        // Return to lobby list after 2 seconds
        this.time.delayedCall(2000, () => {
            this.scene.start('LobbyListScene');
        });
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
        if (!this.lobbyData) {
            console.log('⚠️ No lobby data');
            return;
        }

        console.log('👥 Updating players list:', this.lobbyData.players);

        this.playerContainer.removeAll(true);

        if (!this.lobbyData.players || this.lobbyData.players.length === 0) {
            console.log('⚠️ No players in lobby data');
            // Show "No players" message
            const noPlayers = this.add.text(300, 320, 'No players yet...', {
                fontSize: '24px',
                fontFamily: 'Arial',
                color: '#999999',
            });
            this.playerContainer.add(noPlayers);
            return;
        }

        this.lobbyData.players.forEach((player, index) => {
            console.log(`  Player ${index}:`, player.display_name, player.is_ready ? '✅' : '⏳');
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

        // Ready status indicator - colored dot next to name
        const readyDot = this.add.circle(95, 35, 8, player.is_ready ? 0x4CAF50 : 0x757575);

        // Name
        const name = this.add.text(110, 25, player.display_name, {
            fontSize: '28px',
            fontFamily: 'Arial',
            color: '#ffffff',
            fontStyle: 'bold',
        });

        // Host/Creator badge
        if (this.lobbyData && player.display_name === this.lobbyData.host_username) {
            const hostBadge = this.add.text(110, 60, '👑 Creator', {
                fontSize: '18px',
                fontFamily: 'Arial',
                color: '#FFD700',
            });
            container.add(hostBadge);
        }

        container.add([bg, avatar, readyDot, name]);

        return container;
    }

    updateSettings() {
        if (!this.lobbyData) return;

        this.settingsContainer.removeAll(true);

        const settings = [
            { label: 'Game Mode:', value: this.formatGameMode(this.lobbyData.game_mode) },
            { label: 'Max Players:', value: `${this.lobbyData.max_players}` },
            { label: 'Players:', value: `${this.lobbyData.current_players_count}/${this.lobbyData.max_players}` },
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

        // Update button appearance using stored reference
        if (this.readyButton && this.readyButtonLabel) {
            this.readyButton.setFillStyle(this.isReady ? 0x4CAF50 : 0x2196F3);
            this.readyButtonLabel.setText(this.isReady ? 'Not Ready' : 'Ready');
        }
    }

    async startGame() {
        const authToken = (window as any).authToken || '';
        const username = this.username || (window as any).username;

        try {
            const response = await fetch(`http://localhost:8000/api/v1/zawomons-gt/lobbies/${this.lobbyCode}/start/`, {
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

        console.log('🚪 Leaving lobby...');

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
            console.log('✅ Left lobby successfully');
        } catch (error) {
            console.error('❌ Failed to leave lobby:', error);
        }

        this.closeWebSocket();
        this.scene.start('LobbyListScene');
    }

    startGameplay() {
        this.closeWebSocket();
        console.log('🎮 Game starting!');
        // TODO: Start actual game
        alert('Game starting! (Gameplay not yet implemented)');
        this.scene.start('LobbyListScene');
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

        button.setInteractive({ useHandCursor: true });
        button.on('pointerover', () => button.setScale(1.05));
        button.on('pointerout', () => button.setScale(1));

        return button;
    }

    createButtonWithLabel(x: number, y: number, text: string, color: number, width: number = 300, height: number = 60) {
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

        return { button, label };
    }

    shutdown() {
        this.closeWebSocket();
    }
}
