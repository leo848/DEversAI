<script lang="ts">
	import { BirthyearResponse } from "$lib/backend/types";
	import EmergentSpinner from '$lib/components/EmergentSpinner.svelte';
	import { Client } from '$lib/backend/client';
	import { fade } from 'svelte/transition';
	import { germanMonths } from "$lib/util/calendar";
	import Histogram from './Histogram.svelte';

	const client = new Client();

	let firstName = $state("");
	let lastName = $state("Müller");

	let inputMonth = $state("September");
	let inputDay = $state(20);

	let data: null | BirthyearResponse = $state(null);

	let loading = $state(false);

	async function refreshData() {
		loading = true;
		try {
			data = await client.getBirthyear({
				first_name: firstName,
				last_name: lastName,
				day: `${inputDay}. ${inputMonth}`,
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
		<div class="opacity-50">
			<div class="text-2xl xl:col-span-1">Tag</div>
			<input type="number" bind:value={inputDay} />
			<select bind:value={inputMonth}>
				{#each germanMonths as month}
					<option value={month}>{month}</option>
				{/each}
			</select>
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

	<div class="grid grid-cols-12 gap-8">
		<div class="col-span-6 xl:col-span-4">
			<div class="text-xl font-bold">Kenngrößen</div>
			<div class="flex flex-col gap-2">
				{#each [
					{ name: "Mittelwert μ", key: "mean", sigs: 0 },
					{ name: "Modus D₁", key: "mode", sigs: 0 },
					{ name: "Standardabweichung σ", key: "std", sigs: 1 },
					{ name: "Schiefe γₘ", key: "skew", sigs: 1 },
					] as parameter}
					{@const value = data == null ? null : data.stats[parameter.key]}
					<div class="flex bg-gray-100 border-2 border-gray-200 p-2 rounded-lg text-xl">
						<div>
							{parameter.name}
						</div>
						<div class="grow"></div>
						{#key value}
							<div class="font-bold" in:fade>
								{#if value != null}
									{value.toFixed(parameter.sigs)}
								{/if}
							</div>
						{/key}
					</div>
				{/each}
			</div>
		</div>
		<div class="col-span-12 xl:col-span-8">
			<div class="text-xl font-bold">Histogramm</div>
			{#if data != null}
				<Histogram
				 startYear={1850}
				 endYear={2010}
				 stats={data.stats}
				  data={data.decade_results}
				 />
			{/if}
		</div>
	</div>
</div>
