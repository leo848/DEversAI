<script lang="ts">
	import '../app.css';
	import NavBar from '$lib/components/NavBar.svelte';
	import DeversaiLogo from '$lib/components/DeversaiLogo.svelte';
	import Deployment from '$lib/components/Deployment.svelte';

	let { children } = $props();
</script>

<div class="flex h-full flex-row">
	<NavBar />
	<div class="grow">
		<main class="mb-[10rem] min-h-[100vh]">
			{@render children()}
		</main>
		<footer>
			<hr class="border-1 mb-3 w-full border border-gray-200" />
			<div class="flex flex-row">
				<div>
					<DeversaiLogo />
				</div>
				<div>
					<Deployment />
				</div>
			</div>
		</footer>
	</div>
</div>
