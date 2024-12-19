<script lang="ts">
	import Token from '$lib/components/Token.svelte';
	import vocabulary from '$lib/tokenizing/german50000';

	let string = $state('Gib hier den Text ein...');

	let tokens = $derived(vocabulary.tokenize(string));
</script>

<div class="m-4 flex flex-col gap-8 xl:mx-16">
	<div class="text-4xl font-bold">Tokenisierung</div>

	<div class="grid grid-cols-12 gap-8">
		<div class="col-span-8">
			<textarea
				class="w-full rounded-xl border-2 border-gray-200 p-4 text-2xl transition-all focus:border-gray-500"
				bind:value={string}
			>
			</textarea>
		</div>
		<div class="col-span-4 row-span-2"></div>

		<div class="col-span-8 flex flex-row flex-wrap gap-0 gap-y-4">
			{#each tokens as token, index}
				{@const color = token.isByte()
					? 'gray'
					: (['pastelBlue', 'pastelPink', 'pastelYellow', 'pastelGreen'] as const)[index % 4]}
				<div>
					<Token {token} rawString noPad {color} />
				</div>
			{/each}
		</div>
	</div>
</div>
