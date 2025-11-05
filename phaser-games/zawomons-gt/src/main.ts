import Phaser from 'phaser';
import TitleScene from './scenes/TitleScene';
import LobbyListScene from './scenes/LobbyListScene';
import CreateLobbyScene from './scenes/CreateLobbyScene';
import JoinLobbyScene from './scenes/JoinLobbyScene';
import LobbyScene from './scenes/LobbyScene';

const config: Phaser.Types.Core.GameConfig = {
    type: Phaser.AUTO,
    width: 1920,
    height: 1080,
    parent: 'game',
    backgroundColor: '#2d2d2d',
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH,
    },
    dom: {
        createContainer: true,
    },
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 0, x: 0 },
            debug: false,
        },
    },
    scene: [TitleScene, LobbyListScene, CreateLobbyScene, JoinLobbyScene, LobbyScene],
};

const game = new Phaser.Game(config);

(window as any).phaserGame = game;

window.addEventListener('resize', () => {
    game.scale.refresh();
});
