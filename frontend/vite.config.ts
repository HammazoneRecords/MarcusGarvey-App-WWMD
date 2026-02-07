import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

const devApiTarget = process.env.VITE_DEV_API ?? 'http://localhost:5050';

// https://vitejs.dev/config/
export default defineConfig({
    envDir: '..',
    plugins: [
        react(),
        VitePWA({
            registerType: 'autoUpdate',
            includeAssets: ['whirlwindkb_favicon.ico', 'Whirlwind logo12.png', 'whirlwindkb_favicon_192.png', 'whirlwindkb_favicon_512.png'],
            manifest: {
                name: 'Whirlwind KB',
                short_name: 'WhirlwindKB',
                description: 'Source-grounded knowledge base for organization building and Pan-African philosophy.',
                theme_color: '#05441d',
                background_color: '#fdfbf7',
                display: 'standalone',
                icons: [
                    {
                        src: 'whirlwindkb_favicon_192.png',
                        sizes: '192x192',
                        type: 'image/png'
                    },
                    {
                        src: 'whirlwindkb_favicon_512.png',
                        sizes: '512x512',
                        type: 'image/png'
                    }
                ]
            }
        })
    ],
    server: {
        host: '127.0.0.1',
        port: 5173,
        proxy: {
            '/api': {
                target: devApiTarget,
                changeOrigin: true,
            },
        },
    },
});
