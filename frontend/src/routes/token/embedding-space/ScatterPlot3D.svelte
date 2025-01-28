<script lang="ts">
	import { onMount } from 'svelte';
	import { Deck, COORDINATE_SYSTEM, OrbitView } from '@deck.gl/core';
	import { PointCloudLayer } from '@deck.gl/layers';
	import Token from '$lib/components/Token.svelte';

	import vocabulary from '$lib/tokenizing/german50000';
	import { goto } from '$app/navigation';
	import { Color } from '$lib/util/color';
	import type { Tuple } from '$lib/util/array';
	import { Tween } from 'svelte/motion';

	let {
		points,
		coloring,
		pointSize = 2,
		initialZoom = 8
	}: {
		points: { id: number; position: Tuple<3, number> }[];
		coloring: (id: number) => Color;
		pointSize?: number;
		initialZoom?: number;
	} = $props();

	let tooltipContent: { id: number; position: string } | null = $state(null); // Holds the tooltip content
	let tooltipStyle = $state('display: none;'); // Tooltip visibility and positioning

	let scatterplotElt: HTMLCanvasElement | undefined = $state();
	let deck: Deck<OrbitView> | undefined; // Reference to the deck.gl instance

	const tokenColors = new Tween(
		points.map(({ id }) => coloring(id)),
		{
			interpolate(a, b) {
				if (a.length !== b.length) return (_) => b;
				return (t) =>
					a.map((_, i) => {
						return a[i].lerp(b[i], t);
					});
			}
		}
	);
	$effect(() => {
		coloring;
		tokenColors.target = points.map(({ id }) => coloring(id));
	});

	onMount(() => {
		const view = new OrbitView({
			id: 'view',
			controller: true
		});

		deck = new Deck({
			initialViewState: {
				target: [0, 0, 0],
				zoom: initialZoom
			},
			canvas: scatterplotElt,
			views: view
		});
	});

	$effect(() => {
		if (!deck) return;

		const layer = new PointCloudLayer({
			id: 'PointCloudLayer',
			data: points,
			getColor: (d) => tokenColors.current[d.id].rgb(),
			getPosition: (d) => d.position,
			pointSize: pointSize / 100,
			sizeUnits: 'meters',
			coordinateSystem: COORDINATE_SYSTEM.CARTESIAN,
			pickable: true,
			onHover: (object, evt) => {
				if (!object.picked) {
					tooltipContent = null;
					tooltipStyle = 'display:none';
					return;
				}
				tooltipContent = {
					id: object.object.id,
					position: object.object.position.map((pos: number) => pos.toFixed(2)).join(', ')
				};
				tooltipStyle = `display:block; left: ${evt.srcEvent.clientX}px; top: ${evt.srcEvent.clientY}px`;
			},
			onClick: (object) => {
				if (!object.picked) {
					return;
				}
				goto(`/token/${object.object.id}`);
			},
			updateTriggers: {
				getColor: [tokenColors.current]
			}
		});

		const layers = [layer];

		deck.setProps({ layers });
	});
</script>

<div class="scatterplot-container h-full w-full">
	<canvas id="scatterplot-canvas" bind:this={scatterplotElt}></canvas>
	<!-- Tooltip -->
	{#if tooltipContent}
		<div class="tooltip rounded-xl text-xl" style={tooltipStyle}>
			<Token noTransition token={vocabulary.tokens[tooltipContent.id]} />
			<p>ID: {tooltipContent.id}</p>
			<p>Position: {tooltipContent.position}</p>
		</div>
	{/if}
</div>

<style>
	canvas {
		width: 100%;
		height: 100%;
	}
	.tooltip {
		position: absolute;
		background: rgba(255, 255, 255, 0.9);
		border: 1px solid #ddd;
		padding: 8px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
		pointer-events: none;
		z-index: 1000;
	}
</style>
