<script lang="ts">
	import type { LogitsResponse } from '$lib/backend/types';
	import vocabulary from '$lib/tokenizing/german50000';
	import type { Token } from '$lib/tokenizing/token';
	import { sortByKey } from '$lib/util/array';
	import TokenComponent from './Token.svelte';
	import AugmentedTokenList from './AugmentedTokenList.svelte';

	const {
		logitsResponse,
		temperature = 1.0,
		topK = 50256,
		ontokenclick = undefined
	}: {
		logitsResponse: LogitsResponse;
		temperature?: number;
		topK?: number;
		ontokenclick?: (token: Token) => void;
	} = $props();

	const allTokens = $derived.by(() => {
		return sortByKey(vocabulary.tokens, (token) => -logitsResponse.logits[token.id()]);
	});

	let topElements = $state(100);

	const logits = $derived.by(() => {
		return [...logitsResponse.logits]
			.map((logit) => logit / temperature)
			.map((logit, i) => [logit, i])
			.toSorted(([l1, _i1], [l2, _i2]) => l2 - l1)
			.map(([logit, i], currentI) => [currentI > topK ? -Infinity : logit, i])
			.toSorted(([_l1, i1], [_l2, i2]) => i1 - i2)
			.map(([logit, _i]) => logit);
	});
	const probs = $derived.by(() => {
		const maxLogit = Math.max(...logits);
		const exps = logits.map((logit) => Math.exp(logit - maxLogit));
		const sumExps = exps.reduce((a, b) => a + b, 0);
		return exps.map((exp) => exp / sumExps);
	});

	const shownTokens = $derived(allTokens.slice(0, Math.min(topK + 1, topElements)));

	function onscroll(evt: UIEvent) {
		const { scrollHeight, scrollTop, clientHeight } = evt.target as HTMLDivElement;
		if (Math.abs(scrollHeight - clientHeight - scrollTop) < 1 && topElements < topK) {
			topElements *= 2;
			topElements = Math.min(50256, topElements);
		}
	}
</script>

<AugmentedTokenList
	tokens={shownTokens}
	fields={[
		{ key: 'logit', name: 'Logit', display: 'float' },
		{ key: 'prob', name: 'Wsk.', display: 'perc' }
	]}
	values={shownTokens.map((token, _i) => {
		return { logit: logitsResponse.logits[token.id()], prob: probs[token.id()] };
	})}
	hueKey="prob"
	{onscroll}
	{ontokenclick}
>
	{#snippet tooltip(token: Token, rank: number)}
		<div class="flex flex-col gap-4">
			<div class="text-2xl font-bold">{(probs[token.id()] * 100).toFixed(2)}%</div>
			<div class="flex flex-col">
				<div>Rang #{rank + 1}</div>
				<div class="whitespace-nowrap">
					Logit {logitsResponse.logits[token.id()].toFixed(3)}
					({logits[token.id()].toFixed(3)})
				</div>
				<div class="flex flex-row gap-2 whitespace-nowrap">
					<span>Token</span>
					<TokenComponent size="md" noTransition {token} />
				</div>
				<div class="whitespace-nowrap">Token-ID {token.id()}</div>
			</div>
		</div>
	{/snippet}
</AugmentedTokenList>
