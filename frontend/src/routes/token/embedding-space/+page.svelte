<script lang="ts">
	import { Client } from '$lib/backend/client';
	import vocabulary from '$lib/tokenizing/german50000';
	import type { Tuple } from '$lib/util/array';
	import { Gradient } from '$lib/util/color';
	import ScatterPlot3D from './ScatterPlot3D.svelte';

	const client = new Client();
	const embeddingData = $derived(client.getTokenEmbeddings('anticausal1'));

	const sampleColor = (t: number) => Gradient.Viridis.sample(t).rgb();

	const toData = (data: Tuple<3, number>[]) => {
		return data.map((pos, i) => ({
			id: i,
			position: pos,
			// color: sampleColor(1 - Math.min(10, vocabulary.tokens[i].value.length - 1) / 10)
			color: sampleColor(i / 50256)
		}));
	};
</script>

<div>
	{#await embeddingData}
		Loading data...
	{:then object}
		{@debug object}
		<ScatterPlot3D points={toData(object.embeddings3D)} initialZoom={5} />
	{:catch error}
		Fehler: {error}
	{/await}
</div>
