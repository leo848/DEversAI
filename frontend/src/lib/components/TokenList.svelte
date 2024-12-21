<script lang="ts">
	import { page } from '$app/stores';
	import type { Vocabulary } from '$lib/tokenizing/vocabulary';
	import { Token } from '$lib/tokenizing/token';
	import TokenComponent from '$lib/components/Token.svelte';

	const {
		vocabulary,
		tokens = null,
		searchable = true,
		sortable = true,
		tokensPerPage = 1000
	}: {
		vocabulary: Vocabulary;
		tokens?: null | Token[];
		searchable?: boolean;
		sortable?: boolean;
		tokensPerPage?: number;
	} = $props();

	let search = $state('');
	let searchRegex = $derived(
		(() => {
			try {
				return new RegExp(search);
			} catch {
				return new RegExp('');
			}
		})()
	);

	let tokensExist = $derived(tokens == null ? vocabulary.tokens : tokens);
	let resultingTokens = $derived(tokensExist.filter((token) => searchRegex.test(token.toString())));
	let shownTokens = $derived(
		resultingTokens.slice((pageNumber - 1) * tokensPerPage, pageNumber * tokensPerPage)
	);

	const pageNumber = $derived(Number($page.url.searchParams.get('p') ?? 2));
	let pageAmount = $derived(Math.ceil(resultingTokens.length / tokensPerPage));

	let pagination = $derived(
		(() => {
			const start = [1, 2, 3];
			const context = [pageNumber - 1, pageNumber, pageNumber + 1];
			const end = [pageAmount, pageAmount - 1, pageAmount - 2];
			const array = [...start, ...context, ...end].filter((elem) => elem > 0 && elem <= pageAmount);
			array.sort((a, b) => a - b);
			const unique = [...new Set(array)].map((index) => ({
				number: index
			}));
			if (unique.length !== 1) {
				return unique;
			} else return [];
		})()
	);
</script>

<div class="flex flex-col gap-8">
	{#if searchable}
		<div class="w-full">
			<input
				type="text"
				class="w-full rounded-xl border-4 border-gray-200 text-2xl transition-all focus:border-gray-400"
				bind:value={search}
			/>
		</div>
	{/if}
	<div class="flex flex-row justify-center gap-2">
		{#each pagination as pageLink}
			<a
				class="w-10 rounded-lg border-2 border-gray-200 p-2 text-center text-xl transition-all hover:bg-gray-200"
				href={`/tokens/list?p=${pageLink.number}`}
				class:bg-gray-200={pageLink.number == pageNumber}>{pageLink.number}</a
			>
		{/each}
	</div>
	<div>
		<div class="flex flex-row flex-wrap gap-2">
			{#each shownTokens as token}
				<TokenComponent {token} />
			{/each}
		</div>
	</div>
	<div class="flex flex-row justify-center gap-2">
		{#each pagination as pageLink}
			<a
				class="w-10 rounded-lg border-2 border-gray-200 p-2 text-center text-xl transition-all hover:bg-gray-200"
				href={`/tokens/list?p=${pageLink.number}`}
				class:bg-gray-200={pageLink.number == pageNumber}>{pageLink.number}</a
			>
		{/each}
	</div>
</div>
