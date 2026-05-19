import { UserGroupIcon, UserIcon } from '@heroicons/vue/24/solid'

export interface GameTag {
  icon: any
  text: string
}

export interface Game {
  id: number
  slug: string
  title: string
  description: string
  image: string
  tags: GameTag[]
  addedDate: string
  isPublic: boolean
  category?: string
}

export const GAMES: Game[] = [
    {
        id: 7,
        slug: 'wtz',
        title: 'Wielki Turniej Zawodowców',
        description: '50 championów walczy pozniej napisz opis kiedys',
        image: '/games/wtz/thumbnail.jpg',
        tags: [
            { icon: UserGroupIcon, text: 'Multiplayer' }
        ],
        addedDate: '2026-05-15',
        isPublic: true
    },
    {
        id: 6,
        slug: 'full-life',
        title: 'Full Life: Steal Piwo',
        description: 'Zły czarnoksiężnik RaV ukradł całe twoje zapasy piwa na majówkę! Wyrusz w pełną przygód podróż, aby odzyskać co twoje i uratować majuwe!',
        image: '/games/full-life/thumbnail.jpg',
        tags: [
        { icon: UserIcon, text: 'Singleplayer' }
        ],
        addedDate: '2026-05-10',
        isPublic: true
    },
    {
        id: 5,
        slug: 'zawomons-gt',
        title: 'Zawomons: Grand Tournament',
        description: 'Turowa gierka karciana osadzona w uniwersum zawomonsów. Zbieraj czempionów, ulepszaj zdolności, graj ze znajomymi aby zostać czempionem!',
        image: '/games/zawomons-gt/unnamed.jpg',
        tags: [
        { icon: UserGroupIcon, text: 'Multiplayer' }
        ],
        addedDate: '2025-11-04',
        isPublic: false,
        category: 'Karcianka'
    },
    {
        id: 4,
        slug: 'zawomons',
        title: 'zawomons',
        description: 'coś jak pokemony + heroes of might and magic 5 + shakes and fidget. Zbieraj, trenuj i walcz zawomonsami w turowych bitwach lokalnie i online.',
        image: '/games/zawomons/thumbnail.jpg',
        tags: [
        { icon: UserGroupIcon, text: 'Multiplayer' },
        { icon: UserIcon, text: 'Singleplayer' }
        ],
        addedDate: '2025-10-01',
        isPublic: false,
        category: 'MMORPG'
    },
    {
        id: 3,
        slug: 'ping-pong-in-space',
        title: 'Ping Pong in SPACE!',
        description: 'Prosta gra typu pong z kosmiczną atmosferą. Sterowanie: strzałki góra/dół lub W/S.',
        image: '/games/ping-pong-in-space/thumbnail.jpg',
        tags: [
        { icon: UserGroupIcon, text: 'Multiplayer' }
        ],
        addedDate: '2025-09-23',
        isPublic: true,
        category: 'Arcade'
    },
    {
        id: 2,
        slug: 'the-last-raccoon',
        title: 'The Last Raccoon',
        description: 'Ostatni ocalały szop w świecie pozbawionym brudu. Obroń elektryczny samochód jego wybawiciela, stawiaj wieżyczki i pilnuj by nie padły z głodu na brak prądu. Tower defense w brudnym klimacie zbyt czystych miast.',
        image: '/games/the-last-raccoon/thumbnail.jpg',
        tags: [
        { icon: UserIcon, text: 'Singleplayer' }
        ],
        addedDate: '2025-09-06',
        isPublic: true,
        category: 'Tower Defense'
    },
    {
        id: 1,
        slug: 'cleaning-time',
        title: 'Cleaning Time!',
        description: 'Gra zręcznościowa opowiadająca historię energicznego przedszkolaka, który ma ambicję posprzątać wszystkie zabawki w całym przedszkolu (sam), podczas gdy jego koledzy i koleżanki toczą własne boje w poszukiwaniu swych utraconych chromosomów.',
        image: '/games/cleaning-time/thumbnail.jpg',
        tags: [
        { icon: UserIcon, text: 'Singleplayer' }
        ],
        addedDate: '2025-09-03',
        isPublic: true,
        category: 'Zręcznościowa'
    }
]

// Funkcje pomocnicze
export function getGameBySlug(slug: string): Game | undefined {
  return GAMES.find(game => game.slug === slug)
}

export function getGameSlugs(): string[] {
  return GAMES.map(game => game.slug)
}

export function gameExists(slug: string): boolean {
  return GAMES.some(game => game.slug === slug)
}

export function getVisibleGame(slug: string, isAdmin: boolean): Game | undefined {
  const game = getGameBySlug(slug)
  if (!game) return undefined
  if (game.isPublic || isAdmin) return game
  return undefined
}

export function getVisibleGames(isAdmin: boolean): Game[] {
  return isAdmin ? GAMES : GAMES.filter(game => game.isPublic)
}