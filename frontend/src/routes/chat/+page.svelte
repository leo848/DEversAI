<script lang="ts">
	import { Client } from '$lib/backend/client';
	import BorderSection from '$lib/components/BorderSection.svelte';
	import {models, type ModelId} from '$lib/backend/models';
	import EmergentSpinner from '$lib/components/EmergentSpinner.svelte';
	import TopLogits from '$lib/components/TopLogits.svelte';
	import vocabs from '$lib/tokenizing/vocabs';
	import SimpleInferenceButton from './SimpleInferenceButton.svelte';
	import InferenceOptions from './InferenceOptions.svelte';
	import type { Token } from '$lib/tokenizing/token';
	import { slide } from 'svelte/transition';

	const client = new Client();

	const initialValue = 'In der Pfanne ausbacken. ';

	let inputString = $state(initialValue);

	let processString = $state({
		anticausal: initialValue,
		causal: initialValue
	});

	let vocabulary = (modelId: ModelId) => vocabs[models[modelId].vocab];

	let tokens = $state({
		anticausal: vocabs.fineweb2.tokenize(initialValue),
		causal: vocabs.fineweb2.tokenize(initialValue)
	});

	let logitsInference = $state({
		anticausal: () => client.modelLogits("anticausal" + options.modelId, tokens.anticausal.toReversed()),
		causal: () => client.modelLogits("causal" + options.modelId, tokens.causal)
	});

	const generate = $state((causality: "anticausal" | "causal") => {
		const tokenInput = {
			anticausal: (it: Token[]) => it.toReversed(),
			causal: (it: Token[]) => it
		}[causality](vocabulary(options.modelId).tokenize(inputString));
		const gen = client.autoregressiveInference(causality + options.modelId, tokenInput, {
			num_tokens: Math.floor(Math.exp(options.maxTokens_log)),
			temperature: options.temperature,
			top_k: Math.floor(Math.exp(options.topK_log)),
			synthetic_wait: options.syntheticWait_millis / 1000
		});
		return async () => {
			inProgress.ongoing = true;
			outer: for await (const tokens of gen) {
				for (const token of tokens) {
					if (token == 0xff && options.respectEot || token == -1) break outer;
					({
						causal: () => (inputString += vocabulary(options.modelId).tokens[token].toString()),
						anticausal: () => (inputString = vocabulary(options.modelId).tokens[token].toString() + inputString)
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
		syntheticWait_millis: 0,
		respectEot: true,
		modelId: "-fw2" as "1" | "-fw2",
	});

	function refreshModel(causality: 'anticausal' | 'causal') {
		processString[causality] = inputString;
		tokens[causality] = vocabulary(options.modelId).tokenize(processString[causality]);
		let modelInput = causality == "causal"
			? tokens[causality]
			: tokens[causality].toReversed();
		logitsInference[causality] = () => client.modelLogits(causality + options.modelId, modelInput);
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
				onclick={generate('anticausal')}
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
				onclick={generate('causal')}
				disabled={inProgress.ongoing}
			/>
			<div class="grid grid-cols-12 gap-4">
				<div class="col-span-6">
					<BorderSection title="Rückinferenz" open={false}>
						{#if inputString != processString.anticausal}
							<div class="w-full p-2 text-xl" transition:slide={{ axis: 'y' }}>
								<button class="rounded bg-fire-400 p-2" onclick={() => refreshModel('anticausal')}
									>Aktualisieren</button
								>
							</div>
						{/if}
						{#await logitsInference.anticausal()}
							<EmergentSpinner />
						{:then logitsResponse}
							<TopLogits
								{logitsResponse}
		   						vocabulary={vocabulary(options.modelId)}
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
						{#if inputString != processString.causal}
							<div class="w-full p-2 text-xl" transition:slide={{ axis: 'y' }}>
								<button class="rounded bg-fire-400 p-2" onclick={() => refreshModel('causal')}
									>Aktualisieren</button
								>
							</div>
						{/if}
						{#await logitsInference.causal()}
							<EmergentSpinner />
						{:then logitsResponse}
							<TopLogits
								{logitsResponse}
		   						vocabulary={vocabulary(options.modelId)}
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
