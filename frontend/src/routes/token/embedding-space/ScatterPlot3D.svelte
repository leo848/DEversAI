<script lang="ts">
	import { onMount } from 'svelte';
	import {
		Deck,
		COORDINATE_SYSTEM,
		OrbitView,
		LinearInterpolator,
		LightingEffect,
		AmbientLight
	} from '@deck.gl/core';
	import { PointCloudLayer } from '@deck.gl/layers';
	import Token from '$lib/components/Token.svelte';

	import vocabulary from '$lib/tokenizing/german50000';
	import { Color } from '$lib/util/color';
	import type { Tuple } from '$lib/util/array';
	import { Tween } from 'svelte/motion';

	let {
		points,
		coloring,
		selectedId = $bindable(),
		pointSize = 2,
		initialZoom = 8
	}: {
		points: { id: number; position: Tuple<3, number> }[];
		coloring: (id: number) => Color;
		selectedId: null | number;
		pointSize?: number;
		initialZoom?: number;
	} = $props();

	let tooltipContent: { id: number; position: string } | null = $state(null); // Holds the tooltip content
	let tooltipStyle = $state('display: none;'); // Tooltip visibility and positioning

	let scatterplotElt: HTMLCanvasElement | undefined = $state();
	let deck: Deck<OrbitView> | undefined; // Reference to the deck.gl instance

	let justSelected = $state(false);

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

	const initialViewState = {
		target: [0, 0, 0] satisfies Tuple<3, number>,
		zoom: initialZoom,
		rotationOrbit: -1,
		rotationX: 0
	};
	onMount(() => {
		const view = new OrbitView({
			id: 'view',
			controller: {
				scrollZoom: {
					smooth: true
				},
				doubleClickZoom: false
			}
		});

		deck = new Deck({
			initialViewState,
			canvas: scatterplotElt,
			views: view,
			effects: [
				new LightingEffect({
					ambientLight: new AmbientLight({
						color: [255, 255, 255],
						intensity: 1.0
					})
				})
			]
		});

		scatterplotElt!.addEventListener('click', (evt) => {
			if (!justSelected) selectedId = null;
		});

		if (selectedId != null) {
			let id = selectedId;
			select(id);
			setTimeout(() => select(id), 100);
		}
	});

	function select(tokenId: number, incremental: null | { rotation: number } = null) {
		if (!deck) return;
		let duration = 200;
		if (incremental == null) {
			selectedId = tokenId;
			justSelected = true;
			duration = 1000;
			setTimeout(() => (justSelected = false), 200);
		}
		let transitionEnded = false;
		const newViewState = {
			rotationOrbit: (incremental?.rotation ?? 1) + 2,
			rotationX: 40,
			target: points[tokenId].position,
			zoom: 9,
			transitionDuration: duration,
			transitionInterpolator: new LinearInterpolator([
				'zoom',
				'target',
				'rotationOrbit',
				'rotationX'
			]),
			onTransitionEnd: () => {
				transitionEnded = true;
				let rotation = (incremental?.rotation ?? 0) + 2;
				if (selectedId != null) {
					select(tokenId, { rotation });
				}
			}
		};
		deck.setProps({
			initialViewState: newViewState
		});
		if (incremental == null) {
			setTimeout(() => {
				if (!transitionEnded) newViewState.onTransitionEnd();
			}, 1100);
		}
	}

	$effect(() => {
		if (!deck) return;

		if (selectedId != null) {
			select(selectedId);
		}

		const layer = new PointCloudLayer({
			id: 'PointCloudLayer',
			data: points,
			getColor:
				selectedId == null
					? (d) => tokenColors.current[d.id].rgb()
					: (d) =>
							d.id == selectedId ? [255, 0, 0] : tokenColors.current[d.id].saturate(-2).rgb(),
			getPosition: (d) => d.position,
			material: {
				ambient: 0.8,
				shinyness: 60,
				diffuse: 0.5
			},
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
				const { clientX, clientY } = evt.srcEvent as MouseEvent;
				tooltipStyle = `display:block; left: ${clientX}px; top: ${clientY}px`;
			},
			onDragStart: () => {
				selectedId = null;
			},
			onClick: (object) => {
				// goto(`/token/${object.object.id}`);
				select(object.object.id);
			},
			updateTriggers: {
				getColor: [tokenColors.current, selectedId]
			},
			transitions: {
				getPosition: {
					type: 'spring',
					damping: 0.5,
					stiffness: 0.05
				}
			}
		});

		const layers = [layer];

		deck.setProps({ layers });
	});
</script>

<div class="h-full w-full">
	<canvas id="scatterplot-canvas" bind:this={scatterplotElt}></canvas>
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
