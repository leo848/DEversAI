<script lang="ts">
	import { goto } from '$app/navigation';
	import type { Token } from '$lib/tokenizing/token';
	import { scale } from 'svelte/transition';

	const {
		token,
		rawString = false,
		size = 'md',
		showIndex = false,
		onclick = gotoTokenPage
	}: {
		token: Token;
		rawString?: boolean;
		size?: 'md' | 'xl';
		showIndex?: boolean;
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
		padding: { md: 'p-1', xl: 'p-4' }[size]
	});
	const classList = $derived(
		`inline-block ${style.rounding} ${style.border} border-gray-200 bg-gray-100 ${style.padding} font-mono ${style.textSize}`
	);
</script>

<div>
	<button class={classList} in:scale onclick={() => onclick(token)}>
		{stringRepr}
	</button>
</div>
