import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

const devApiTarget = process.env.VITE_DEV_API ?? 'http://localhost:5050';

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        react(),
        VitePWA({
            registerType: 'autoUpdate',
            includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'mask-icon.svg'],
            manifest: {
                name: 'Garvey Compass',
                short_name: 'GarveyCompass',
                description: 'Source-grounded insights into organization building and Pan-African philosophy.',
                theme_color: '#05441d',
                background_color: '#fdfbf7',
                display: 'standalone',
                icons: [
                    {
                        src: 'pwa-192x192.png',
                        sizes: '192x192',
                        type: 'image/png'
                    },
                    {
                        src: 'pwa-512x512.png',
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
