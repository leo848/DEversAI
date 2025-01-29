<script lang="ts">
	import { Client } from '$lib/backend/client';
	import type { Token } from '$lib/tokenizing/token';
	import vocabulary from '$lib/tokenizing/german50000';
	import type { Tuple } from '$lib/util/array';
	import { Color, Gradient } from '$lib/util/color';
	import ScatterPlot3D from './ScatterPlot3D.svelte';

	const client = new Client();
	const embeddingData = $derived(client.getTokenEmbeddings('anticausal1'));

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
		while (categories[categories.length - 1] == 0) {
			categories.length -= 1;
		}
		return {
			categories,
			unknownCategory,
			paint: (input) => {
				const categoryIndex = classifier(input);
				const color = categoryIndex == -1 ? Color.luma(1.0) : Color.Category10[categoryIndex];
				return color;
			}
		};
	}

	function paintContinuous(metric: Metric): { paint: Painter; min: number; max: number } {
		let min = Infinity,
			max = -Infinity;
		for (let id = 0; id < vocabulary.tokens.length; id++) {
			const value = metric({ id, token: vocabulary.tokens[id] });
			min = Math.min(min, value);
			max = Math.max(max, value);
		}
		return {
			paint: ({ id }) => {
				const value = metric({ id, token: vocabulary.tokens[id] });
				const normalized = (value - min) / (max - min);
				return Gradient.Viridis.sample(1 - normalized);
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

	const option = {
		continuous: (object: { name: string; metric: Metric }) =>
			({
				type: 'continuous',
				name: object.name,
				metric: object.metric,
				...paintContinuous(object.metric)
			}) as const,
		discrete: (object: { name: string; classifier: Metric; labels: string[] }) =>
			({
				type: 'discrete',
				name: object.name,
				metric: object.classifier,
				labels: object.labels,
				...paintDiscrete(object.classifier)
			}) as const
	};

	const paintOptions = {
		id: option.continuous({
			name: 'Token-ID',
			metric: ({ id }) => id
		}),
		suffix: option.discrete({
			name: 'Suffixe',
			labels: ['⎵', '\\n', '-', '.', '/', '(', ',', ':', '_', '"'],
			classifier: suffixClassifier([32, 10, 45, 46, 47, 40, 44, 58, 95, 34])
		}),
		prefix: option.discrete({
			name: 'Präfixe',
			labels: ['\\n', '.', '-', '(', ':', ',', '⎵', ')', '?', '!'],
			classifier: prefixClassifier([10, 46, 45, 40, 58, 44, 32, 41, 63, 33])
		}),
		byteCount: option.continuous({
			name: 'Anzahl Bytes',
			metric: ({ token }) => token.value.length
		}),
		letterCount: option.discrete({
			name: 'Anzahl Wörter',
			labels: ['1', '2'],
			classifier: ({ token }) => token.displayString.split(' ').filter(Boolean).length - 1
		}),
		casing: option.discrete({
			name: 'Groß- / Kleinschreibung',
			labels: ['a b', 'A B', 'A b'],
			classifier: casingClassifier
		})
	} as const satisfies Record<
		string,
		{ type: string; name: string; paint: (input: MetricInput) => Color } & (
			| { type: 'discrete'; labels: string[]; categories: number[]; unknownCategory: number }
			| { type: 'continuous'; min: number; max: number }
		)
	>;
	const paintKeys = Object.keys(paintOptions) as (keyof typeof paintOptions)[];

	let paintKey: keyof typeof paintOptions = $state('id');
	let paintOption = $derived(paintOptions[paintKey]);

	let pointSize = $state(2);

	let scaleGradient = $derived(
		paintOption.type === 'continuous' ? Gradient.Viridis.reverse().css() : 'none'
	);
</script>

<div>
	{#await embeddingData}
		Loading data...
	{:then object}
		<ScatterPlot3D
			points={toData(object.embeddings3D)}
			{pointSize}
			coloring={(id) => paintOption.paint({ id, token: vocabulary.tokens[id] })}
			initialZoom={5}
		/>
	{:catch error}
		Fehler: {error}
	{/await}
	<div class="selection absolute m-4 flex h-svh w-[300px] flex-col gap-4 overflow-scroll">
		<div class="flex flex-col gap-4 rounded-xl border border-gray-300 p-4">
			<div class="flex flex-col items-stretch gap-2">
				<div class="text-xl">Färben nach</div>
				{#each paintKeys as key}
					<button
						class="border-gray block rounded border p-1 hover:bg-gray-100 active:bg-gray-100"
						class:bg-gray-100={paintKey == key}
						onclick={() => (paintKey = key)}>{paintOptions[key].name}</button
					>
				{/each}
			</div>
		</div>
		<div class="flex flex-col gap-4 rounded-xl border border-gray-300 p-4">
			<div class="flex flex-col items-stretch gap-2">
				<div class="text-xl">Legende</div>
				{#if paintOption.type === 'continuous'}
					{@const { min, max } = paintOption}
					{@const digits = Math.max(-Math.log(max - min), 0)}
					{@const rangeStepCount = Math.max(3, 10 - max.toFixed(digits).length)}
					{@const rangeStepSize = (max - min) / (rangeStepCount - 1)}
					{@const rangeSteps = new Array(rangeStepCount)
						.fill(-1)
						.map((_, i) => min + rangeStepSize * i)}
					<div>
						<div style:background={scaleGradient} class="h-8 w-full rounded"></div>
						<div class="flex flex-row justify-between">
							{#each rangeSteps as rangeStepValue}
								<div>{rangeStepValue.toFixed(digits)}</div>
							{/each}
						</div>
					</div>
				{:else if paintOption.type === 'discrete'}
					{@const labels = paintOption.labels}
					{@const colors = Color.Category10}
					{@const categoryCounts = paintOption.categories}

					<div class="grid grid-cols-4 gap-4">
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
			</div>
		</div>
		<div class="flex flex-col gap-4 rounded-xl border border-gray-300 p-4">
			<div class="flex flex-col items-stretch gap-2">
				<div class="text-xl">Darstellung</div>
				<div>
					<div class="-mb-1">Punktgröße: {pointSize.toFixed(1)}</div>
					<input
						type="range"
						class="block w-full"
						min={0.5}
						max={3}
						step={0.1}
						bind:value={pointSize}
					/>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	.selection > div {
		background: rgba(255, 255, 255, 0.9);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
		z-index: 1000;
	}
</style>
