<script lang="ts">
	import * as d3 from 'd3';
	import type { Gradient } from '$lib/util/color';
	import { assert } from '$lib/util/typed';

	type HistogramProps = {
		posts: number[];
		values: number[];
		colorGradient: Gradient;
	};

	const { posts, values, colorGradient }: HistogramProps = $props();

	// Ensure the input is valid
	assert(
		posts.length === values.length + 1,
		`Posts must have n+1 elements compared to values, but posts.length = ${posts.length}, values.length = ${values.length}`
	);

	let svg: SVGSVGElement;

	$effect(() => {
		if (!svg) return;

		const width = 100;
		const height = 50;

		const maxBucketCount = d3.max(values) ?? 1; // Prevent division by zero
		const barWidth = width / (posts.length - 1); // Fix bar width calculation

		// Define scales
		const xScale = d3
			.scaleLinear()
			.domain([posts[0], posts[posts.length - 1]])
			.range([0, width]);
		const yScale = d3.scaleLinear().domain([0, maxBucketCount]).range([height, 0]);

		// Select the SVG group
		const selection = d3
			.select(svg)
			.attr('viewBox', `0 0 ${width} ${height}`)
			.attr('preserveAspectRatio', 'xMidYMid meet')
			.select('g');

		// Bind data
		const bars = selection.selectAll<SVGRectElement, number>('rect').data(values, (_, i) => i);

		// Enter: New bars
		bars
			.enter()
			.append('rect')
			.attr('x', (_, i) => xScale(posts[i])) // Corrected X position
			.attr('width', barWidth - 1)
			.attr('y', height)
			.attr('height', 0)
			.attr('fill', (_, i) => colorGradient.sample(i / (values.length - 1)).toString())
			.transition()
			.duration(400)
			.attr('y', (d) => yScale(d))
			.attr('height', (d) => height - yScale(d));

		// Update: Adjust existing bars
		bars
			.transition()
			.duration(400)
			.attr('x', (_, i) => xScale(posts[i])) // Ensure bars shift correctly
			.attr('width', barWidth - 1)
			.attr('y', (d) => yScale(d))
			.attr('height', (d) => height - yScale(d))
			.attr('fill', (_, i) => colorGradient.sample(i / (values.length - 1)).toString());

		// Exit: Remove disappearing bars
		bars.exit().transition().duration(400).attr('height', 0).remove();
	});
</script>

<svg bind:this={svg} class="chart">
	<g></g>
</svg>

<style>
	.chart {
		width: 100%;
		height: 100%;
		display: block;
	}
</style>
