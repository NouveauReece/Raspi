// @ts-check
import { defineConfig } from "astro/config";
import { VitePWA } from "vite-plugin-pwa";

const isDev = process.env.NODE_ENV === 'development';

// https://astro.build/config
export default defineConfig({
	vite: {
		plugins: [
			VitePWA({
        disable: isDev,
				registerType: "autoUpdate",
				workbox: {
					cleanupOutdatedCaches: true,
					runtimeCaching: [
						{
							urlPattern: /^https:\/\/your-api\.com\/.*/i,
							handler: "CacheFirst",
							options: {
								cacheName: "dev.2026.04.26.02",
								expiration: {
									maxEntries: 50,
									maxAgeSeconds: 60 * 60 * 24, // 1 day
								},
							},
						},
					],
				},
				manifest: {
					name: "Raspi App",
					short_name: "Raspi",
					start_url: "/",
					display: "standalone",
					theme_color: "#000000",
					icons: [
						{ src: "/icon-192.png", sizes: "192x192", type: "image/png" },
						{ src: "/icon-512.png", sizes: "512x512", type: "image/png" },
					],
				},
				workbox: { navigateFallback: "/404" },
			}),
		],
	},
});
