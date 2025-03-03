<script lang="ts">
	import { remap } from '$lib/util/math';
	import * as d3 from 'd3';
	import { onMount, onDestroy } from 'svelte';
	import type { TokenHistory } from '$lib/tokenizing/token';

	const {
		data,
		dy,
		width,
		onClick = (_) => {}
	}: {
		data: TokenHistory;
		dy: number;
		width: number;
		onClick?: (d: TokenHistory) => void;
	} = $props();

	const fontSize = 20;
	const fontBold = false;

	let d3Wrapper: HTMLElement;
	let svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
	let linkGroup: d3.Selection<SVGGElement, unknown, null, undefined>;
	let nodeGroup: d3.Selection<SVGGElement, unknown, null, undefined>;

	type Data = d3.HierarchyNode<TokenHistory>;

	// Function to handle clicks on nodes
	function onNodeClick(node: TokenHistory) {
		onClick(node);
	}

	onMount(() => {
		svg = d3
			.select(d3Wrapper)
			.append('svg')
			.attr('width', width)
			.attr(
				'style',
				`max-width: 100%; height: auto; font: ${fontSize}px Fira Code, ui-monospace, monospace; font-weight: ${fontBold ? "bold" : "regular"}`
			);

		linkGroup = svg
			.append('g')
			.attr('fill', 'none')
			.attr('stroke', '#555')
			.attr('stroke-opacity', 0.4)
			.attr('stroke-width', 3);
		nodeGroup = svg.append('g').attr('stroke-linejoin', 'round').attr('stroke-width', 3);

		renderTree();
	});

	onDestroy(() => {
		svg?.remove();
	});

	$effect(() => {
		renderTree();
	});

	function renderTree() {
		const root = d3.hierarchy(data);
		const tree = d3.cluster<TokenHistory>().nodeSize([1, dy]);
		tree(root);

		let x0 = Infinity;
		let x1 = -Infinity;
		root.each((d) => {
			x0 = Math.min(x0, d.x ?? Infinity);
			x1 = Math.max(x1, d.x ?? -Infinity);
		});

		const height = dy * (root.height + 2);
		const scaleX = (d: Data) => remap([x0, x1], [fontSize, width - fontSize])(d.x!);
		const scaleY = (d: Data) => -d.y! + height - dy;

		svg.attr('viewBox', [0, 0, width, height]);

		const links = root.links();
		const nodes = root.descendants();

		// Update Links
		const link = linkGroup
			.selectAll('path')
			.data(links, (d) => `${(d as any).source.data.id}-${(d as any).target.data.id}`);
		link
			.enter()
			.append('path')
			.attr('d', (d) =>
				d3
					.linkHorizontal<
						d3.HierarchyPointNode<TokenHistory>,
						d3.HierarchyPointLink<TokenHistory>
					>()
					.x((_) => scaleX(d.target))
					.y((_) => scaleY(d.target))(d as any)
			)
			.merge(link as any)
			.transition()
			.delay(250)
			.duration(750)
			.attr(
				'd',
				d3
					.linkHorizontal()
					.x(scaleX as any)
					.y(scaleY as any) as any
			);
		link.exit().remove();

		// Update Nodes
		const node = nodeGroup.selectAll('g').data(nodes, (d) => (d as any).data.id);

		// Enter selection: Add click, hover effects
		const nodeEnter = node
			.enter()
			.append('g')
			.attr('opacity', 0) // Start invisible for fade-in
			.attr('transform', (d) => `translate(${scaleX(d)}, ${scaleY(d)})`)
			.on('click', (_, d) => d.children && onNodeClick(d.data)) // Add click handler
			.on('mouseover', function () {
				d3.select(this)
					.select('rect')
					.attr('fill', (d) => ((d as any).children ? '#ca4' : '#fc8')); // Highlight on hover
				d3.select(this).style('cursor', (d) => ((d as any).children ? 'pointer' : 'auto')); // Add pointer cursor
			})
			.on('mouseout', function (d) {
				d3.select(this)
					.select('rect')
					.attr('fill', (d) => ((d as any).children ? '#fc6' : '#fc8')); // Reset color on mouse out
			});

		nodeEnter
			.append('rect')
			.attr('fill', (d) => (d.children ? '#fc6' : '#fc8'))
			.attr('stroke', (d) => (d.children ? '#ca4' : '#c86'))
			.attr('width', (d) => Math.max(fontSize, d.data.name.length * fontSize / 2 + fontSize))
			.attr('height', fontSize * 1.2)
			.attr('x', (d) => -Math.max(fontSize, (d.data.name.length * fontSize / 2 + fontSize)) / 2)
			.attr('y', -fontSize * 1.2 / 2)
			.attr('rx', fontSize * 1.2 / 2)
			.attr('ry', fontSize * 1.2 / 2);

		nodeEnter
			.append('text')
			.text((d) => d.data.name)
			.attr('text-anchor', 'middle')
			.attr('y', '0.25em');

		nodeEnter.transition().duration(750).attr('opacity', 1); // Fade-in animation to fully visible

		// Merge and Update selection
		node
			.merge(nodeEnter as any)
			.transition()
			.duration(750)
			.attr('transform', (d) => `translate(${scaleX(d)}, ${scaleY(d)})`)
			.attr('opacity', 1); // Ensure opacity is set to 1 during updates

		// Exit selection: Fade-out nodes
		node
			.exit()
			.transition()
			.duration(750)
			.attr('opacity', 0) // Fade-out animation
			.remove();
	}
</script>

<div bind:this={d3Wrapper}></div>
