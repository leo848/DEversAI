<script lang="ts">
	import type { Snippet } from 'svelte';
	import { slide } from 'svelte/transition';

	const { title, children }: { title: string; children: Snippet } = $props();

	let open = $state(true);
</script>

<div class="entry flex flex-col gap-4 rounded-xl border border-gray-300 p-4">
	<button class="block text-xl" onclick={() => (open = !open)}>{title}</button>
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
