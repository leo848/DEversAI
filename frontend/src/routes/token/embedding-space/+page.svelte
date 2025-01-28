<script lang="ts">
	import { Client } from '$lib/backend/client';
	import type { Tuple } from '$lib/util/array';
	import ScatterPlot3D from './ScatterPlot3D.svelte';

	const client = new Client();
    const embeddingData = $derived(client.getTokenEmbeddings("anticausal1"))

	const toData = (data: Tuple<3, number>[]) => {
        return data.map((pos, i) => ({
          id: i,
          position: pos
        }));
	};
</script>

<div>
    {#await embeddingData}
      Loading data...
    {:then object}
      <ScatterPlot3D points={toData(object.embeddings3D)} initialZoom={5} />
    {:catch error}
      Fehler: {error}
    {/await}
</div>
