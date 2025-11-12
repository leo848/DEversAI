<script lang="ts">
	import { Client } from '$lib/backend/client';
	import fineweb2 from '$lib/tokenizing/fineweb2';
	import type { ForcingResponse } from '$lib/backend/types';
	import { slide } from 'svelte/transition';
	import EmergentSpinner from '$lib/components/EmergentSpinner.svelte';
	import TokenComponent from '$lib/components/Token.svelte';
	import type { Token } from '$lib/tokenizing/token';

	const client = new Client();

	let inputText: string = $state('Es war einmal ein Kind');
	let tokens = $derived(fineweb2.tokenize(inputText));

	let styleOptions = $state({ coloringRoot: 4 });

	let data: null | ForcingResponse = $state(null);
	let old: { tokens: Token[] } = $state({ tokens: [] });

	let scratchpadTokens: Token[] = $state([]);

	let loading = $state(false);

	let tokensUpdated = $derived(
		tokens.length == old.tokens.length &&
			tokens.every((token, tokenIndex) => old.tokens[tokenIndex].id() == token.id())
	);

	async function refreshData() {
		loading = true;
		try {
			data = await client.modelForcing('causal-fw2', tokens);
			old.tokens = tokens;
			scratchpadTokens = [];
		} finally {
			loading = false;
		}
	}
</script>

<div class="m-4 flex flex-col gap-8 xl:mx-16">
	<div class="text-4xl font-bold">Forcing</div>

	<textarea bind:value={inputText}></textarea>

	<div class="w-8">
		Farbsensitivität
		<input type="range" min={0.5} max={5} step={0.1} bind:value={styleOptions.coloringRoot} />
	</div>

	<div class="w-full p-2 text-xl" transition:slide={{ axis: 'y' }}>
		<button class="rounded bg-fire-400 p-2" disabled={loading} onclick={refreshData}>
			{#if loading}
				<EmergentSpinner />
			{:else}
				Aktualisieren
			{/if}
		</button>
	</div>

	<div class="flex flex-row flex-wrap gap-y-2">
		{#each tokens as token, tokenIndex}
			{@const hueValue =
				data && tokenIndex > 0 && tokensUpdated
					? Math.exp(data.steps[tokenIndex - 1].logit) ** (1 / styleOptions.coloringRoot)
					: 0}
			<TokenComponent {token} {hueValue} />
		{/each}
	</div>

	{#if data != null}
		<div class="grid grid-cols-12">
			<div class="col-span-12 md:col-span-4">
				<div>Tokens: <b>{data.steps.length + 1}</b></div>
				<div>
					Logits:
					<b>{(data.total_logprob / (data.steps.length + 1)).toFixed(2)}</b>/Token, insg.
					<span>{data.total_logprob.toFixed(2)}</span>
				</div>
			</div>
			<div class="col-span-12 md:col-span-8">
				<div class="grid grid-cols-8 xl:grid-cols-12">
					<div class="col-span-2"><b>Token</b></div>
					<div class="col-span-1"><b>Wsk.</b></div>
					<div class="col-span-1"><b>Rang</b></div>
					<div class="col-span-4 xl:col-span-8"><b>Alternativen</b></div>
					{#each old.tokens as token, tokenIndex}
						<div class="col-span-2"><TokenComponent {token} /></div>
						{#if tokenIndex == 0}
							<div class="col-span-6 xl:col-span-10">–</div>
						{:else}
							{@const step = data.steps[tokenIndex - 1]}
							{@const altTokens = step.alternatives}
							<div class="col-span-1">
								{(Math.exp(step.logit) * 100).toFixed(2)}%
							</div>
							<div class="col-span-1">
								{step.k + 1}
							</div>
							<div class="col-span-4 flex flex-row gap-2 overflow-x-scroll xl:col-span-8">
								{#each altTokens as { token_id, logit }}
									{@const token = fineweb2.tokens[token_id]}
									<TokenComponent
										token={fineweb2.tokens[token_id]}
										onclick={() => (scratchpadTokens = [...old.tokens.slice(0, tokenIndex), token])}
										hueValue={Math.exp(logit) ** (1 / styleOptions.coloringRoot)}
									/>
								{/each}
							</div>
						{/if}
					{/each}
				</div>
			</div>
		</div>
	{/if}

	{#if scratchpadTokens.length}
		<div class="w-full">
			<textarea disabled value={scratchpadTokens.map((token) => token.toString()).join('')}
			></textarea>
		</div>
	{/if}
</div>
