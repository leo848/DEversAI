<script lang="ts">
	import { Client } from '$lib/backend/client';
	import BorderSection from '$lib/components/BorderSection.svelte';
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
				<div class="flex flex-col gap-4 text-lg">
					<div class="flex flex-col">
						<div>Maximal erzeugte Tokens: <b>{Math.round(Math.exp(options.maxTokens_log))}</b></div>
						<input
							type="range"
							bind:value={options.maxTokens_log}
							min={Math.log(1)}
							max={Math.log(1001)}
							step={0.001}
						/>
					</div>
					<div class="flex flex-col">
						<div>Temperatur: <b>{options.temperature}</b></div>
						<input type="range" bind:value={options.temperature} min={0.1} max={1.5} step={0.025} />
					</div>
					<div class="flex flex-col">
						<div>
							Top-K: <b>{((v) => (v > 50200 ? '–' : v))(Math.round(Math.exp(options.topK_log)))}</b>
						</div>
						<input
							type="range"
							bind:value={options.topK_log}
							min={Math.log(1)}
							max={Math.log(50261)}
							step={0.001}
						/>
					</div>
					<div class="flex flex-col">
						<div>Wartezeit: <b>{(options.syntheticWait_millis / 1000).toFixed(1)}</b>s</div>
						<input
							type="range"
							bind:value={options.syntheticWait_millis}
							min={0}
							max={2000}
							step={10}
						/>
					</div>
				</div>
			</BorderSection>
		</div>
		<div class="col-span-8 grid w-full gap-4">
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
								topK={Math.exp(options.topK_log)}
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
								topK={Math.exp(options.topK_log)}
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
