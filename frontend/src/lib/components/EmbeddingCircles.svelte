<script lang="ts">
	import Tooltip from '$lib/components/Tooltip.svelte';
	import { Gradient } from '$lib/util/color';
	import { normalize } from '$lib/util/math';
	const { embeddingValues }: { embeddingValues: number[] } = $props();

	let sensitivity = $state(Math.round(Math.log(0.2)));
</script>

<div>
	<div>Sensitivität Farbe: <b>{Math.exp(sensitivity).toFixed(2)}</b></div>
	<div>
		<input
			bind:value={sensitivity}
			class="w-full"
			type="range"
			min={Math.floor(Math.log(0.01))}
			max={Math.floor(Math.log(1))}
			step={0.001}
		/>
	</div>
	<div class="grid grid-cols-[repeat(32,minmax(0,1fr))] gap-1">
		{#each embeddingValues as value, dimension}
			<Tooltip>
				{#snippet tooltip()}
					<div class="flex flex-col">
						<div class="whitespace-nowrap">Dim. {dimension}</div>
						<div class="text-2xl font-bold">{value.toFixed(3)}</div>
					</div>
				{/snippet}
				{#snippet trigger()}
					<div
						class="h-4 w-4 rounded-xl text-center"
						style:background-color={Gradient.Vlag.sample(
							normalize([-Math.exp(sensitivity), Math.exp(sensitivity)])(value)
						).toString()}
					></div>
				{/snippet}
			</Tooltip>
		{/each}
	</div>
</div>
