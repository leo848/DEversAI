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

	function paintCategorical(categoryIndex: number): Color {
		const color = categoryIndex == -1 ? Color.luma(1.0) : Color.Category10[categoryIndex];
		return color;
	}

	function paintContinuous(metric: Metric): Painter {
		let min = Infinity,
			max = -Infinity;
		for (let id = 0; id < vocabulary.tokens.length; id++) {
			const value = metric({ id, token: vocabulary.tokens[id] });
			min = Math.min(min, value);
			max = Math.max(max, value);
		}
		return ({ id }) => {
			const value = metric({ id, token: vocabulary.tokens[id] });
			const normalized = (value - min) / (max - min);
			return Gradient.Viridis.sample(1 - normalized);
		};
	}

	function paintPrefix(prefixes: number[]): Painter {
		// const commonPrefixes = [101, 97, 115, 83, 65, 103, 105, 98, 66, 100];
		// const interestingPrefixes = [10, 46, 45, 40, 58, 44, 32, 41, 63, 33];

		return ({ token }) => {
			const bytes = token.value;
			const categoryIndex = prefixes.findIndex((byte) => bytes[0] == byte);
			return paintCategorical(categoryIndex);
		};
	}

	function paintSuffix(suffixes: number[]): Painter {
		// const commonSuffixes = [32, 114, 110, 116, 108, 115, 10, 104, 101, 103];
		// const interestingSuffixes = [32, 10, 45, 46, 47, 40, 44, 58, 95, 34];

		return ({ token }) => {
			const bytes = token.value;
			const categoryIndex = suffixes.findIndex((byte) => bytes[bytes.length - 1] == byte);
			return paintCategorical(categoryIndex);
		};
	}

	function paintCasing({ token }: MetricInput): Color {
		const string = token.toString();
		if (string.length < 1) {
			return Color.luma(1.0);
		}
		let headUppercase = string[0].toUpperCase() == string[0];
		let headLowercase = string[0].toLowerCase() == string[0];
		let tailUppercase = string.substring(1).toUpperCase() == string.substring(1);
		let tailLowercase = string.substring(1).toLowerCase() == string.substring(1);
		const categoryIndex = [
			headUppercase && tailLowercase,
			headLowercase && tailLowercase,
			headUppercase && tailUppercase
		].findIndex(Boolean);
		return paintCategorical(
			headUppercase == headLowercase || tailUppercase == tailLowercase ? -1 : categoryIndex
		);
	}

	const paintOptions = {
		id: {
			type: 'continuous',
			name: 'Token-ID',
			paint: paintContinuous(({ id }) => id)
		},
		suffix: {
			type: 'categorical',
			name: 'Suffixe',
			paint: paintSuffix([32, 10, 45, 46, 47, 40, 44, 58, 95, 34])
		},
		prefix: {
			type: 'categorical',
			name: 'Präfixe',
			paint: paintPrefix([10, 46, 45, 40, 58, 44, 32, 41, 63, 33])
		},
		byteCount: {
			type: 'continuous',
			name: 'Anzahl Bytes',
			paint: paintContinuous(({ token }) => token.value.length)
		},
		letterCount: {
			type: 'continuous',
			name: 'Anzahl Wörter',
			paint: ({ token }) =>
				paintCategorical(token.displayString.split(' ').filter(Boolean).length - 1)
		},
		casing: {
			type: 'categorical',
			name: 'Groß- / Kleinschreibung',
			paint: paintCasing
		}
	} as const satisfies Record<
		string,
		{ type: string; name: string; paint: (input: MetricInput) => Color }
	>;
	const paintSelectionValues = Object.keys(paintOptions) as (keyof typeof paintOptions)[];

	let paintSelection: keyof typeof paintOptions = $state('id');
	let pointSize = $state(2);

	const tokenColor = $derived(paintOptions[paintSelection].paint ?? (() => paintCategorical(-1)));
</script>

<div>
	{#await embeddingData}
		Loading data...
	{:then object}
		<ScatterPlot3D
			points={toData(object.embeddings3D)}
			{pointSize}
			coloring={(id) => tokenColor({ id, token: vocabulary.tokens[id] })}
			initialZoom={5}
		/>
	{:catch error}
		Fehler: {error}
	{/await}
	<div class="selection absolute m-4 flex w-[300px] flex-col gap-4">
		<div class="flex flex-col gap-4 rounded-xl border border-gray-300 p-4">
			<div class="flex flex-col items-stretch gap-2">
				<div class="text-xl">Färben nach</div>
				{#each paintSelectionValues as key}
					<button
						class="border-gray block rounded border p-1 hover:bg-gray-100 active:bg-gray-100"
						class:bg-gray-100={paintSelection == key}
						onclick={() => (paintSelection = key)}>{paintOptions[key].name}</button
					>
				{/each}
			</div>
		</div>
		<div class="flex flex-col gap-4 rounded-xl border border-gray-300 p-4">
			<div class="flex flex-col items-stretch gap-2">
				<div class="text-xl">Darstellung</div>
				<input type="range" min={0.5} max={3} step={0.1} bind:value={pointSize} />
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
