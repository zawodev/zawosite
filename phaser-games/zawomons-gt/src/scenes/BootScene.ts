import Phaser from 'phaser';

export default class BootScene extends Phaser.Scene {
    constructor() {
        super({ key: 'BootScene' });
    }

    preload() {
        // Load assets here if needed
    }

    create() {
        // Wait for auth token to arrive, or timeout after 5 seconds
        console.log('⏳ BootScene: Waiting for auth token...');
        
        // Check if token already exists
        if ((window as any).authToken) {
            console.log('✅ Token already available');
            this.getUsernameAndStart();
        } else {
            // Listen for token event
            let tokenReceived = false;
            
            const handleToken = () => {
                if (!tokenReceived) {
                    tokenReceived = true;
                    console.log('✅ Token event received');
                    this.getUsernameAndStart();
                }
            };

            // Listen for token via Phaser game events
            if ((window as any).phaserGame) {
                (window as any).phaserGame.events.once('authTokenReceived', handleToken);
            }

            // Fallback timeout - start anyway after 3 seconds
            this.time.delayedCall(3000, () => {
                if (!tokenReceived) {
                    console.log('⏰ Token timeout - starting without auth');
                    tokenReceived = true;
                    if ((window as any).phaserGame) {
                        (window as any).phaserGame.events.off('authTokenReceived', handleToken);
                    }
                    this.getUsernameAndStart();
                }
            });
        }
    }

    async getUsernameAndStart() {
        const authToken = (window as any).authToken || '';
        let username = '';
        let avatar = '';

        console.log('🎮 BootScene: Checking auth token...', authToken ? `Token present (${authToken.length} chars)` : '❌ No token');

        if (authToken) {
            // Try to fetch user data
            try {
                console.log('📡 Fetching user data from API...');
                const response = await fetch('http://localhost:8000/api/v1/users/me/', {
                    headers: {
                        'Authorization': `Bearer ${authToken}`,
                    },
                });

                console.log('📡 API Response status:', response.status);

                if (response.ok) {
                    const userData = await response.json();
                    console.log('✅ User data received:', userData);
                    username = userData.username;
                    (window as any).username = username;
                    avatar = userData.avatar || '';
                    if (avatar) (window as any).avatar = avatar;
                } else {
                    const errorText = await response.text();
                    console.error('❌ API Error:', response.status, errorText);
                }
            } catch (error) {
                console.error('❌ Failed to fetch user data:', error);
            }
        }

        // If no username, generate guest username silently
        if (!username) {
            username = 'Guest' + (Math.floor(Math.random() * 9000) + 1000);
            (window as any).username = username;
            console.log('👤 Generated guest username:', username);
        } else {
            console.log('👤 Logged in as:', username);
        }

        // Store in registry
        this.registry.set('username', username);
        try {
            if (typeof (window as any).updatePlayerInfo === 'function') {
                (window as any).updatePlayerInfo();
            }
        } catch (e) {}

        // Start lobby list by default
        this.scene.start('LobbyListScene');
    }
}
