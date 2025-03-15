<script lang="ts">
	import type { LogitsResponse } from '$lib/backend/types';
	import vocabulary from '$lib/tokenizing/german50000';
	import type { Token } from '$lib/tokenizing/token';
	import { sortByKey } from '$lib/util/array';
	import TokenComponent from './Token.svelte';
	import { remap } from '$lib/util/math';
	import Tooltip from './Tooltip.svelte';

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

	let topElements = $state(100);

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

	let viewType: 'table' | 'overview' = $state('overview');
</script>

<div class="max-h-[400px] overflow-scroll" {onscroll}>
	<div class="my-2 text-sm">
		Darstellung
		<select bind:value={viewType} class="text-sm">
			<option value="overview">Überblick</option>
			<option value="table">Tabelle</option>
		</select>
	</div>
	{#if viewType == 'table'}
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
	{:else if viewType == 'overview'}
		<div class="flex flex-wrap gap-y-2">
			{#each shownTokens as token, i}
				<div style:margin-right={Math.sqrt(probs[token.id()]) * 100 + 'px'}>
					<Tooltip>
						{#snippet trigger()}
							<TokenComponent
								{token}
								hueValue={remap([-5, 0], [0, 1])(Math.log(probs[token.id()]))}
								scale={Math.sqrt(probs[token.id()] * 100)}
								onclick={ontokenclick ? () => ontokenclick(token) : undefined}
							/>
						{/snippet}
						{#snippet tooltip()}
							<div class="flex flex-col gap-4">
								<div class="text-2xl font-bold">{(probs[token.id()] * 100).toFixed(2)}%</div>
								<div class="flex flex-col">
									<div>Rang #{i + 1}</div>
									<div class="whitespace-nowrap">
										Logit {logitsResponse.logits[token.id()].toFixed(3)}
									</div>
									<div class="flex flex-row gap-2 whitespace-nowrap">
										<span>Token</span>
										<TokenComponent
											size="md"
											noTransition
											{token}
											onclick={ontokenclick ? () => ontokenclick(token) : undefined}
										/>
									</div>
									<div class="whitespace-nowrap">Token-ID {token.id()}</div>
								</div>
							</div>
						{/snippet}
					</Tooltip>
				</div>
			{/each}
		</div>
	{/if}
</div>
