// @ts-check
import { defineConfig } from 'astro/config'
import AstroPWA from '@vite-pwa/astro'

// https://astro.build/config
export default defineConfig({
  integrations: [
  AstroPWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Raspi App',
        short_name: 'Raspi',
        start_url: '/',
        display: 'standalone',
        theme_color: '#000000',
        icons: [
          { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icon-512.png', sizes: '512x512', type: 'image/png' }
        ]
      },
      workbox: { navigateFallback: '/404' }
    })
  ]
})