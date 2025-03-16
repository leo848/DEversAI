<script lang="ts">
	import { Client } from '$lib/backend/client';
	import BorderSection from '$lib/components/BorderSection.svelte';
	import EmergentSpinner from '$lib/components/EmergentSpinner.svelte';
	import TopLogits from '$lib/components/TopLogits.svelte';
	import vocabulary from '$lib/tokenizing/german50000';
	import SimpleInferenceButton from './SimpleInferenceButton.svelte';
	import InferenceOptions from './InferenceOptions.svelte';
	import type { Token } from '$lib/tokenizing/token';
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

	const generate = $state((modelName: string) => {
		const causality = modelName.includes('anticausal') ? 'anticausal' : 'causal';
		const tokenInput = {
			anticausal: (it: Token[]) => it.toReversed(),
			causal: (it: Token[]) => it
		}[causality](vocabulary.tokenize(inputString));
		const gen = client.autoregressiveInference(modelName, tokenInput, {
			num_tokens: Math.floor(Math.exp(options.maxTokens_log)),
			temperature: options.temperature,
			top_k: Math.floor(Math.exp(options.topK_log)),
			synthetic_wait: options.syntheticWait_millis / 1000
		});
		return async () => {
			inProgress.ongoing = true;
			outer: for await (const tokens of gen) {
				for (const token of tokens) {
					if (token == 0xff) break outer;
					({
						causal: () => (inputString += vocabulary.tokens[token].toString()),
						anticausal: () => (inputString = vocabulary.tokens[token].toString() + inputString)
					})[causality]();
				}
			}
			inProgress.ongoing = false;
		};
	});

	let inProgress = $state({
		ongoing: false
	});

	let options = $state({
		temperature: 0.8,
		topK_log: Math.log(200),
		maxTokens_log: Math.log(200),
		syntheticWait_millis: 0
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
		<div class="col-span-4">
			<BorderSection title="Einstellungen">
				<InferenceOptions bind:value={options} />
			</BorderSection>
		</div>
		<div class="col-span-8 grid w-full gap-4">
			<SimpleInferenceButton
				causality="anticausal"
				onclick={generate('anticausal1')}
				disabled={inProgress.ongoing}
			/>
			<textarea
				spellcheck={false}
				class="w-full resize-none overflow-scroll rounded-xl border-2 border-gray-200 focus:border-gray-400"
				disabled={inProgress.ongoing}
				rows={10}
				bind:value={inputString}
			></textarea>
			<SimpleInferenceButton
				causality="causal"
				onclick={generate('causal1')}
				disabled={inProgress.ongoing}
			/>
			<div class="grid grid-cols-12 gap-4">
				<div class="col-span-6">
					<BorderSection title="Rückinferenz" open={false}>
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
								temperature={options.temperature}
								topK={Math.floor(Math.exp(options.topK_log))}
								ontokenclick={(token) => {
									inputString = token.toString() + inputString;
								}}
							/>
						{:catch error}
							{error}
						{/await}
					</BorderSection>
				</div>
				<div class="col-span-6">
					<BorderSection title="Hininferenz" open={false}>
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
								temperature={options.temperature}
								topK={Math.floor(Math.exp(options.topK_log))}
								ontokenclick={(token) => {
									inputString += token.toString();
								}}
							/>
						{:catch error}
							{error}
						{/await}
					</BorderSection>
				</div>
			</div>
		</div>
	</div>
</div>
