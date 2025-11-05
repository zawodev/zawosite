// Game Theme - Easy to customize color palette
export const Theme = {
    // Primary colors (hex strings for VS Code color picker!)
    colors: {
        primary: '#667eea',      // Purple-blue
        secondary: '#764ba2',    // Deep purple
        accent: '#4CAF50',       // Green
        danger: '#F44336',       // Red
        warning: '#FFEB3B',      // Yellow
        info: '#2196F3',         // Blue
        success: '#4CAF50',      // Green
        background: '#1a1a2e',   // Dark blue-gray
        surface: '#16213e',      // Slightly lighter
        card: '#0f3460',         // Card background
        text: '#ffffff',         // White
        textSecondary: '#e0e0e0', // Light gray
        textDisabled: '#999999',  // Gray
        border: '#4ecca3',       // Cyan accent
    },

    // Text styles
    text: {
        title: {
            fontSize: '64px',
            fontFamily: 'Arial, sans-serif',
            color: '#ffffff',
            fontStyle: 'bold',
            stroke: '#000000',
            strokeThickness: 6,
        },
        subtitle: {
            fontSize: '36px',
            fontFamily: 'Arial, sans-serif',
            color: '#e0e0e0',
        },
        heading: {
            fontSize: '42px',
            fontFamily: 'Arial, sans-serif',
            color: '#ffeb3b',
            fontStyle: 'bold',
        },
        body: {
            fontSize: '28px',
            fontFamily: 'Arial, sans-serif',
            color: '#ffffff',
        },
        bodySmall: {
            fontSize: '24px',
            fontFamily: 'Arial, sans-serif',
            color: '#ffffff',
        },
        label: {
            fontSize: '20px',
            fontFamily: 'Arial, sans-serif',
            color: '#e0e0e0',
        },
    },

    // Button styles
    button: {
        primary: {
            color: '#4CAF50',
            hoverColor: '#66BB6A',
            textColor: '#ffffff',
        },
        secondary: {
            color: '#2196F3',
            hoverColor: '#42A5F5',
            textColor: '#ffffff',
        },
        danger: {
            color: '#F44336',
            hoverColor: '#E57373',
            textColor: '#ffffff',
        },
        disabled: {
            color: '#757575',
            hoverColor: '#757575',
            textColor: '#999999',
        },
    },

    // Card/Panel styles
    card: {
        backgroundColor: '#0f3460',
        borderColor: '#4ecca3',
        alpha: 0.9,
    },

    // Gradients
    gradients: {
        background: {
            topLeft: '#1a1a2e',
            topRight: '#1a1a2e',
            bottomLeft: '#16213e',
            bottomRight: '#0f3460',
        },
        accent: {
            topLeft: '#667eea',
            topRight: '#667eea',
            bottomLeft: '#764ba2',
            bottomRight: '#764ba2',
        },
    },

    // Layout
    layout: {
        padding: 20,
        margin: 10,
        borderRadius: 8,
        cardHeight: 100,
        buttonHeight: 60,
    },
};

// Helper to convert hex string to Phaser number color
function hexToNumber(hex: string): number {
    return parseInt(hex.replace('#', ''), 16);
}

// Helper functions for creating styled elements
export class StyledUI {
    static createGradientBackground(graphics: Phaser.GameObjects.Graphics, width: number, height: number, gradientName: 'background' | 'accent' = 'accent') {
        const gradient = Theme.gradients[gradientName];
        graphics.fillGradientStyle(
            hexToNumber(gradient.topLeft),
            hexToNumber(gradient.topRight),
            hexToNumber(gradient.bottomLeft),
            hexToNumber(gradient.bottomRight),
            1
        );
        graphics.fillRect(0, 0, width, height);
    }

    static createStyledButton(
        scene: Phaser.Scene,
        x: number,
        y: number,
        text: string,
        style: 'primary' | 'secondary' | 'danger' | 'disabled' = 'primary',
        width: number = 300,
        height: number = 60,
        onClick?: () => void
    ): Phaser.GameObjects.Container {
        const buttonStyle = Theme.button[style];
        
        const button = scene.add.rectangle(0, 0, width, height, hexToNumber(buttonStyle.color));
        button.setStrokeStyle(2, hexToNumber(Theme.colors.border));
        
        const label = scene.add.text(0, 0, text, {
            fontSize: '28px',
            fontFamily: 'Arial, sans-serif',
            color: buttonStyle.textColor,
            fontStyle: 'bold',
        });
        label.setOrigin(0.5);

        const container = scene.add.container(x, y, [button, label]);
        
        // Make button interactive
        button.setInteractive({ useHandCursor: true });

        if (style !== 'disabled') {
            button.on('pointerover', () => {
                button.setFillStyle(hexToNumber(buttonStyle.hoverColor));
                container.setScale(1.05);
            });
            button.on('pointerout', () => {
                button.setFillStyle(hexToNumber(buttonStyle.color));
                container.setScale(1);
            });
            
            if (onClick) {
                button.on('pointerdown', onClick);
            }
        }

        // Store reference for external event binding
        (container as any).button = button;
        return container;
    }

    static createCard(
        scene: Phaser.Scene,
        x: number,
        y: number,
        width: number,
        height: number
    ): Phaser.GameObjects.Graphics {
        const graphics = scene.add.graphics();
        graphics.fillStyle(hexToNumber(Theme.card.backgroundColor), Theme.card.alpha);
        graphics.fillRoundedRect(x, y, width, height, Theme.layout.borderRadius);
        graphics.lineStyle(2, hexToNumber(Theme.card.borderColor), 1);
        graphics.strokeRoundedRect(x, y, width, height, Theme.layout.borderRadius);
        return graphics;
    }
}
