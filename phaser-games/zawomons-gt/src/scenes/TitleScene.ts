import Phaser from 'phaser';
import { Theme, StyledUI } from '../styles/theme';

export default class TitleScene extends Phaser.Scene {
    private titleText!: Phaser.GameObjects.Text;
    private promptText!: Phaser.GameObjects.Text;
    private canStart: boolean = false;
    private tokenReady: boolean = false;

    constructor() {
        super({ key: 'TitleScene' });
    }

    async create() {
        const width = 1920;
        const height = 1080;
        const centerX = width / 2;
        const centerY = height / 2;

        // Background with dark gradient (same as other scenes)
        const graphics = this.add.graphics();
        StyledUI.createGradientBackground(graphics, width, height, 'background');

        // Animated particles in background
        this.createParticles();

        // Decorative card background for title
        const titleCard = this.add.graphics();
        titleCard.fillStyle(parseInt(Theme.colors.card.replace('#', ''), 16), 0.3);
        titleCard.fillRoundedRect(centerX - 500, centerY - 200, 1000, 300, 20);
        titleCard.lineStyle(3, parseInt(Theme.colors.primary.replace('#', ''), 16), 0.5);
        titleCard.strokeRoundedRect(centerX - 500, centerY - 200, 1000, 300, 20);

        // Main title - Zawomons: Grand Tournament
        this.titleText = this.add.text(centerX, centerY - 100, 'ZAWOMONS', {
            fontFamily: 'Arial, sans-serif',
            fontSize: '120px',
            color: Theme.colors.text,
            fontStyle: 'bold',
            stroke: Theme.colors.primary,
            strokeThickness: 6,
            shadow: {
                offsetX: 4,
                offsetY: 4,
                color: Theme.colors.background,
                blur: 8,
                fill: true,
            },
        });
        this.titleText.setOrigin(0.5);
        this.titleText.setAlpha(0);

        // Subtitle with glow effect
        const subtitle = this.add.text(centerX, centerY + 50, 'Grand Tournament', {
            fontFamily: 'Arial, sans-serif',
            fontSize: '48px',
            color: Theme.colors.accent,
            fontStyle: 'bold',
            shadow: {
                offsetX: 2,
                offsetY: 2,
                color: Theme.colors.background,
                blur: 6,
                fill: true,
            },
        });
        subtitle.setOrigin(0.5);
        subtitle.setAlpha(0);

        // Press any key prompt with rounded background
        const promptBg = this.add.graphics();
        promptBg.setAlpha(0);
        
        this.promptText = this.add.text(centerX, centerY + 250, 'Press any key to start', {
            fontFamily: 'Arial, sans-serif',
            fontSize: '32px',
            color: Theme.colors.text,
            fontStyle: 'bold',
        });
        this.promptText.setOrigin(0.5);
        this.promptText.setAlpha(0);

        // Draw rounded background for prompt
        const promptWidth = this.promptText.width + 60;
        const promptHeight = this.promptText.height + 30;
        promptBg.fillStyle(parseInt(Theme.colors.primary.replace('#', ''), 16), 0.2);
        promptBg.fillRoundedRect(centerX - promptWidth/2, centerY + 250 - promptHeight/2, promptWidth, promptHeight, 15);
        promptBg.lineStyle(2, parseInt(Theme.colors.primary.replace('#', ''), 16), 0.8);
        promptBg.strokeRoundedRect(centerX - promptWidth/2, centerY + 250 - promptHeight/2, promptWidth, promptHeight, 15);

        // Animate title entrance
        this.tweens.add({
            targets: this.titleText,
            alpha: 1,
            scale: { from: 0.5, to: 1 },
            duration: 1000,
            ease: 'Back.easeOut',
            onComplete: () => {
                // Floating animation
                this.tweens.add({
                    targets: this.titleText,
                    y: centerY - 110,
                    duration: 2000,
                    yoyo: true,
                    repeat: -1,
                    ease: 'Sine.easeInOut',
                });
            }
        });

        // Animate subtitle
        this.tweens.add({
            targets: subtitle,
            alpha: 1,
            y: { from: centerY + 30, to: centerY + 50 },
            duration: 1000,
            delay: 500,
            ease: 'Power2',
        });

        // Wait for token sync FIRST before showing prompt
        await this.waitForToken();
        this.tokenReady = true;

        // NOW show prompt and enable input
        this.tweens.add({
            targets: this.promptText,
            alpha: 1,
            duration: 1000,
            ease: 'Power2',
            onComplete: () => {
                this.canStart = true;
                // Pulsing animation
                this.tweens.add({
                    targets: this.promptText,
                    alpha: 0.3,
                    duration: 1000,
                    yoyo: true,
                    repeat: -1,
                    ease: 'Sine.easeInOut',
                });
            }
        });

        // Listen for any key press or click
        this.input.keyboard?.on('keydown', () => {
            if (this.canStart) {
                this.startGame();
            }
        });

        this.input.on('pointerdown', () => {
            if (this.canStart) {
                this.startGame();
            }
        });
    }

