<script lang="ts">
	import type { Vocabulary } from '$lib/tokenizing/vocabulary';
	import { Token } from '$lib/tokenizing/token';
	import TokenComponent from '$lib/components/Token.svelte';
	import { sortByKey } from '$lib/util/array';
	import { leftPad } from '$lib/util/string';
	import { flip } from 'svelte/animate';

	const {
		vocabulary,
		pageNumber,
		tokens = null,
		href = (_) => null,
		searchable = true,
		sortable = true,
		tokensPerPage = 1000
	}: {
		vocabulary: Vocabulary;
		pageNumber: number;
		tokens?: null | Token[];
		searchable?: boolean;
		sortable?: boolean;
		href?: (page: number) => string | null;
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

	let sortKey = $state('tokenID');
	let sortDirection = $state('ascending');

	const sortKeys = {
		tokenID: (token) => token.id(),
		byteValue: (token) => [...token.value].map((v) => leftPad(v.toString(), '0', '3')).join('-'),
		byteCount: (token) => token.value.length
	};

	let tokensExist = $derived(tokens == null ? vocabulary.tokens : tokens);
	let resultingTokens = $derived(tokensExist.filter((token) => searchRegex.test(token.toString())));
	let shownTokens = $derived(
		sortByKey(resultingTokens, sortKeys[sortKey] ?? sortKeys.tokenID, {
			reverse: sortDirection == 'descending'
		}).slice((pageNumber - 1) * tokensPerPage, pageNumber * tokensPerPage)
	);

	let pageAmount = $derived(Math.ceil(resultingTokens.length / tokensPerPage));

	let pagination = $derived(
		(() => {
			const start = [1, 2];
			const context = [pageNumber - 2, pageNumber - 1, pageNumber, pageNumber + 1, pageNumber + 2];
			const end = [pageAmount, pageAmount - 1];
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

	const interestingPlaceholders = [
		'\\d{4}',
		'^[a-z]+$',
		'^[A-Z]+$',
		'[Ss]uch',
		'orsch',
		'^[0-9]+$',
		'spiel',
		'[a-z][A-Z]',
		'CDU|SPD|FDP',
		'[Dd]eutsch',
		'ismus',
		'Kategorie',
		'^20\\d\\d ?$'
	];
	let interestingPlaceholder =
		interestingPlaceholders[Math.floor(Math.random() * interestingPlaceholders.length)];
</script>

<div class="flex flex-col gap-8">
	{#if searchable}
		<div class="w-full">
			<input
				type="text"
				class="w-full rounded-xl border-4 border-gray-200 text-2xl transition-all focus:border-gray-400"
				bind:value={search}
				placeholder={`Gib einen beliebigen regulären Ausdruck ein, z.B.: ${interestingPlaceholder}`}
			/>
		</div>
		<div>
			Sortieren nach
			<select bind:value={sortKey}>
				<option value="tokenID">Token-ID</option>
				<option value="byteValue">Bytewerte</option>
				<option value="byteCount">Anzahl Bytes</option>
			</select>
			<select bind:value={sortDirection}>
				<option value="ascending">aufsteigend</option>
				<option value="descending">absteigend</option>
			</select>
		</div>
	{/if}
	{#snippet paginationRow()}
		<div class="flex flex-row justify-center gap-2">
			{#each pagination as pageLink, index (pageLink.number)}
				{#if index != 0 && pagination[index].number - pagination[index - 1].number != 1}
					{#if pagination[index].number - pagination[index - 1].number == 2}
						<a
							class="flex h-10 w-10 flex-row items-center justify-center rounded-lg border-2 border-gray-200 p-2 text-center text-xl transition-all hover:bg-gray-200"
							href={href(pageLink.number - 1)}
							class:bg-gray-200={pageLink.number - 1 == pageNumber}>{pageLink.number - 1}</a
						>
					{:else}
						<div
							class="flex h-10 w-10 flex-row items-center justify-center rounded-lg border-2 border-gray-200 p-2 text-center text-xl transition-all"
						>
							...
						</div>
					{/if}
				{/if}
				<a
					class="flex h-10 w-10 flex-row items-center justify-center rounded-lg border-2 border-gray-200 p-2 text-center text-xl transition-all hover:bg-gray-200"
					href={href(pageLink.number)}
					class:bg-gray-200={pageLink.number == pageNumber}>{pageLink.number}</a
				>
			{/each}
		</div>
	{/snippet}
	{@render paginationRow()}
	<div>
		<div class="flex flex-row flex-wrap gap-2">
			{#each shownTokens as token}
				<TokenComponent {token} />
			{/each}
		</div>
	</div>
	{@render paginationRow()}
</div>
