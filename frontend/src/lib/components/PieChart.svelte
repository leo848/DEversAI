<script lang="ts">
    import { pie, arc, select } from "d3";
    import type { Color } from "$lib/util/color";

    type Datum = {
        value: number;
        label: string;
        color: Color;
    };

    const {
        data,
    }: {
        data: Datum[],
    } = $props();

    let svg: SVGSVGElement;

    $effect(() => {
        if (!svg) return;

        const pieData = pie<Datum>()
            .sort(null)
            .value(d => d.value)(data);

        const arcGenerator = arc<d3.PieArcDatum<Datum>>() 
            .innerRadius(0)
            .outerRadius(50);

        const selection = select(svg)
            .attr("viewBox", "-50 -50 100 100")
            .attr("preserveAspectRatio", "xMidYMid meet")
            .select("g");

        const paths = selection.selectAll<SVGPathElement, d3.PieArcDatum<Datum>>("path").data(pieData);

        paths.join(
            enter => enter.append("path")
                .attr("fill", d => d.data.color.toString())
                .attr("stroke", "white")
                .attr("stroke-width", "1px")
                .attr("d", arcGenerator)
                .attr("opacity", 0)
                .transition().duration(600)
                .attr("opacity", 1),
            update => update.transition().duration(600)
                .attr("d", arcGenerator)
        );

        paths.exit().transition().duration(600).attr("opacity", 0).remove();
    });
</script>

<div class="chart-container">
    <svg bind:this={svg} class="chart">
        <g></g>
    </svg>
</div>

<style>
    .chart-container {
        position: relative;
        width: 100%;
        height: 100%;
    }

    .chart {
        width: 100%;
        height: 100%;
        display: block;
    }
</style>
