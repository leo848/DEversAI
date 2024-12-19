<script lang="ts">
	import InverseBinaryTree from '$lib/components/InverseBinaryTree.svelte';
	import vocabulary from '$lib/tokenizing/german50000';
	import Icon from '@iconify/svelte';
	import { scale } from 'svelte/transition';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import Token from '$lib/components/Token.svelte';
	import BorderSection from '$lib/components/BorderSection.svelte';

	const tokenIndex = $derived(+$page.params.id);
	const token = $derived(vocabulary.tokens[tokenIndex]);

	function setTokenIndex(newTokenIndex: number) {
		if (newTokenIndex != tokenIndex) {
			goto(`/token/${newTokenIndex}`, { replaceState: false });
		}
	}
</script>

<div class="m-4 flex flex-col gap-8 xl:mx-16">
	<div class="text-4xl font-bold">Token-Visualisierung</div>
	<div class="flex flex-row justify-between">
		{#key tokenIndex}
			<Token {token} size="xl" />
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
			{#each ['left', 'right'] as const as key}
				<div class="flex flex-col gap-2">
					<div class="text-xl">
						{(() => ({ left: 'Links', right: 'Rechts' }))()[key]} ({token.children[key].length})
					</div>
					<div class="flex flex-row flex-wrap gap-4">
						{#each token.children[key] as child}
							<Token token={child} />
						{/each}
					</div>
				</div>
			{/each}
		</div>
	</BorderSection>
</div>
