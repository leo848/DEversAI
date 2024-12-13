<script lang="ts">
	import '../app.css';
	import { pages } from '$lib/navigation';
	import Icon from "@iconify/svelte";

	let { children } = $props();
</script>

<div class="flex flex-row">
	<nav class="flex flex-col fancy-gradient-bg gap-4 p-2">
		{#each pages as page}
			<div>
				<button class="bg-white bg-opacity-50 hover:bg-opacity-100 rounded-xl p-2 transition">
					<Icon {...page.icon} width="50px" />
				</button>
			</div>
		{/each}
	</nav>
	<main class="grow">
		{@render children()}
	</main>
</div>

<style>
	.fancy-gradient-bg {
		background: linear-gradient(to bottom, #ffcc44 0%, #aa3300 100%)
	}
</style>
