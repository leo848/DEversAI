<script lang="ts">
	import Tooltip from '$lib/components/Tooltip.svelte';
	import { scale } from 'svelte/transition';
	import type { TokenInfo } from '$lib/backend/types';
	import type { Token } from '$lib/tokenizing/token';

	const {
		tokenData,
		token
	}: {
		tokenData: TokenInfo;
		token: Token;
	} = $props();
</script>

<div
	transition:scale
	class="flex h-full flex-col rounded-xl border border-4 border-gray-200 bg-gray-100 p-4"
>
	{#each ['count_direct', 'count_transitive'] as const as key}
		{@const contained = !!tokenData.occurrences.tokens[token.id()]}
		{#if contained}
			{@const freq = tokenData.occurrences.tokens[token.id()][key] / tokenData.occurrences.total}
			{@const [base, exp] = freq.toExponential().split('e-').map(Number)}
			<Tooltip>
				{#snippet trigger()}
					<div class:font-bold={key == 'count_direct'} class="text-2xl">
						{base.toFixed(2)} × 10<sup>-{exp}</sup>
					</div>
				{/snippet}
				{#snippet tooltip()}
					<div>
						{#if key == 'count_direct'}
							<div class="text-2xl">Direktes Vorkommen</div>
							<p class="text-md">
								Wie oft kommt das Token im Korpus vor? Die angegebene Zahl beschreibt den Anteil an
								allen Tokens.
							</p>
						{:else if key == 'count_transitive'}
							<div class="text-2xl">Transitives Vorkommen</div>
							<p class="text-md">Wie oft kommt das Token oder eines seiner Kinder im Korpus vor?</p>
						{/if}
					</div>
				{/snippet}
			</Tooltip>
		{/if}
	{/each}
</div>
