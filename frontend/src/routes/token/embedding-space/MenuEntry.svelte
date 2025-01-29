<script lang="ts">
	import type { Snippet } from 'svelte';

	const { title, children }: { title: string; children: Snippet } = $props();
</script>

<div class="entry flex flex-col gap-4 rounded-xl border border-gray-300 p-4">
	<div class="flex flex-col items-stretch gap-2">
		<div class="text-xl">{title}</div>
		{@render children()}
	</div>
</div>

<style>
	.entry {
		background: rgba(255, 255, 255, 0.9);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
		z-index: 1000;
	}
</style>
