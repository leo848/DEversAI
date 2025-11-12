<script lang="ts">
	import Icon from '@iconify/svelte';

	const subPages = [
		{
			title: 'Geburtsjahr',
			link: '/statistics/birthyear',
			icon: {
				icon: 'iconoir:birthday-cake'
			},
			description: 'Visualisiere die Wahrscheinlichkeitsverteilung über Geburtsjahre abhängig vom Vornamen.'
		},
		{
			title: "Forcing",
			link: '/statistics/forcing',
			icon: {
				icon: 'meteor-icons:chain'
			},
			description: 'Zwinge das Modell dazu, bestimmten Text auszugeben, und überprüfe so semantische und syntaktische Kohärenz',
		}
	];
</script>

<div class="m-4 flex flex-col gap-8 xl:mx-16">
	<div class="text-4xl font-bold">Statistiken</div>

	<div class="grid grid-cols-2 gap-4">
		{#each subPages as page}
			<a
				href={page.link}
				class="col-span-2 md:col-span-1 bg-gradient flex flex-row justify-between gap-8 rounded-xl p-8 transition-all"
			>
				<div>
					<div class="text-4xl font-bold">{page.title}</div>
					<div class="text-xl">{page.description}</div>
				</div>
				<Icon {...page.icon} height="8em" />
			</a>
		{/each}
	</div>
</div>

<style>
	.bg-gradient {
		filter: saturate(50%);
		background: linear-gradient(to right, #ffcc44 0%, #bb4433 100%);
	}

	.bg-gradient:hover {
		filter: saturate(100%);
	}
</style>
