<script lang="ts">
	import '../app.css';
	import { pages } from '$lib/navigation';
	import Icon from '@iconify/svelte';

	let { children } = $props();
</script>

<div class="flex h-full flex-row">
	<nav class="transition-all duration-300 w-20 group/navbar hover:w-64">
		<div class="fancy-gradient-bg flex h-full flex-col gap-4 overflow-hidden p-2">
			{#each pages as page, index}
				{@const extern = !page.link.startsWith("/")}
				<div>
					<a href={page.link} target={extern ? "_blank": undefined} class="group/link flex flex-row gap-4">
						<div
							class="relative inline-block rounded-xl bg-white bg-opacity-50 p-2 transition-all group-hover/link:bg-opacity-100"
						>
							<Icon {...page.icon} width="3rem" />
							{#if extern}
								<div class="absolute inline-flex -top-2 -end-2 rounded-xl bg-white bg-opacity-40 group-hover/link:bg-opacity-90 w-6 h-6 justify-center align-center items-center">
									<Icon icon="iconamoon:arrow-top-right-1-bold" width="1.5rem" />
								</div>
							{/if}
						</div>
						<div class="w-full text-2xl flex flex-col text-right justify-center font-normal group-hover/link:font-bold transition-all opacity-0 group-hover/navbar:opacity-100">
							<div>{page.title}</div>
						</div>
					</a>
				</div>
				{#if index < pages.length - 1}
					<div class="h-[1px] opacity-50 w-full max-w-0 group-hover/navbar:max-w-full bg-black transition-all"></div>
				{/if}
			{/each}
		</div>
	</nav>
	<main class="grow">
		{@render children()}
	</main>
</div>

<style>
	.fancy-gradient-bg {
		background: linear-gradient(to bottom, #ffcc44 0%, #aa3300 100%);
		background-size: 4rem;
		background-repeat: false;
	}
</style>
