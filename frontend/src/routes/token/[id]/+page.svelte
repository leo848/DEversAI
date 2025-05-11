<script lang="ts">
	import InverseBinaryTree from '$lib/components/InverseBinaryTree.svelte';
	import vocabulary from '$lib/tokenizing/fineweb2';
	import Icon from '@iconify/svelte';
	import { scale } from 'svelte/transition';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import TokenComponent from '$lib/components/Token.svelte';
	import BorderSection from '$lib/components/BorderSection.svelte';
	import { Client } from '$lib/backend/client';
	import { sortByKey } from '$lib/util/array';
	import TopLogits from '$lib/components/TopLogits.svelte';
	import EmergentSpinner from '$lib/components/EmergentSpinner.svelte';
	import EmbeddingCircles from '$lib/components/EmbeddingCircles.svelte';
	import TokenOccurrence from './TokenOccurrence.svelte';
	import AugmentedTokenList from '$lib/components/AugmentedTokenList.svelte';
	import type {ModelId} from '$lib/backend/models';

	const tokenIndex = $derived(+$page.params.id);
	const token = $derived(vocabulary.tokens[tokenIndex]);

	let inputTokenIndex = $state(+$page.params.id);
	$effect(() => {
		inputTokenIndex = +$page.params.id;
	});

	const client = new Client();

	const tokenData = $derived(client.getTokenInfo(token));

	const predictions = $derived({
		causal: client.modelLogits('causal-fw2', [token]),
		anticausal: client.modelLogits('anticausal-fw2', [token])
	});

	let showPercentages = $state(false);

	function setTokenIndex(newTokenIndex: number) {
		if (newTokenIndex != tokenIndex) {
			inputTokenIndex = newTokenIndex;
			goto(`/token/${newTokenIndex}`, { replaceState: false });
		}
	}
</script>

