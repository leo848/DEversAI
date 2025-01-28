<script lang="ts">
	import { Client } from '$lib/backend/client';
	import vocabulary from '$lib/tokenizing/german50000';
	import type { Tuple } from '$lib/util/array';
	import { Color, Gradient } from '$lib/util/color';
	import ScatterPlot3D from './ScatterPlot3D.svelte';

	const client = new Client();
	const embeddingData = $derived(client.getTokenEmbeddings('anticausal1'));

	const sampleColor = (t: number) => Gradient.Viridis.sample(t).rgb();

	let paintSelection: string = $state('Suffix');

	const toData = (data: Tuple<3, number>[]) => {
		return data.map((pos, i) => {
			return {
				id: i,
				position: pos
				// color: sampleColor(1 - Math.min(10, vocabulary.tokens[i].value.length - 1) / 10)
				// color: sampleColor(i / 50256)
			};
		});
	};

	function paintCategorical(categoryIndex: number): Color {
		const color = categoryIndex == -1 ? Color.luma(1.0) : Color.Category10[categoryIndex];
		return color;
	}

	function paintPrefix(i: number): Color {
		const bytes = vocabulary.tokens[i].value;

		// const commonPrefixes = [101, 97, 115, 83, 65, 103, 105, 98, 66, 100];
		const interestingPrefixes = [10, 46, 45, 40, 58, 44, 32, 41, 63, 33];

		const categoryIndex = interestingPrefixes.findIndex((byte) => bytes[0] == byte);
		return paintCategorical(categoryIndex);
	}

	function paintSuffix(i: number): Color {
		const bytes = vocabulary.tokens[i].value;

		// const commonSuffixes = [32, 114, 110, 116, 108, 115, 10, 104, 101, 103];
		const interestingSuffixes = [32, 10, 45, 46, 47, 40, 44, 58, 95, 34];

		const categoryIndex = interestingSuffixes.findIndex((byte) => bytes[bytes.length - 1] == byte);

		return paintCategorical(categoryIndex);
	}

	const tokenColor = $derived(
		{
			Suffix: paintSuffix,
			Präfix: paintPrefix
		}[paintSelection] ?? (() => paintCategorical(-1))
	);
</script>

<div>
	{#await embeddingData}
		Loading data...
	{:then object}
		<ScatterPlot3D points={toData(object.embeddings3D)} coloring={tokenColor} initialZoom={5} />
	{:catch error}
		Fehler: {error}
	{/await}
	<div class="selection absolute m-4 w-[300px] rounded-xl border border-black p-4">
		<select bind:value={paintSelection}>
			<option value="Suffix">Suffix</option>
			<option value="Präfix">Präfix</option>
		</select>
	</div>
</div>

<style>
	.selection {
		background: rgba(255, 255, 255, 0.9);
		border: 1px solid #ddd;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
		z-index: 1000;
	}
</style>
