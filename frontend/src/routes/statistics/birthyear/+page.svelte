<script lang="ts">
	import { BirthyearResponse } from "$lib/backend/types";
	import { Client } from '$lib/backend/client';
	import Histogram from './Histogram.svelte';

	const client = new Client();

	let firstName = $state("");

	let data: null | BirthyearResponse = $state(null);

	async function refreshData() {
		data = await client.getBirthyear({
			first_name: firstName,
		})
	}
</script>

<div class="m-4 flex flex-col gap-8 xl:mx-16">
	<div class="text-4xl font-bold">Geburtsjahr</div>

	<div class="grid grid-cols-3">
		<div>
			<div class="text-2xl font-bold xl:col-span-1">Vorname</div>
			<input type="text" bind:value={firstName} />
		</div>
	</div>

	<div class="w-full p-2 text-xl" transition:slide={{ axis: 'y' }}>
		<button class="rounded bg-fire-400 p-2" onclick={refreshData}
			>Aktualisieren</button
		>
	</div>

	{#if data != null}
		<Histogram
		 startYear={1850}
		 endYear={2010}
		 stats={data.stats}
		  data={data.decade_results}
		 />
	{/if}
</div>
