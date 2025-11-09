<script lang="ts">
	import { BirthyearResponse } from "$lib/backend/types";
	import EmergentSpinner from '$lib/components/EmergentSpinner.svelte';
	import { Client } from '$lib/backend/client';
	import Histogram from './Histogram.svelte';

	const client = new Client();

	let firstName = $state("");
	let lastName = $state("Müller");

	let data: null | BirthyearResponse = $state(null);

	let loading = $state(false);

	async function refreshData() {
		loading = true;
		try {
			data = await client.getBirthyear({
				first_name: firstName,
				last_name: lastName,
				day: "31. Oktober",
			})
		} finally {
			loading = false;
		}
	}
</script>

<div class="m-4 flex flex-col gap-8 xl:mx-16">
	<div class="text-4xl font-bold">Geburtsjahr</div>

	<div class="grid grid-cols-3">
		<div>
			<div class="text-2xl font-bold xl:col-span-1">Vorname</div>
			<input type="text" bind:value={firstName} />
		</div>
		<div class="opacity-50">
			<div class="text-2xl xl:col-span-1">Nachname</div>
			<input type="text" bind:value={lastName} />
		</div>
	</div>

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

	{#if data != null}
		<Histogram
		 startYear={1850}
		 endYear={2010}
		 stats={data.stats}
		  data={data.decade_results}
		 />
	{/if}
</div>
