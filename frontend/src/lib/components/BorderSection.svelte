<script lang="ts">
	import Icon from '@iconify/svelte';
	import type { Snippet } from 'svelte';
	import { slide } from 'svelte/transition';

	let {
		title,
		children,
		flex = false,
		open = $bindable(true)
	}: {
		title: string;
		children: Snippet;
		flex?: boolean;
		open?: boolean;
	} = $props();
</script>

<div class={`rounded-xl border border-2 border-gray-200 p-4 flex flex-col transition-all ${open ? "gap-4" : "gap-0"}`}>
	<button
		class="block flex flex-row items-center gap-2 text-2xl font-bold"
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
		<div transition:slide>
			{@render children()}
		</div>
	{/if}
</div>
