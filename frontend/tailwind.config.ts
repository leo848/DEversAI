import containerQueries from '@tailwindcss/container-queries';
import forms from '@tailwindcss/forms';
import typography from '@tailwindcss/typography';
import type { Config } from 'tailwindcss';

export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],

	theme: {
		extend: {
			fontFamily: {
				sans: ['Fira Sans', 'Inter', 'ui-sans', 'sans', 'system'],
				mono: ['ui-monospace', 'SFMono-Regular', 'IosevkaTermNerdFont', 'Fira Code', 'monospace']
			},
			colors: {
				fire: {
					'50': '#fff8eb',
					'100': '#fff0cf',
					'200': '#ffdd9f',
					'300': '#ffc262',
					'400': '#ff9a23',
					'500': '#ff7b00',
					'600': '#ff5c00',
					'700': '#da4200',
					'800': '#aa3300',
					'900': '#8a2d04',
					'950': '#4b1300',
				},
			}
		}
	},

	plugins: [typography, forms, containerQueries]
} satisfies Config;
