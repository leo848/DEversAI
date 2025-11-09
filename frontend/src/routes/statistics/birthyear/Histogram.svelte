<script lang="ts">
	import * as d3 from 'd3';
	import { Gradient } from '$lib/util/color';

	const {
		startYear,
		endYear,
		stats,
		data,
		step = 10,
		width = 600,
		height = 200
	}: {
		startYear: number;
		endYear: number;
		stats: { mean: number; mode: number; std: number; skew: number };
		data: Record<string, number>;
		step?: number;
		width?: number;
		height?: number;
	} = $props();

	const colorGradient = Gradient.Viridis;

	const processedData = $derived.by(() => {
		const processed: { year: string; value: number; isAggregated?: boolean }[] = [];
		const dataMap = new Map(Object.entries(data));
		let beforeValue = 0;

		for (const [year, value] of dataMap.entries()) {
			if (parseInt(year) < startYear) {
				beforeValue += value;
				dataMap.delete(year);
			}
		}

		processed.push({ year: `Before`, value: beforeValue, isAggregated: true });

		for (let year = startYear; year < endYear; year += step) {
			const yearStr = String(year);
			processed.push({
				year: yearStr,
				value: dataMap.get(yearStr) || 0
			});
		}

		return processed;
	});

	const padding = { top: 10, right: 10, bottom: 30, left: 40 };

	const yMax = $derived(Math.max(0.101, d3.max(processedData, (d) => d.value) ?? 0));

	const yScale = $derived(
		d3
			.scaleLinear()
			.domain([0, yMax])
			.range([height - padding.bottom, padding.top])
	);

	const xScale = $derived(
		d3
			.scaleBand()
			.domain(processedData.map((d) => d.year))
			.range([padding.left, width - padding.right])
			.padding(0.1)
	);

	function getBarColor(d: { isAggregated?: boolean }, index: number): string {
		if (d.isAggregated) {
			return 'white';
		}
		const t = (index - 1) / (processedData.length - 2);
		return colorGradient.sample(t).toString();
	}
</script>

<div class="chart-container" style:width="{width}px">
	<div class="header">
		<span class="stats">
			(µ ≈ {Math.round(stats.mean)}, D₁ = {Math.round(stats.mode)}, σ ≈ {Math.round(stats.std)},
			γₘ ≈ {stats.skew.toFixed(1)})
		</span>
	</div>

	<svg {width} {height} class="chart-svg">
		<!-- y grid lines -->
		{#each yScale.ticks(4) as tick}
			{#if tick > 0}
				<g class="tick y-tick" transform="translate(0, {yScale(tick)})">
					<line x2={width - padding.right} x1={padding.left}></line>
					<text x={padding.left - 8} dy="0.32em">{tick.toFixed(2)}</text>
				</g>
			{/if}
		{/each}

		<!-- x base line -->
		<g class="tick" transform="translate(0, {yScale(0)})">
			<line x1={padding.left} x2={width - padding.right}></line>
		</g>

		{#each processedData as d, i}
			<rect
				x={xScale(d.year)}
				y={yScale(d.value)}
				width={xScale.bandwidth()}
				height={yScale(0) - yScale(d.value)}
				fill={getBarColor(d, i)}
				stroke="black"
			/>
		{/each}

		{#each processedData as d}
			{@const yearNum = parseInt(d.year)}
			{#if yearNum % 50 === 0 && !Number.isNaN(yearNum)}
				<text
					class="tick x-tick-label"
					x={(xScale(d.year) ?? 0) + xScale.bandwidth() / 2}
					y={height - padding.bottom + 15}
				>
					{d.year}
				</text>
			{/if}
		{/each}
	</svg>
</div>

<style>
	.chart-container {
		background-color: #f8f8f8;
		border: 1px solid #eee;
		border-radius: 1em;
		padding: 1em;
		display: inline-block;
		margin: 0.5em;
	}

	.header {
		margin-bottom: 0.5em;
	}

	.stats {
		font-size: 0.8em;
		color: #555;
		margin-left: 0.5em;
	}

	.chart-svg {
		display: block;
	}

	.tick line {
		stroke: #ccc;
		stroke-dasharray: 2;
	}

	.tick text {
		fill: #555;
		font-size: 12px;
		text-anchor: end;
	}

	.tick.x-tick-label {
		text-anchor: middle;
	}

	rect {
		stroke-width: 1.5;
	}
</style>
