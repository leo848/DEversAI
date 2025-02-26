<script lang="ts">
	import type { LogitsResponse } from '$lib/backend/types';
	import vocabulary from '$lib/tokenizing/german50000';
	import type { Token } from '$lib/tokenizing/token';
	import { sortByKey } from '$lib/util/array';
	import TokenComponent from './Token.svelte';

	const {
		logitsResponse,
		ontokenclick = undefined
	}: {
		logitsResponse: LogitsResponse;
		ontokenclick?: (token: Token) => void | undefined;
	} = $props();

	const allTokens = $derived.by(() => {
		return sortByKey(vocabulary.tokens, (token) => -logitsResponse.logits[token.id()]);
	});

	let topElements = $state(20);

	const probs = $derived.by(() => {
		const maxLogit = Math.max(...logitsResponse.logits);
		const exps = logitsResponse.logits.map((logit) => Math.exp(logit - maxLogit));
		const sumExps = exps.reduce((a, b) => a + b, 0);
		return exps.map((exp) => exp / sumExps);
	});

	const shownTokens = $derived(allTokens.slice(0, topElements));

	function onscroll(evt: UIEvent) {
		const { scrollHeight, scrollTop, clientHeight } = evt.target as HTMLDivElement;
		if (Math.abs(scrollHeight - clientHeight - scrollTop) < 1) {
			topElements *= 2;
			topElements = Math.min(50256, topElements);
		}
	}
</script>

<div class="max-h-[400px] overflow-scroll" {onscroll}>
	<div class="grid grid-cols-6">
		<div class="font-bold">Rang</div>
		<div class="col-span-3 font-bold">Token</div>
		<div class="font-bold">Logit</div>
		<div class="font-bold">Wsk.</div>
		{#each shownTokens as token, i}
			<div>#{i + 1}</div>
			<div class="col-span-3">
				<TokenComponent {token} onclick={ontokenclick ? () => ontokenclick(token) : undefined} />
			</div>
			<div>{logitsResponse.logits[token.id()].toFixed(2)}</div>
			<div>{(probs[token.id()] * 100).toFixed(2)}%</div>
		{/each}
	</div>
</div>
