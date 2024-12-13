import containerQueries from '@tailwindcss/container-queries';
import forms from '@tailwindcss/forms';
import typography from '@tailwindcss/typography';
import type { Config } from 'tailwindcss';

export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],

	theme: {
		extend: {
			fontFamily: {
				"sans": ["Fira Sans", "Inter", "ui-sans", "sans", "system"],
				"mono": ["ui-monospace", "SFMono-Regular", "IosevkaTermNerdFont", "Fira Code", "monospace"]
			}
		}
	},

	plugins: [typography, forms, containerQueries]
} satisfies Config;
