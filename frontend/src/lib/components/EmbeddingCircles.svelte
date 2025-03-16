<script lang="ts">
	import Tooltip from '$lib/components/Tooltip.svelte';
	import { Gradient } from '$lib/util/color';
	import { normalize } from '$lib/util/math';
	const { embeddingValues }: { embeddingValues: number[] } = $props();

	const embeddingValuesMax = $derived(Math.max(...embeddingValues.map(Math.abs)));

	const round = (digits: number) => {
		return (n: number) => {
			return Math.round(n * 10 ** digits) / 10 ** digits;
		};
	};

	let sensitivity = $state(round(2)(Math.log(0.2)));
</script>

<div>
	<div>
		Sensitivität Farbe: <b>{Math.exp(sensitivity).toFixed(2)}</b>
		<button
			class="ml-4 rounded bg-gray-100"
			onclick={() => (sensitivity = round(2)(Math.log(embeddingValuesMax)))}
		>
			= {embeddingValuesMax.toFixed(2)} (norm)
		</button>
	</div>
	<div>
		<input
			bind:value={sensitivity}
			class="w-full"
			type="range"
			min={round(2)(Math.log(0.01))}
			max={round(2)(Math.log(1))}
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
							normalize([Math.exp(sensitivity), -Math.exp(sensitivity)])(value)
						).toString()}
					></div>
				{/snippet}
			</Tooltip>
		{/each}
	</div>
</div>
