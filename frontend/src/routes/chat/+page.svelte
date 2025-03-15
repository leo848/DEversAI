<script lang="ts">
	import { Client } from '$lib/backend/client';
	import EmergentSpinner from '$lib/components/EmergentSpinner.svelte';
	import TopLogits from '$lib/components/TopLogits.svelte';
	import vocabulary from '$lib/tokenizing/german50000';
	import { slide } from 'svelte/transition';

	const client = new Client();

	const initialValue = 'In der Pfanne ausbacken. ';

	let inputString = $state(initialValue);

	let processString = $state({
		anticausal1: initialValue,
		causal1: initialValue
	});

	let tokens = $state({
		anticausal1: vocabulary.tokenize(initialValue),
		causal1: vocabulary.tokenize(initialValue)
	});

	let logitsInference = $state({
		anticausal1: () => client.modelLogits('anticausal1', tokens.anticausal1.toReversed()),
		causal1: () => client.modelLogits('causal1', tokens.causal1)
	});

	let generate = $state({
		causal1: async () => {
			const gen = client.autoregressiveInference('causal1', vocabulary.tokenize(inputString));
			for await (const tokens of gen) {
				for (const token of tokens) {
					if (token == 0xff) return;
					inputString += vocabulary.tokens[token].toString();
				}
			}
		},
		anticausal1: async () => {
			const gen = client.autoregressiveInference(
				'anticausal1',
				vocabulary.tokenize(inputString).toReversed()
			);
			for await (const tokens of gen) {
				for (const token of tokens) {
					if (token == 0xff) return;
					inputString = vocabulary.tokens[token].toString() + inputString;
				}
			}
		}
	});

	function refreshModel(modelName: 'anticausal1' | 'causal1') {
		processString[modelName] = inputString;
		tokens[modelName] = vocabulary.tokenize(processString[modelName]);
		let modelInput = modelName.includes('anti')
			? tokens[modelName].toReversed()
			: tokens[modelName];
		logitsInference[modelName] = () => client.modelLogits(modelName, modelInput);
	}
</script>

<div class="m-4 flex flex-col gap-8 xl:mx-16">
	<div class="text-4xl font-bold">Inferenz</div>

	<div class="grid grid-cols-12 gap-4">
		<div class="col-span-4"></div>
		<div class="col-span-8 w-full">
			<div>
				<button
					class="rounded-xl border border-2 border-gray-200 p-2"
					onclick={generate.anticausal1}
				>
					Antikausale Vorhersage
				</button>
			</div>
			<textarea
				spellcheck={false}
				class="w-full resize-none overflow-scroll rounded-xl border-2 border-gray-200 focus:border-gray-400"
				rows={10}
				bind:value={inputString}
			></textarea>
			<div>
				<button class="rounded-xl border border-2 border-gray-200 p-2" onclick={generate.causal1}>
					Kausale Vorhersage
				</button>
			</div>
		</div>
		<div class="min-w-200 col-span-2 rounded-xl border border-2 border-gray-200 p-2">
			{#if inputString != processString.causal1}
				<div class="w-full p-2 text-xl" transition:slide={{ axis: 'y' }}>
					<button class="rounded bg-fire-400 p-2" onclick={() => refreshModel('causal1')}
						>Aktualisieren</button
					>
				</div>
			{/if}
			{#await logitsInference.causal1()}
				<EmergentSpinner />
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
		<div class="min-w-200 col-span-2 rounded-xl border border-2 border-gray-200 p-2">
			{#if inputString != processString.anticausal1}
				<div class="w-full p-2 text-xl" transition:slide={{ axis: 'y' }}>
					<button class="rounded bg-fire-400 p-2" onclick={() => refreshModel('anticausal1')}
						>Aktualisieren</button
					>
				</div>
			{/if}
			{#await logitsInference.anticausal1()}
				<EmergentSpinner />
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
	</div>
</div>
