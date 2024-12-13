<script lang="ts">
	import '../app.css';
	import { pages } from '$lib/navigation';
	import Icon from '@iconify/svelte';

	let { children } = $props();
</script>

<div class="flex h-full flex-row">
	<nav class="group/navbar w-20 transition-all duration-300 hover:w-64">
		<div class="fancy-gradient-bg flex h-full flex-col gap-4 overflow-hidden p-2">
			{#each pages as page, index}
				{@const extern = !page.link.startsWith('/')}
				<div>
					<a
						href={page.link}
						target={extern ? '_blank' : undefined}
						class="group/link flex flex-row gap-4"
					>
						<div
							class="relative inline-block rounded-xl bg-white bg-opacity-50 p-2 transition-all group-hover/link:bg-opacity-100"
						>
							<Icon {...page.icon} width="3rem" />
							{#if extern}
								<div
									class="align-center absolute -end-2 -top-2 inline-flex h-6 w-6 items-center justify-center rounded-xl bg-white bg-opacity-40 group-hover/link:bg-opacity-90"
								>
									<Icon icon="iconamoon:arrow-top-right-1-bold" width="1.5rem" />
								</div>
							{/if}
						</div>
						<div
							class="flex w-full flex-col justify-center text-right text-2xl font-normal opacity-0 transition-all group-hover/link:font-bold group-hover/navbar:opacity-100"
						>
							<div>{page.title}</div>
						</div>
					</a>
				</div>
				{#if index < pages.length - 1}
					<div
						class="h-[1px] w-full max-w-0 bg-black opacity-50 transition-all group-hover/navbar:max-w-full"
					></div>
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
