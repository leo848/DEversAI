import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

declare let process: {
	env: {
		VERCEL: 1 | undefined;
		VERCEL_GIT_COMMIT_SHA: string | undefined;
		VERCEL_GIT_COMMIT_MESSAGE: string | undefined;
	};
};

export default defineConfig({
	plugins: [sveltekit()],
	define: {
		'process.env': process.env
	},
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}']
	}
});
