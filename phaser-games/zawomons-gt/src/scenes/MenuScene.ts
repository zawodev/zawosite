import Phaser from 'phaser';

export default class MenuScene extends Phaser.Scene {
    constructor() {
        super({ key: 'MenuScene' });
    }

    create() {
        const width = 1920;
        const height = 1080;
        const centerX = width / 2;

        // Background gradient
        const graphics = this.add.graphics();
        graphics.fillGradientStyle(0x667eea, 0x667eea, 0x764ba2, 0x764ba2, 1);
        graphics.fillRect(0, 0, width, height);

        // Title
        const title = this.add.text(centerX, 150, 'Zawomons: Grand Tournament', {
            fontSize: '80px',
            fontFamily: 'Arial',
            color: '#ffffff',
            fontStyle: 'bold',
            stroke: '#000000',
            strokeThickness: 8,
        });
        title.setOrigin(0.5);

        // Subtitle
        const subtitle = this.add.text(centerX, 250, 'Select Game Mode', {
            fontSize: '36px',
            fontFamily: 'Arial',
            color: '#e0e0e0',
        });
        subtitle.setOrigin(0.5);

        // Game mode buttons
        this.createModeButton(centerX, 400, 'Classic 1v1', 'classic_1v1', true);
        this.createModeButton(centerX, 520, 'Tournament', 'tournament', false);
        this.createModeButton(centerX, 640, 'Boss Fight', 'boss_fight', false);

        // Create/Join lobby buttons
        const createButton = this.createButton(centerX - 200, 850, 'Create Lobby', 0x4CAF50);
        createButton.on('pointerdown', () => this.scene.start('CreateLobbyScene'));

        const joinButton = this.createButton(centerX + 200, 850, 'Join by Code', 0x2196F3);
        joinButton.on('pointerdown', () => this.scene.start('JoinLobbyScene'));
    }

    createModeButton(x: number, y: number, text: string, mode: string, enabled: boolean) {
        const container = this.add.container(x, y);
        
        const bg = this.add.rectangle(0, 0, 600, 80, enabled ? 0x4CAF50 : 0x757575, enabled ? 1 : 0.5);
        const label = this.add.text(0, 0, text, {
            fontSize: '32px',
            fontFamily: 'Arial',
            color: '#ffffff',
            fontStyle: 'bold',
        });
        label.setOrigin(0.5);

        if (!enabled) {
            const comingSoon = this.add.text(200, 0, 'Coming Soon', {
                fontSize: '18px',
                fontFamily: 'Arial',
                color: '#ffeb3b',
            });
            comingSoon.setOrigin(0.5);
            container.add(comingSoon);
        }

        container.add([bg, label]);

        if (enabled) {
            bg.setInteractive({ useHandCursor: true });
            bg.on('pointerover', () => bg.setFillStyle(0x66BB6A));
            bg.on('pointerout', () => bg.setFillStyle(0x4CAF50));
            bg.on('pointerdown', () => {
                this.registry.set('selectedGameMode', mode);
                this.scene.start('LobbyListScene');
            });
        }

        return container;
    }

    createButton(x: number, y: number, text: string, color: number) {
        const button = this.add.rectangle(x, y, 350, 70, color);
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
