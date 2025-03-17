<script lang="ts">
	import type { Token } from '$lib/tokenizing/token';
	import { remap } from '$lib/util/math';
	import type { Snippet } from 'svelte';
	import TokenComponent from './Token.svelte';
	import Tooltip from './Tooltip.svelte';

	const {
		tokens,
		fields,
		values,
		hueKey,
		tooltip,
		hueMap = (x: number) => x,
		hueRange = [0, 1],
		onscroll = () => {},
		ontokenclick = undefined
	}: {
		tokens: Token[];
		fields: { name: string; key: string; display: 'float' | 'perc' | 'none' }[];
		hueKey: string;
		values: Record<string, number>[];
		tooltip: Snippet<[Token, number]>;
		hueMap?: (input: number) => number;
		hueRange?: [number, number];
		onscroll?: (evt: UIEvent) => void;
		ontokenclick?: (token: Token) => void;
	} = $props();

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
		{@const colCount = fields.filter((field) => field.display != 'none').length + 3 + 1}
		{@const gridColsClass = { 5: 'grid-cols-5', 6: 'grid-cols-6' }[colCount]}
		{@debug fields}
		<div class={`grid ${gridColsClass}`}>
			<div class="font-bold">Rang</div>
			<div class="col-span-3 font-bold">Token</div>
			{#each fields as field}
				{#if field.display != 'none'}
					<div class="font-bold">{field.name}</div>
				{/if}
			{/each}
			{#each tokens as token, tokenIndex}
				<div>#{tokenIndex + 1}</div>
				<div class="col-span-3">
					<TokenComponent {token} onclick={ontokenclick ? () => ontokenclick(token) : undefined} />
				</div>
				{#each fields as field}
					{@const value = values[tokenIndex][field.key]}
					{#if field.display == 'float'}
						<div>{value.toFixed(2)}</div>
					{:else if field.display == 'perc'}
						<div>{(value * 100).toFixed(2)}%</div>
					{/if}
				{/each}
			{/each}
		</div>
	{:else if viewType == 'overview'}
		<div class="flex flex-wrap gap-y-2">
			{#each tokens as token, tokenIndex}
				{@const hueNormalized = hueMap(remap(hueRange, [0, 1])(values[tokenIndex][hueKey]))}
				<div
					style:margin-right={Math.sqrt(hueNormalized) * 100 + 'px'}
					style:margin-bottom={tokenIndex == tokens.length - 1 ? '50%' : undefined}
				>
					{#snippet outerTooltip()}
						{@render tooltip(token, tokenIndex)}
					{/snippet}
					<Tooltip tooltip={outerTooltip}>
						{#snippet trigger()}
							<TokenComponent
								{token}
								hueValue={remap([-5, 0], [0, 1])(Math.log(hueNormalized))}
								scale={Math.sqrt(hueNormalized * 100)}
								onclick={ontokenclick ? () => ontokenclick(token) : undefined}
							/>
						{/snippet}
					</Tooltip>
				</div>
			{/each}
		</div>
	{/if}
</div>
