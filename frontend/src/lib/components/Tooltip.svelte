<script lang="ts">
	import type { Snippet } from 'svelte';
	import { scale } from 'svelte/transition';

	let {
		trigger,
		tooltip,
		outerClass = ''
	}: {
		trigger: Snippet;
		tooltip: Snippet;
		outerClass?: string;
	} = $props();

	let open = $state(false);
</script>

<div
	class={`relative ${outerClass}`}
	onmousemove={() => (open = true)}
	onfocus={() => (open = true)}
	onmouseout={() => (open = false)}
	onblur={() => (open = false)}
	role="tooltip"
>
	{@render trigger()}
	{#if open}
		<div
			class="absolute z-50 rounded border border-2 border-gray-200 bg-white p-4"
			transition:scale
		>
			{@render tooltip()}
		</div>
	{/if}
</div>
