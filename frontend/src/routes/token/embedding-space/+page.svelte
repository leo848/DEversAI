<script lang="ts">
	import { Client } from '$lib/backend/client';
	import type { Token } from '$lib/tokenizing/token';
	import vocabulary from '$lib/tokenizing/fineweb2';
	import { sortByKey, type Tuple } from '$lib/util/array';
	import { Color, Gradient } from '$lib/util/color';
	import ScatterPlot3D from './ScatterPlot3D.svelte';
	import FullLoader from '$lib/components/FullLoader.svelte';
	import PieChart from '$lib/components/PieChart.svelte';
	import Histogram from '$lib/components/Histogram.svelte';
	import MenuEntry from './MenuEntry.svelte';
	import { slide } from 'svelte/transition';
	import { urlNullableNumberStore } from '$lib/state/urlState.svelte';
	import { geminiKeys } from '$lib/backend/geminiTypes';
	import type { Writable } from 'svelte/store';
	import TokenComponent from '$lib/components/Token.svelte';

	const client = new Client();
	let modelDirectionality = $state('anticausal') as 'anticausal' | 'augmented' | 'causal';
	let modelFinetune = $state('') as '' | 'laws1' | 'plenar1';
	let modelName = $derived(modelDirectionality + "-fw2" + (modelFinetune && modelDirectionality != "augmented" ? '-' + modelFinetune : ''));

	const embeddingData = $derived(client.getTokenEmbeddings(modelName));

	const toData = (data: Tuple<3, number>[]) => {
		return data.map((pos, i) => {
			return {
				id: i,
				position: pos
				// color: sampleColor(1 - Math.min(10, vocabulary.tokens[i].value.length - 1) / 10)
				// color: sampleColor(i / 50256)
			};
		});
	};
	const toData2D = (data: Tuple<2, number>[]) => {
		return toData(data.map(([x, y]) => [x, y, 0]));
	};

	let selectedId: Writable<number | null> = urlNullableNumberStore('id');

	type MetricInput = { id: number; token: Token };
	type Metric = (input: MetricInput) => number;
	type Painter = (input: MetricInput) => Color;

	function paintDiscrete(classifier: Metric): {
		paint: Painter;
		categories: number[];
		unknownCategory: number;
	} {
		const categories = new Array(10).fill(0);
		let unknownCategory = 0;
		for (let id = 0; id < vocabulary.tokens.length; id++) {
			const categoryIndex = classifier({ id, token: vocabulary.tokens[id] });
			if (categoryIndex >= 0) {
				categories[categoryIndex] += 1;
			} else {
				unknownCategory += 1;
			}
		}
		return {
			categories,
			unknownCategory,
			paint: (input) => {
				const categoryIndex = classifier(input);
				const color = categoryIndex == -1 || categoryIndex >= 10 ? Color.luma(1.0) : Color.Category10[categoryIndex];
				return color;
			}
		};
	}

	function paintContinuous(metric: Metric): {
		paint: Painter;
		min: number;
		max: number;
		histogram: { values: number[]; posts: number[] };
	} {
		let min = Infinity,
			max = -Infinity;
		for (let id = 0; id < vocabulary.tokens.length; id++) {
			const value = metric({ id, token: vocabulary.tokens[id] });
			min = Math.min(min, value);
			max = Math.max(max, value);
		}
		let histogramBucketSize = 1;
		if (max - min == 100) {
			histogramBucketSize = 11;
		}
		while ((max - min) / histogramBucketSize > 20) {
			histogramBucketSize *= 2;
		}
		const histogramBuckets = [min];
		while (histogramBuckets[histogramBuckets.length - 1] <= max) {
			histogramBuckets.push(histogramBuckets[histogramBuckets.length - 1] + histogramBucketSize);
		}

		const histogram = new Array(histogramBuckets.length - 1).fill(0);
		for (let id = 0; id < vocabulary.tokens.length; id++) {
			const value = metric({ id, token: vocabulary.tokens[id] });
			histogram[Math.floor((value - min) / histogramBucketSize)] += 1;
		}

		return {
			paint: ({ id }) => {
				const value = metric({ id, token: vocabulary.tokens[id] });
				const normalized = (value - min) / (max - min);
				return Gradient.Viridis.sample(1 - normalized);
			},
			histogram: {
				values: histogram,
				posts: histogramBuckets
			},
			min,
			max
		};
	}

	function prefixClassifier(prefixes: number[]): Metric {
		// const commonPrefixes = [101, 97, 115, 83, 65, 103, 105, 98, 66, 100];
		// const interestingPrefixes = [10, 46, 45, 40, 58, 44, 32, 41, 63, 33];

		return ({ token }) => {
			const bytes = token.value;
			return prefixes.findIndex((byte) => bytes[0] == byte);
		};
	}

	function suffixClassifier(suffixes: number[]): Metric {
		// const commonSuffixes = [32, 114, 110, 116, 108, 115, 10, 104, 101, 103];
		// const interestingSuffixes = [32, 10, 45, 46, 47, 40, 44, 58, 95, 34];

		return ({ token }) => {
			const bytes = token.value;
			return suffixes.findIndex((byte) => bytes[bytes.length - 1] == byte);
		};
	}

	function casingClassifier({ token }: MetricInput): number {
		const string = token.toString();
		if (string.length < 1) {
			return -1;
		}
		const head = string[0];
		let headUppercase = head.toUpperCase() == head;
		let headLowercase = head.toLowerCase() == head;
		const tail = string.substring(1);
		let tailUppercase = tail.toUpperCase() == tail;
		let tailLowercase = tail.toLowerCase() == tail;
		const categoryIndex = [
			headLowercase && tailLowercase,
			headUppercase && tailUppercase,
			headUppercase && tailLowercase
		].findIndex(Boolean);
		return headUppercase == headLowercase || (tailUppercase == tailLowercase && tail.length > 0)
			? -1
			: categoryIndex;
	}

	let geminiClassifier: number[] = $state(new Array(50256).fill(-1));
	let geminiLabels = $state(["(Leer)"])

	async function loadGeminiKey(key: { path: string, name: string }) {
		const blacklist = new Set([
			"andere",
			"rest",
			"-1",
			-1,
			"keine",
			null,
			undefined,
		])
		geminiKey = key.path;
		const result = await client.getGeminiColumn(key.path.split("/"));
		const counter: Record<number | string, number> = {};
		for (const entry of result.column) {
			if (entry == null || blacklist.has(entry?.toString()?.toLowerCase())) continue;
			counter[entry] = (counter[entry] ?? 0) + 1;
		}
		const topElements = sortByKey([...new Set(result.column)], element => -(counter[element ?? -1] ?? -1));
		const sliced = topElements.slice(0, Math.min(topElements.length, 10)).map(e => e?.toString()).filter(str => !blacklist.has(str)).map(str => str as string);

		geminiLabels = [...sliced];

		const elementToNumber: Record<string | number, number> = {};
		for (let i = 0; i < sliced.length; i++) {
			elementToNumber[sliced[i]] = i;
		}

		for (let i = 0; i < result.column.length; i++) {
			geminiClassifier[i] = elementToNumber[result.column[i] ?? -1] ?? -1;
		}

		paintKey = paintKey;
	}

	let geminiKey: string = $state('');
	let geminiKeyCategory: string = $state("general")

	const option = {
		continuous: (object: { name: string; metric: Metric }) =>
			() => ({
				type: 'continuous',
				name: object.name,
				metric: object.metric,
				...paintContinuous(object.metric)
			}) as const,
		discrete: (object: { name: string; classifier: Metric; labels: string[] | (() => string[]) }) =>
			() => ({
				type: 'discrete',
				name: object.name,
				metric: object.classifier,
				labels: (typeof object.labels === "function") ? (object.labels) : (() => object.labels as string[]),
				...paintDiscrete(object.classifier)
			}) as const
	};

	const paintOptions = {
		id: option.continuous({
			name: 'Token-ID',
			metric: ({ id }) => id
		}),
		suffixChar: option.discrete({
			name: 'Suffixe (Zeichen)',
			labels: [32, 45].map(i => String.fromCharCode(i)),
			classifier: suffixClassifier([32, 45])
		}),
		suffixLetter: option.discrete({
			name: 'Suffixe (Buchstaben)',
			labels: [110, 116, 114, 101, 105, 115, 108, 104, 103, 97].map(i => String.fromCharCode(i)),
			classifier: suffixClassifier([110, 116, 114, 101, 105, 115, 108, 104, 103, 97])
		}),
		prefix: option.discrete({
			name: 'Präfixe',
			labels: [115, 100, 83, 103, 97, 98, 101, 65, 66, 119].map(i => String.fromCharCode(i)),
			classifier: prefixClassifier([115, 100, 83, 103, 97, 98, 101, 65, 66, 119])
		}),
		byteCount: option.continuous({
			name: 'Anzahl Bytes',
			metric: ({ token }) => token.value.length
		}),
		percentCapital: option.continuous({
			name: 'Anteil Großbuchstaben (%)',
			metric: ({ token }) => {
				return (
					(token.value.filter((value) => value >= 65 && value <= 90).length / token.value.length) *
					100
				);
			}
		}),
		percentSmall: option.continuous({
			name: 'Anteil Kleinbuchstaben (%)',
			metric: ({ token }) => {
				return (
					(token.value.filter((value) => value >= 97 && value <= 122).length / token.value.length) *
					100
				);
			}
		}),
		percentDigit: option.continuous({
			name: 'Anteil Ziffern (%)',
			metric: ({ token }) => {
				return (
					(token.value.filter((value) => value >= 48 && value <= 57).length / token.value.length) *
					100
				);
			}
		}),
		letterCount: option.continuous({
			name: 'Anzahl Wörter',
			metric: ({ token }) => token.displayString.split(' ').filter(Boolean).length
		}),
		casing: option.discrete({
			name: 'Groß- / Kleinschreibung',
			labels: ['a b', 'A B', 'A b'],
			classifier: casingClassifier
		}),
		gemini: option.discrete({
			name: 'LLM-erfasster Eintrag',
			labels: () => geminiLabels,
			classifier: ({ id }) => geminiClassifier[id],
		})
	} as const satisfies Record<
		string,
		() => ({ type: string; name: string; paint: (input: MetricInput) => Color } & (
			| { type: 'discrete'; labels: () => string[]; categories: number[]; unknownCategory: number }
			| {
					type: 'continuous';
					min: number;
					max: number;
					histogram: { posts: number[]; values: number[] };
			  }
		))
	>;
	const paintKeys = Object.keys(paintOptions) as (keyof typeof paintOptions)[];

	let paintKey = $state('id') as keyof typeof paintOptions;

	let paintOption: ReturnType<(typeof paintOptions)[keyof typeof paintOptions]> = $derived(
		paintOptions[paintKey]()
	);

	let dimensionality: '2d' | '3d' = $state('3d') as '2d' | '3d';
	let pointSize = $state(2);

	let scaleGradient = $derived(
		paintOption.type === 'continuous' ? Gradient.Viridis.reverse().css() : 'none'
	);
