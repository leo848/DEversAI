<script lang="ts">
	import Icon from '@iconify/svelte';

	const {
		onclick,
		causality,
		disabled = false
	}: {
		causality: 'causal' | 'anticausal';
		onclick: () => void;
		disabled?: boolean;
	} = $props();
</script>

<div>
	<button
		class="align-center flex w-full flex-row items-center justify-between rounded-xl border border-2 border-gray-200 p-4 text-xl font-bold transition-all hover:bg-gray-100 disabled:opacity-50"
		{onclick}
		{disabled}
	>
		<div>
			<Icon
				icon={`line-md:arrow-${{ causal: 'down', anticausal: 'up' }[causality]}`}
				height="2em"
			/>
		</div>
		<div>
			{#if causality == 'causal'}
				Kausale Vorhersage
			{:else if causality == 'anticausal'}
				Antikausale Vorhersage
			{/if}
		</div>
		<div></div>
	</button>
</div>
