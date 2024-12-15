<script lang="ts">
	import InverseBinaryTree from '$lib/components/InverseBinaryTree.svelte';
	import vocabulary from '$lib/tokenizing/preVocabulary';
	import Icon from '@iconify/svelte';
	import { scale } from 'svelte/transition';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	let tokenIndex = $state(
		+$page.params.id ?? Math.floor(Math.random() * vocabulary.tokens.length)
	);
	const token = $derived(vocabulary.tokens[tokenIndex]);

	let effectFlag = false;

	function setTokenIndex(newTokenIndex: number) {
		if (newTokenIndex != tokenIndex) {
			effectFlag = true;
			tokenIndex = newTokenIndex;
			goto(`/token/${newTokenIndex}`, { replaceState: false }).then(() => (effectFlag = false));
		}
	}

	$effect(() => {
		if (+$page.params.id != tokenIndex && !effectFlag) {
			goto(`/token/${tokenIndex}`, { replaceState: false }).then(() => {
				tokenIndex = +$page.params.id;
			});
		}
	});
</script>

<div class="m-4 xl:mx-16">
	<div class="my-8 text-4xl font-bold">Token-Visualisierung</div>
	<div class="flex flex-row justify-between">
		{#key tokenIndex}
			<div class="rounded-xl border-4 border-gray-200 bg-gray-100 p-4 font-mono text-6xl" in:scale>
				{token.toStringDebug()}
			</div>
		{/key}
		<div
			class="flex flex-col content-stretch overflow-hidden rounded-xl border-4 border-gray-200 tabular-nums"
		>
			<div class="grow bg-gray-100 p-4 text-2xl" in:scale>
				{#key tokenIndex}
					<input
						class="m-0 max-w-16 border-none bg-gray-100 p-0 text-2xl focus:border-none"
						type="number"
						value={token.id()}
						in:scale
						onblur={(e) => setTokenIndex(+e.target!.value ?? tokenIndex)}
					/>
				{/key}
			</div>
			<div class="flex flex-row justify-stretch">
				<button
					class="flex grow flex-row justify-center bg-gray-200 transition-all hover:bg-gray-300 active:bg-gray-400"
					onclick={() => setTokenIndex(tokenIndex - 1)}
				>
					<Icon icon="bxs:left-arrow" width="2rem" />
				</button>
				<button
					class="flex grow flex-row justify-center bg-gray-200 transition-all hover:bg-gray-300 active:bg-gray-400"
					onclick={() => setTokenIndex(tokenIndex + 1)}
				>
					<Icon icon="bxs:right-arrow" width="2rem" />
				</button>
			</div>
		</div>
	</div>
	<InverseBinaryTree
		onClick={(d) => setTokenIndex(d.id)}
		data={token.historyTree()}
		width={1200}
		dy={100}
	/>
</div>
