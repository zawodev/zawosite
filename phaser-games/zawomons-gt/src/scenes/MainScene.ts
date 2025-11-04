import Phaser from 'phaser';

export default class MainScene extends Phaser.Scene {
    private authToken: string = '';

    constructor() {
        super({ key: 'MainScene' });
    }

    create() {
        const graphics = this.add.graphics();
        graphics.fillGradientStyle(0x667eea, 0x667eea, 0x764ba2, 0x764ba2, 1);
        graphics.fillRect(0, 0, 1920, 1080);

        const titleText = this.add.text(960, 200, 'Zawomons: Grand Tournament', {
            fontSize: '80px',
            fontFamily: 'Arial',
            color: '#ffffff',
            fontStyle: 'bold',
            stroke: '#000000',
            strokeThickness: 6,
        });
        titleText.setOrigin(0.5);

        const subtitleText = this.add.text(960, 300, 'Powered by Phaser + TypeScript + Vite', {
            fontSize: '32px',
            fontFamily: 'Arial',
            color: '#e0e0e0',
            fontStyle: 'italic',
        });
        subtitleText.setOrigin(0.5);

        const welcomeText = this.add.text(960, 500, 'Click anywhere to create effects!', {
            fontSize: '28px',
            fontFamily: 'Arial',
            color: '#ffffff',
            align: 'center',
        });
        welcomeText.setOrigin(0.5);

        this.tokenText = this.add.text(960, 650, 'Waiting for auth token...', {
            fontSize: '22px',
            fontFamily: 'Arial',
            color: '#ffff00',
        });
        this.tokenText.setOrigin(0.5);

        const zawomons = this.add.rectangle(960, 800, 150, 150, 0x4CAF50);
        const zawoText = this.add.text(960, 800, '🐉', { fontSize: '100px' });
        zawoText.setOrigin(0.5);

        this.tweens.add({
            targets: [zawomons, zawoText],
            y: '+=20',
            duration: 1500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut',
        });

        this.tweens.add({
            targets: zawomons,
            angle: 360,
            duration: 4000,
            repeat: -1,
            ease: 'Linear',
        });

        this.tweens.add({
            targets: welcomeText,
            alpha: 0.5,
            duration: 1000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut',
        });

        this.input.on('pointerdown', (pointer: Phaser.Input.Pointer) => {
            this.createClickEffect(pointer.x, pointer.y);
        });

        if ((window as any).phaserGame) {
            (window as any).phaserGame.events.on('authTokenReceived', (token: string) => {
                this.authToken = token;
                this.updateTokenStatus();
            });
        }

        if ((window as any).authToken) {
            this.authToken = (window as any).authToken;
            this.updateTokenStatus();
        }
    }

    private tokenText!: Phaser.GameObjects.Text;

    private createClickEffect(x: number, y: number) {
        const colors = [0xff0000, 0x00ff00, 0x0000ff, 0xffff00, 0xff00ff, 0x00ffff];
        const color = colors[Math.floor(Math.random() * colors.length)];

        const circle = this.add.circle(x, y, 20, color, 0.8);

        this.tweens.add({
            targets: circle,
            scale: 3,
            alpha: 0,
            duration: 800,
            ease: 'Power2',
            onComplete: () => {
                circle.destroy();
            },
        });

        const clickText = this.add.text(x, y - 30, 'Click!', {
            fontSize: '20px',
            color: '#ffffff',
            fontStyle: 'bold',
        });
        clickText.setOrigin(0.5);

        this.tweens.add({
            targets: clickText,
            y: y - 80,
            alpha: 0,
            duration: 800,
            ease: 'Power2',
            onComplete: () => {
                clickText.destroy();
            },
        });
    }

    private updateTokenStatus() {
        if (this.authToken) {
            this.tokenText.setText('✓ Auth token received');
            this.tokenText.setColor('#00ff00');
            console.log('Token updated:', this.authToken.substring(0, 10) + '...');
        } else {
            this.tokenText.setText('⚠ No token (playing as guest)');
            this.tokenText.setColor('#ff9800');
        }
    }
}
