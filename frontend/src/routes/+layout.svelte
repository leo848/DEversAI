<script lang="ts">
	import '../app.css';
	import NavBar from '$lib/components/NavBar.svelte';

	let { children } = $props();
</script>

<div class="flex h-full flex-row">
	<NavBar />
	<main class="mb-[10rem] grow">
		{@render children()}
	</main>
</div>
