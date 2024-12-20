<script lang="ts">
	import Icon from '@iconify/svelte';

	const subPages = [
		{
			title: 'Liste',
			link: '/tokens/list',
			icon: {
				icon: 'ic:round-list'
			},
			description: 'Betrachte alle Tokens in einer Liste, sortiere, suche und filtere sie.'
		},
		{
			title: 'Tokenizen',
			link: '/tokenize',
			icon: {
				icon: 'mdi:set-split'
			},
			description:
				'Tokenize eigenen Eingabetext und erfasse Statistiken über die Tokendistribution.'
		},
		{
			title: 'Zufälliges Token',
			link: '/token',
			icon: {
				icon: 'gravity-ui:dice-6'
			},
			description: 'Betrachte die Tokeninformationsseite für ein zufälliges Token.'
		},
		{
			title: 'Matrizen',
			link: '/tokens/matrices',
			icon: {
				icon: 'tabler:matrix'
			},
			description: 'Betrachte die Existenz von zusammengefügten Tokens anhand von Matrizen.'
		}
	];
</script>

<div class="m-4 flex flex-col gap-8 xl:mx-16">
	<div class="text-4xl font-bold">Tokens</div>

	<div class="grid grid-cols-2 gap-4">
		{#each subPages as page}
			<a
				href={page.link}
				class="bg-gradient flex flex-row justify-between gap-8 rounded-xl p-8 transition-all"
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
