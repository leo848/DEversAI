<script lang="ts">
	import { Client } from '$lib/backend/client';
	import { LogitsResponse } from '$lib/backend/types';
	import TopLogits from '$lib/components/TopLogits.svelte';
	import vocabulary from '$lib/tokenizing/german50000';

	const client = new Client();

	const initialValue = 'In der Pfanne ausbacken. ';

	let inputString = $state(initialValue);
	let processString = $state(initialValue);

	let tokens = $derived(vocabulary.tokenize(processString));

	let logitsInference = $derived({
		anticausal1: () => client.modelLogits('anticausal1', tokens.toReversed()),
		causal1: () => client.modelLogits('causal1', tokens)
	});

	let changeProcessTimeout: null | number = null;
	$effect(() => {
		inputString;
		if (changeProcessTimeout != null) clearTimeout(changeProcessTimeout);
		changeProcessTimeout = setTimeout(() => {
			processString = inputString;
		}, 1000);
	});
</script>

<div class="m-4 flex flex-col gap-8 xl:mx-16">
	<div class="text-4xl font-bold">Inferenz</div>

	<div class="grid grid-cols-3 gap-4">
		<div class="min-w-200">
			{#await logitsInference.anticausal1()}
				Lade Logits...
			{:then logitsResponse}
				<TopLogits
					{logitsResponse}
					ontokenclick={(token) => {
						inputString = token.toString() + inputString;
					}}
				/>
			{:catch error}
				{error}
			{/await}
		</div>
		<div class="w-full">
			<textarea
				class="w-full resize-none overflow-scroll rounded border-2 border-gray-200 text-xl focus:border-gray-400"
				rows={10}
				bind:value={inputString}
			></textarea>
		</div>
		<div class="min-w-200">
			{#await logitsInference.causal1()}
				Lade Logits...
			{:then logitsResponse}
				<TopLogits
					{logitsResponse}
					ontokenclick={(token) => {
						inputString += token.toString();
					}}
				/>
			{:catch error}
				{error}
			{/await}
		</div>
	</div>
</div>
