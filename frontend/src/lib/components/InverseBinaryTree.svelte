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

let d3Wrapper: HTMLElement;
let svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
let linkGroup: d3.Selection<SVGGElement, unknown, null, undefined>;
let nodeGroup: d3.Selection<SVGGElement, unknown, null, undefined>;

// Function to handle clicks on nodes
function onNodeClick(node: TokenHistory) {
    onClick(node);
}

onMount(() => {
    svg = d3
        .select(d3Wrapper)
        .append('svg')
        .attr('width', width)
        .attr('style', 'max-width: 100%; height: auto; font: 15px Fira Code, ui-monospace, monospace');

    linkGroup = svg.append('g').attr('fill', 'none').attr('stroke', '#555').attr('stroke-opacity', 0.4).attr('stroke-width', 3);
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
    const scaleX = (d: d3.HierarchyPointNode<TokenHistory>) => remap([x0, x1], [20, width - 20])(d.x);
    const scaleY = (d: d3.HierarchyPointNode<TokenHistory>) => -d.y + height - dy;

    svg.attr('viewBox', [0, 0, width, height]);

    const links = root.links();
    const nodes = root.descendants();

    // Update Links
    const link = linkGroup.selectAll('path').data(links, (d) => `${d.source.data.id}-${d.target.data.id}`);
    link
        .enter()
        .append('path')
        .attr('d', (d) =>
            d3
                .linkHorizontal<d3.HierarchyPointNode<TokenHistory>, d3.HierarchyPointLink<TokenHistory>>()
                .x((p) => scaleX(d.source))
                .y((p) => scaleY(d.source))(d)
        )
        .merge(link)
        .transition()
        .duration(750)
        .attr('d', 
            d3
                .linkHorizontal<d3.HierarchyPointNode<TokenHistory>, d3.HierarchyPointLink<TokenHistory>>()
                .x((p) => scaleX(p))
                .y((p) => scaleY(p))
        );
    link.exit().remove();

    // Update Nodes
    const node = nodeGroup.selectAll('g').data(nodes, (d) => d.data.id);

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
                .attr('fill', d => (d.children ? '#ca4' : '#fc8')); // Highlight on hover
            d3.select(this).style('cursor', d => d.children ? 'pointer' : 'auto'); // Add pointer cursor
        })
        .on('mouseout', function (d) {
            d3.select(this)
                .select('rect')
                .attr('fill', (d) => (d.children ? '#fc6' : '#fc8')); // Reset color on mouse out
        });

    nodeEnter
        .append('rect')
        .attr('fill', (d) => (d.children ? '#fc6' : '#fc8'))
        .attr('stroke', (d) => (d.children ? '#ca4' : '#c86'))
        .attr('width', (d) => Math.max(25, d.data.name.length * 10 + 10))
        .attr('height', 25)
        .attr('x', (d) => -Math.max(25, d.data.name.length * 10 + 10) / 2)
        .attr('y', -12.5)
        .attr('rx', 12.5)
        .attr('ry', 12.5);

    nodeEnter
        .append('text')
        .text((d) => d.data.name)
        .attr('text-anchor', 'middle')
        .attr('y', '0.25em');

    nodeEnter
        .transition()
        .duration(750)
        .attr('opacity', 1); // Fade-in animation to fully visible

    // Merge and Update selection
    node
        .merge(nodeEnter)
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
