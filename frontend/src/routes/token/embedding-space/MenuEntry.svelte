<script lang="ts">
	import Icon from '@iconify/svelte';
	import type { Snippet } from 'svelte';
	import { scale, slide } from 'svelte/transition';

	const { title, children }: { title: string; children: Snippet } = $props();

	let open = $state(true);
</script>

<div
	class="entry flex flex-col rounded-xl border border-gray-300 p-4"
	transition:slide={{ axis: 'y' }}
>
	<button
		class="block flex flex-row items-center gap-2 text-xl font-bold"
		class:mb-4={open}
		onclick={() => (open = !open)}
	>
		<div>
			<Icon
				icon="line-md:chevron-up"
				style={`transform: rotate(${90 + Number(open) * 90}deg)`}
				class="transition-all"
				height="1em"
			/>
		</div>
		<div>
			{title}
		</div>
	</button>
	{#if open}
		<div class="flex flex-col items-stretch gap-2" transition:slide={{ axis: 'y' }}>
			{@render children()}
		</div>
	{/if}
</div>

<style>
	.entry {
		background: rgba(255, 255, 255, 0.9);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
		z-index: 1000;
	}
</style>