    async waitForToken(): Promise<void> {
        console.log('🎮 TitleScene: Syncing auth token...');

        // Check if token already exists
        if ((window as any).authToken) {
            console.log('✅ Token already available');
            await this.getUserData();
            return;
        }

        // Wait for token event or timeout
        return new Promise<void>((resolve) => {
            let tokenReceived = false;

            const handleToken = async () => {
                if (!tokenReceived) {
                    tokenReceived = true;
                    console.log('✅ Token event received in TitleScene');
                    await this.getUserData();
                    resolve();
                }
            };

            // Listen for token via Phaser game events
            if ((window as any).phaserGame) {
                (window as any).phaserGame.events.once('authTokenReceived', handleToken);
            }

            // Fallback timeout - proceed without auth after 2 seconds
            this.time.delayedCall(2000, () => {
                if (!tokenReceived) {
                    console.log('⏰ Token timeout in TitleScene - proceeding as guest');
                    tokenReceived = true;
                    if ((window as any).phaserGame) {
                        (window as any).phaserGame.events.off('authTokenReceived', handleToken);
                    }
                    this.setGuestUsername();
                    resolve();
                }
            });
        });
    }

    async getUserData() {
        const authToken = (window as any).authToken || '';
        let username = '';
        let avatar = '';

        if (authToken) {
            try {
                console.log('📡 Fetching user data from API...');
                const response = await fetch('http://localhost:8000/api/v1/users/me/', {
                    headers: {
                        'Authorization': `Bearer ${authToken}`,
                    },
                });

                if (response.ok) {
                    const userData = await response.json();
                    console.log('✅ User data received:', userData);
                    username = userData.username;
                    (window as any).username = username;
                    avatar = userData.avatar || '';
                    if (avatar) (window as any).avatar = avatar;
                    
                    // Update UI
                    try {
                        if (typeof (window as any).updatePlayerInfo === 'function') {
                            (window as any).updatePlayerInfo();
                        }
                    } catch (e) {}
                    
                    console.log('👤 Logged in as:', username);
                    return;
                }
            } catch (error) {
                console.error('❌ Failed to fetch user data:', error);
            }
        }

        // Fallback to guest
        this.setGuestUsername();
    }

    setGuestUsername() {
        const username = 'Guest' + (Math.floor(Math.random() * 9000) + 1000);
        (window as any).username = username;
        console.log('👤 Generated guest username:', username);
        
        try {
            if (typeof (window as any).updatePlayerInfo === 'function') {
                (window as any).updatePlayerInfo();
            }
        } catch (e) {}
    }

    createParticles() {
        // Create some floating particles for visual effect
        const colors = [
            Theme.colors.primary,
            Theme.colors.secondary, 
            Theme.colors.accent,
            Theme.colors.warning,
        ];
        
        for (let i = 0; i < 30; i++) {
            const x = Phaser.Math.Between(0, 1920);
            const y = Phaser.Math.Between(0, 1080);
            const size = Phaser.Math.Between(5, 15);
            const colorHex = colors[i % colors.length];
            const color = Phaser.Display.Color.HexStringToColor(colorHex);
            
            const particle = this.add.circle(x, y, size, color.color, 0.3);
            
            // Random floating animation
            this.tweens.add({
                targets: particle,
                y: y + Phaser.Math.Between(-100, 100),
                x: x + Phaser.Math.Between(-50, 50),
                alpha: { from: 0.1, to: 0.5 },
                duration: Phaser.Math.Between(3000, 6000),
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut',
            });
        }
    }

    startGame() {
        if (!this.canStart || !this.tokenReady) return;

        console.log('🎮 Starting game from TitleScene');
        this.canStart = false;

        // Fade out animation
        this.cameras.main.fadeOut(1000, 0, 0, 0);

        this.cameras.main.once('camerafadeoutcomplete', () => {
            this.scene.start('LobbyListScene');
        });
    }
}
