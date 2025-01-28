<script lang="ts">
	import { onMount } from 'svelte';
	import { Deck, COORDINATE_SYSTEM, OrbitView } from '@deck.gl/core';
	import { PointCloudLayer } from '@deck.gl/layers';
	import Token from '$lib/components/Token.svelte';

	import vocabulary from '$lib/tokenizing/german50000';
	import { goto } from '$app/navigation';
	import { Gradient } from '$lib/util/color';
	import type { Tuple } from '$lib/util/array';

	let {
		points,
		initialZoom = 8
	}: {
		points: { id: number; position: [number, number, number]; color: [number, number, number] }[];
		initialZoom?: number;
	} = $props();

	let tooltipContent: { label: string; id: number; position: string } | null = $state(null); // Holds the tooltip content
	let tooltipStyle = $state('display: none;'); // Tooltip visibility and positioning

	let scatterplotElt: HTMLCanvasElement | undefined = $state();
	let deck; // Reference to the deck.gl instance

	onMount(() => {
		// Initialize deck.gl
		const layer = new PointCloudLayer({
			id: 'PointCloudLayer',
			data: points,
			getColor: (d) => d.color,
			getPosition: (d) => d.position,
			pointSize: 2,
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
                console.log(evt);
				tooltipStyle = `display:block; left: ${evt.srcEvent.clientX}px; top: ${evt.srcEvent.clientY}px`;
			},
			onClick: (object) => {
				if (!object.picked) {
					return;
				}
				goto(`/token/${object.object.id}`);
			}
		});

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
			layers: [layer],
			views: view
		});
	});
</script>

<div class="scatterplot-container w-full h-full">
	<canvas id="scatterplot-canvas" bind:this={scatterplotElt}></canvas>
	<!-- Tooltip -->
	{#if tooltipContent}
		<div class="tooltip text-xl" style={tooltipStyle}>
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
		border-radius: 4px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
		pointer-events: none;
		z-index: 1000;
	}
</style>