</script>

<div>
	{#await embeddingData}
		<FullLoader />
	{:then object}
		<ScatterPlot3D
			points={dimensionality == '3d' ? toData(object.embeddings3D) : toData2D(object.embeddings2D)}
			{pointSize}
			bind:selectedId={$selectedId}
			coloring={(id) => paintOption.paint({ id, token: vocabulary.tokens[id] })}
			initialZoom={5}
		/>
	{:catch error}
		Fehler: {error}
	{/await}
	<div
		class="selection absolute flex h-svh w-[300px] flex-col gap-4 overflow-scroll p-4 2xl:w-[400px]"
	>
		{#if $selectedId != null}
			<MenuEntry title="Ausgewähltes Token">
				<!--<div class="italic opacity-50">Kein Token ausgewählt</div>-->
				<TokenComponent size="lg" token={vocabulary.tokens[$selectedId]} />
			</MenuEntry>
		{/if}

		<MenuEntry title="Ansicht">
			<div class="grid grid-cols-2 gap-4">
				<button
					class="align-center rounded border border-gray-200 p-3 text-center text-4xl transition-all hover:bg-gray-100 active:bg-gray-100"
					class:bg-gray-100={dimensionality == '2d'}
					onclick={() => (dimensionality = '2d')}
				>
					2D
				</button>
				<button
					class="align-center rounded border border-gray-200 p-3 text-center text-4xl transition-all hover:bg-gray-100 active:bg-gray-100"
					class:bg-gray-100={dimensionality == '3d'}
					onclick={() => (dimensionality = '3d')}
				>
					3D
				</button>
				<div class="grid grid-cols-5 col-span-2 gap-4">
					<button
						class="col-span-2 align-center rounded border border-gray-200 p-3 text-center transition-all hover:bg-gray-100 active:bg-gray-100"
						class:bg-gray-100={modelDirectionality == 'causal'}
						onclick={() => (modelDirectionality = 'causal')}
					>
						causal1
					</button>
					<button
						class="align-center rounded border border-gray-200 p-3 text-center transition-all hover:bg-gray-100 active:bg-gray-100"
						class:bg-gray-100={modelDirectionality == 'augmented'}
						onclick={() => (modelDirectionality = 'augmented')}
						>
						+
					</button>
					<button
						class="col-span-2 align-center rounded border border-gray-200 p-3 text-center transition-all hover:bg-gray-100 active:bg-gray-100"
						class:bg-gray-100={modelDirectionality == 'anticausal'}
						onclick={() => (modelDirectionality = 'anticausal')}
					>
						anticausal1
					</button>
				</div>
				<div class="self-center text-right">Finetune</div>
				<select bind:value={modelFinetune}>
					<option value="">Basis</option>
					<option value="laws1">Gesetzestexte</option>
					<option value="plenar1">Plenarprotokolle</option>
				</select>
			</div>
		</MenuEntry>

		<MenuEntry title="Färben nach">
			{#each paintKeys as key}
				<button
					class="border-gray block rounded border p-1 transition-all hover:bg-gray-100 active:bg-gray-100"
					class:bg-gray-100={paintKey == key}
					onclick={() => (paintKey = key)}>{paintOptions[key]().name}</button
				>
			{/each}
		</MenuEntry>

		{#if paintKey == "gemini"}
			<MenuEntry title="LLM-Schlüssel">
				<select bind:value={geminiKeyCategory}>
					<option value="general">Allgemein</option>
					<option value="substantiv">Substantiv</option>
					<option value="verb">Verb</option>
					<option value="adjektiv">Adjektiv</option>
					<option value="pronomen">Präposition</option>
					<option value="other">Weitere</option>
				</select>
				{#each geminiKeys.filter(key => key.category == geminiKeyCategory) as key}
					<button
						class="border-gray block rounded border p-1 transition-all hover:bg-gray-100 active:bg-gray-100"
						class:bg-gray-100={geminiKey == key.path}
						onclick={() => loadGeminiKey(key)}>{key.name}</button
					>
				{/each}
			</MenuEntry>
		{/if}

		<MenuEntry title="Legende">
			{#if paintOption.type === 'discrete'}
				{@const labels = paintOption.labels()}
				{@const colors = Color.Category10}
				{@const categoryCounts = paintOption.categories}

				<div class="grid grid-cols-4 gap-4" in:slide={{ axis: 'y' }}>
					{#each labels as label, id}
						<div class="h-8 w-8 rounded" style:background={colors[id].toString()}></div>
						<div class="self-start">{label}</div>
						<div class="opacity-50">({categoryCounts[id]})</div>
						<div class="opacity-50">
							{((categoryCounts[id] / vocabulary.tokens.length) * 100).toFixed(2)}%
						</div>
					{/each}
					{#if paintOption.unknownCategory !== 0}
						<div class="h-8 w-8 rounded bg-gray-300"></div>
						<div class="self-start">Rest</div>
						<div class="opacity-50">({paintOption.unknownCategory})</div>
						<div class="opacity-50">
							{((paintOption.unknownCategory / vocabulary.tokens.length) * 100).toFixed(2)}%
						</div>
					{/if}
				</div>
			{/if}
			{#if paintOption.type === 'continuous'}
				{@const min = paintOption.min}
				{@const max = paintOption.max}
				{@const digits = Math.max(-Math.log(max - min), 0)}
				{@const rangeStepCount =
					max - min == 100
						? 6
						: Math.min(max - min + 1, Math.max(3, 10 - max.toFixed(digits).length))}
				{@const rangeStepSize = (max - min) / (rangeStepCount - 1)}
				{@const rangeSteps = new Array(rangeStepCount)
					.fill(-1)
					.map((_, i) => min + rangeStepSize * i)}
				<div transition:slide={{ axis: 'x' }}>
					<div style:background={scaleGradient} class="h-8 w-full rounded"></div>
					{#key rangeSteps}
						<div class="flex flex-row justify-between" in:slide={{ axis: 'x' }}>
							{#each rangeSteps as rangeStepValue}
								<div>{rangeStepValue.toFixed(digits)}</div>
							{/each}
						</div>
					{/key}
				</div>
			{/if}
		</MenuEntry>
		<MenuEntry title={paintOption.type === 'continuous' ? 'Histogramm' : 'Tortendiagramm'}>
			{#if paintOption.type === 'continuous'}
				<Histogram {...paintOption.histogram} colorGradient={Gradient.Viridis.reverse()} />
			{:else if paintOption.type === 'discrete'}
				<PieChart
					data={new Array(11).fill(-1).map((_, i) =>
						i == 10
							? {
									color: Color.luma(0.8),
									value: paintOption.unknownCategory / vocabulary.tokens.length,
									label: 'Rest'
								}
							: {
									value: paintOption.categories[i] / vocabulary.tokens.length,
									color: Color.Category10[i],
									label: paintOption.labels()[i]
								}
					)}
				/>
			{/if}
		</MenuEntry>
		<MenuEntry title="Darstellung">
			<div>
				<div class="-mb-1">Punktgröße: {pointSize.toFixed(1)}</div>
				<input
					type="range"
					class="block w-full"
					min={0.1}
					max={5}
					step={0.1}
					bind:value={pointSize}
				/>
			</div>
		</MenuEntry>
	</div>
</div>
