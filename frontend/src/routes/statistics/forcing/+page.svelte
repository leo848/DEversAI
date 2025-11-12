<script lang="ts">
	import { Client } from '$lib/backend/client';
	import fineweb2 from '$lib/tokenizing/fineweb2';
	import type { ForcingResponse } from "$lib/backend/types";
	import { slide } from 'svelte/transition';
	import EmergentSpinner from '$lib/components/EmergentSpinner.svelte';


	const client = new Client();

	let data: null | ForcingResponse = $state(null);

	let loading = $state(false);

	async function refreshData() {
		loading = true;
		try {
			data = await client.modelForcing("causal-fw2", fineweb2.tokenize("Eintausend Fragen"))
		} finally {
			loading = false;
		}
	}
</script>

<div class="m-4 flex flex-col gap-8 xl:mx-16">
	<div class="text-4xl font-bold">Forcing</div>

	<div class="w-full p-2 text-xl" transition:slide={{ axis: 'y' }}>
		<button class="rounded bg-fire-400 p-2" disabled={loading} onclick={refreshData}
		  >
		  {#if loading}
			  <EmergentSpinner />
		  {:else}
		  Aktualisieren
		  {/if}
		</button
		>
	</div>

	<code>{data}</code>
</div>
