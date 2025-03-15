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
			<div class="grid grid-cols-6 p-4">
				<div class="col-span-6 flex flex-col gap-2 xl:col-span-2">
					<DeversaiLogo />
					<Deployment />
				</div>
				<div class="col-span-6 md:col-span-3 xl:col-span-2">
					<a href="https://jugend-forscht.de" target="_blank">
						<img
							class="bg-black-transparent mb-4 rounded-md p-2"
							src="/1920px-Jugend_forscht.svg"
							alt="Jugend forscht logo"
						/>
					</a>
					<div class="">Ein <b>jugend forscht</b>-Projekt von Leo Blume</div>
					<div class="opacity-50">
						Copyright &copy; 2024, 2025 Leo Blume. Der Quelltext des Projekts (Frontend und Backend)
						steht unter der GNU GPL v3-Lizenz und ist damit freie Software; er kann unter den
						Bedingungen dieser Lizenz geteilt und/oder modifiziert werden.
					</div>
				</div>
			</div>
		</footer>
	</div>
</div>

<style>
	.bg-black-transparent {
		background-color: rgba(0, 0, 0, 10%);
		transition: all 0.1s;
	}
	.bg-black-transparent:hover {
		background-color: rgba(0, 0, 0, 30%);
	}
</style>
