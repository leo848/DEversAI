<script lang="ts">
	import { goto } from '$app/navigation';
	import type { Token } from '$lib/tokenizing/token';
	import { scale } from 'svelte/transition';

	const {
		token,
		rawString = false,
		size = 'md',
		showIndex = false,
		bold = 'hover',
		noPad = false,
		noTransition = false,
		color = 'gray',
		onclick = gotoTokenPage
	}: {
		token: Token;
		rawString?: boolean;
		bold?: 'hover' | boolean;
		size?: 'md' | 'lg' | 'xl';
		showIndex?: boolean;
		noTransition?: boolean;
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
		border: { md: 'border-2', lg: 'border-2', xl: 'border-4' }[size],
		textSize: { md: '', lg: 'text-3xl', xl: 'text-6xl' }[size],
		rounding: { md: 'rounded-lg', lg: 'rounded-lg', xl: 'rounded-xl' }[size],
		padding: noPad ? '' : { md: 'p-1', lg: 'p-2', xl: 'p-4' }[size],
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
		}[color],
		bold: { hover: 'hover:font-bold', true: 'font-bold', false: 'font-normal' }['' + bold]
	});
	const classList = $derived(
		`inline-block ${style.rounding} ${style.border} ${style.borderColor} ${style.bgColor} ${style.padding} font-mono ${style.textSize} ${style.bold} transition-all`
	);
</script>

<div>
	<a
		href={`/token/${token.id()}`}
		class={classList}
		in:scale={{ duration: noTransition ? 0 : 400 }}
		onclick={(e) => {
			e.preventDefault();
			onclick(token);
		}}
	>
		<pre>{stringRepr}</pre>
	</a>
</div>