<div class="m-4 flex flex-col gap-8 xl:mx-16">
	<div class="text-4xl font-bold">Token-Visualisierung</div>
	<div class="flex flex-row justify-between">
		{#key tokenIndex}
			<TokenComponent {token} size="xl" />
		{/key}
		<div>
			{#key token}
				{#await tokenData then tokenData}
					<TokenOccurrence {tokenData} {token} />
				{/await}
			{/key}
		</div>
		<div
			class="flex flex-col content-stretch overflow-hidden rounded-xl border-4 border-gray-200 tabular-nums"
		>
			<div class="grow bg-gray-100 p-4 text-2xl" in:scale>
				{#key tokenIndex}
					<input
						class="m-0 max-w-16 border-none bg-gray-100 p-0 text-2xl focus:border-none"
						type="number"
						bind:value={inputTokenIndex}
						in:scale
						onchange={() => setTokenIndex(inputTokenIndex ?? tokenIndex)}
					/>
				{/key}
			</div>
			<div class="flex flex-row justify-stretch">
				<button
					class="flex grow flex-row justify-center bg-gray-200 transition-all hover:bg-gray-300 active:bg-gray-400 disabled:text-gray-500"
					disabled={tokenIndex == 0}
					onclick={() => setTokenIndex(tokenIndex - 1)}
				>
					<Icon icon="bxs:left-arrow" width="2rem" />
				</button>
				<button
					class="flex grow flex-row justify-center bg-gray-200 transition-all hover:bg-gray-300 active:bg-gray-400 disabled:text-gray-500"
					disabled={tokenIndex == vocabulary.tokens.length - 1}
					onclick={() => setTokenIndex(tokenIndex + 1)}
				>
					<Icon icon="bxs:right-arrow" width="2rem" />
				</button>
			</div>
		</div>
	</div>
	<BorderSection title="Stammbaum">
		<InverseBinaryTree
			onClick={(d) => setTokenIndex(d.id)}
			data={token.historyTree()}
			width={1200}
			dy={100}
		/>
	</BorderSection>
	<BorderSection title="Kinder">
		<div class="grid grid-cols-2 gap-8">
			<div class="col-span-2 flex flex-row justify-around">
				<div>
					Prozente anzeigen <input type="checkbox" bind:checked={showPercentages} />
				</div>
			</div>
			{#each ['left', 'right'] as const as key}
				<div class="flex flex-col gap-2">
					<div class="text-xl">
						{(() => ({ left: 'Links', right: 'Rechts' }))()[key]} ({token.children[key].length})
					</div>
					<div class="flex flex-row flex-wrap gap-4">
						{#each token.children[key] as child}
							{#if showPercentages}
								{#await tokenData}
									<TokenComponent token={child} />
								{:then tokenData}
									{#if tokenData.occurrences.tokens[token.id()]}
										{@const ownCount = tokenData.occurrences.tokens[token.id()].count_transitive}
										{@const childCount = tokenData.occurrences.tokens[child.id()].count_transitive}
										{@const proportion = childCount / ownCount}
										<TokenComponent token={child} {proportion} hueValue={proportion} />
									{/if}
								{/await}
							{:else}
								<TokenComponent token={child} />
							{/if}
						{/each}
					</div>
				</div>
			{/each}
		</div>
	</BorderSection>
	<BorderSection title="Beispiele" open={false} innerClass="overflow-scroll max-h-[32rem]">
		<div class="grid grid-cols-1 overflow-hidden">
			{#await tokenData}
				Beispiele werden geladen...
			{:then data}
				{#each sortByKey(data.examples, (examples) => examples
						.map((example) => example.length)
						.reduce((a, b) => a + b)) as [exampleL, exampleR]}
					<div class="group/item flex flex-row gap-2 rounded p-2 even:bg-gray-100">
						<div>
							<span>{exampleL}</span><span class="font-bold">{token.toString()}</span><span
								>{exampleR}</span
							>
						</div>
						<div class="grow"></div>
						<div
							class="h-8 w-8 rounded bg-fire-300 opacity-10 transition-all group-hover/item:opacity-100"
						>
							<a href={`/tokenize?i=${encodeURIComponent(exampleL + token.toString() + exampleR)}`}>
								<Icon icon="mdi:set-split" height="2em" />
							</a>
						</div>
					</div>
				{:else}
					<div class="text-gray-500 font-italic">(keine)</div>
				{/each}
			{:catch error}
				<div>{error}</div>
			{/await}
		</div>
	</BorderSection>
	<div class="grid grid-cols-2 gap-8">
		<div>
			<BorderSection title="Embedding" open={false}>
				<div class="flex flex-col gap-4">
					<div class="flex flex-row">
						<a class="rounded bg-gray-100 p-2" href={`/token/embedding-space?id=${tokenIndex}`}>
							Embedding-Raum
						</a>
					</div>
					<div class="grid gap-4">
						{#await tokenData}
							<EmergentSpinner />
						{:then tokenInfo}
							<BorderSection title="anticausal-fw2">
								<EmbeddingCircles embeddingValues={tokenInfo.embedding_768d.anticausal_fw2} />
							</BorderSection>
							<BorderSection title="causal-fw2">
								<EmbeddingCircles embeddingValues={tokenInfo.embedding_768d.causal_fw2} />
							</BorderSection>
						{:catch error}
							<div>{error}</div>
						{/await}
					</div>
				</div>
			</BorderSection>
		</div>
		<div class="grid gap-8">
			<BorderSection title="Ähnliche Tokens">
				<div class="grid grid-cols-2 gap-4">
					{#each ['anticausal_fw2', 'causal_fw2'] as modelId}
						<div>
							<div>{modelId}</div>
							{#await tokenData}
								<EmergentSpinner />
							{:then tokenData}
								{@const { neighbors, distances } = tokenData.nearest_neighbors[modelId] ?? { neighbors: [], distances: [] }}
								<AugmentedTokenList
									tokens={neighbors.map((id) => vocabulary.tokens[id])}
									fields={[
										{ name: 'Distanz', key: 'dist', display: 'float' },
										{ name: 'Similarity', key: 'sim', display: 'none' }
									]}
									values={neighbors.map((_, i) => ({ dist: distances[i], sim: 1 - distances[i] }))}
									hueKey="sim"
									hueMap={(x) => x ** 4}
								>
									{#snippet tooltip(token, rank)}
										<div class="flex flex-col gap-4">
											<div class="text-2xl font-bold">{distances[rank].toFixed(4)}</div>
											<div class="flex flex-col">
												<div>Rang #{rank + 1}</div>
												<div class="flex flex-row gap-2 whitespace-nowrap">
													<span>Token</span>
													<TokenComponent size="md" noTransition {token} />
												</div>
												<div class="whitespace-nowrap">Token-ID {token.id()}</div>
											</div>
										</div>
									{/snippet}
								</AugmentedTokenList>
							{:catch error}
								<div>{error}</div>
							{/await}
						</div>
					{/each}
				</div>
			</BorderSection>
			<BorderSection title="Vorhersagen">
				<div class="grid grid-cols-2 gap-4">
					<div>
						<div>anticausal-fw2</div>
						{#await predictions.anticausal}
							<EmergentSpinner />
						{:then logitsResponse}
							<TopLogits {logitsResponse} {vocabulary} />
						{:catch error}
							<div>{error}</div>
						{/await}
					</div>
					<div>
						<div>causal-fw2</div>
						{#await predictions.causal}
							<EmergentSpinner />
						{:then logitsResponse}
							<TopLogits {logitsResponse} {vocabulary} />
						{:catch error}
							<div>{error}</div>
						{/await}
					</div>
				</div>
			</BorderSection>
		</div>
	</div>
</div>
