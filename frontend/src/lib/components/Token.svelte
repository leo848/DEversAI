<script lang="ts">
	import { goto } from '$app/navigation';
	import type { Token } from '$lib/tokenizing/token';
	import { scale } from 'svelte/transition';

	const {
		token,
		rawString = false,
		size = 'md',
		showIndex = false,
		noPad = false,
		color = 'gray',
		onclick = gotoTokenPage
	}: {
		token: Token;
		rawString?: boolean;
		size?: 'md' | 'xl';
		showIndex?: boolean;
		noPad?: boolean;
		color?:
			| 'gray'
			| 'blue'
			| 'orange'
			| 'purple'
			| 'pastelBlue'
			| 'pastelPink'
			| 'pastelGreen'
			| 'pastelYellow';
		onclick?: (token: Token) => void;
	} = $props();

	function gotoTokenPage(token: Token) {
		goto(`/token/${token.id()}`);
	}

	const stringRepr = $derived(rawString ? token.toString() : token.toStringDebug());

	const style = $derived({
		border: { md: 'border-2', xl: 'border-4' }[size],
		textSize: { md: '', xl: 'text-6xl' }[size],
		rounding: { md: 'rounded-lg', xl: 'rounded-xl' }[size],
		padding: noPad ? '' : { md: 'p-1', xl: 'p-4' }[size],
		bgColor: {
			gray: 'bg-gray-100',
			blue: 'bg-blue-200',
			orange: 'bg-orange-200',
			purple: 'bg-purple-200',
			pastelBlue: 'bg-[#a8d5e2]',
			pastelGreen: 'bg-[#b2e2b4]',
			pastelPink: 'bg-[#f8bfd5]',
			pastelYellow: 'bg-[#fbe7a1]'
		}[color],
		borderColor: {
			gray: 'border-gray-200',
			blue: 'border-blue-300',
			orange: 'border-orange-300',
			purple: 'border-purple-300',
			pastelBlue: 'border-[#88b5c2]',
			pastelGreen: 'border-[#92c294]',
			pastelPink: 'border-[#c89fb5]',
			pastelYellow: 'border-[#cbb781]'
		}[color]
	});
	const classList = $derived(
		`inline-block ${style.rounding} ${style.border} ${style.borderColor} ${style.bgColor} ${style.padding} font-mono ${style.textSize} hover:font-bold transition-all`
	);
</script>

<div>
	<button class={classList} in:scale onclick={() => onclick(token)}>
		<pre>{stringRepr}</pre>
	</button>
</div>
