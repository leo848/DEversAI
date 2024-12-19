<script lang="ts">
	import Token from "$lib/components/Token.svelte";
import vocabulary from "$lib/tokenizing/german50000";

	let string = $state("Gib hier den Text ein...");

	let tokens = $derived(vocabulary.tokenize(string))
</script>

<div class="m-4 flex flex-col gap-8 xl:mx-16">
	<div class="text-4xl font-bold">Tokenisierung</div>

	<input class="w-full rounded-xl text-2xl p-4 border-gray-200 focus:border-gray-500 transition-all border-2" type="text" bind:value={string}>

	<div class="flex flex-row flex-wrap gap-0">
		{#each tokens as token}
			<Token {token} />
		{/each}
	</div>

</div>
