<script lang="ts">
  import { onMount } from "svelte";
  import { Deck, COORDINATE_SYSTEM, OrbitView } from "@deck.gl/core";
  import { ScatterplotLayer, PointCloudLayer } from "@deck.gl/layers";

  let {
	  points
  }: {
	  points: { id: number, position: [number, number, number], label: string }[]
  } = $props();

  let tooltipContent = $state(null); // Holds the tooltip content
  let tooltipStyle = $state("display: none;"); // Tooltip visibility and positioning

  let scatterplotElt: HTMLCanvasElement | undefined = $state();
  let deck; // Reference to the deck.gl instance

  onMount(() => {
    // Initialize deck.gl

    const layer = new PointCloudLayer({
      id: "PointCloudLayer",
      data: points,
      getColor: (d) => [
        d.position[0] * 256 + 128,
        d.position[1] * 256 + 128,
        d.position[2] * 256 + 128,
      ],
      getPosition: (d) => d.position,
      pointSize: 2,
      coordinateSystem: COORDINATE_SYSTEM.CARTESIAN,
      pickable: true,
    });

    const view = new OrbitView({
      id: "view",
      controller: true,
    });

    deck = new Deck({
      initialViewState: {
        target: [0, 0, 0],
        zoom: 8,
      },
      canvas: scatterplotElt,
      layers: [layer],
      views: view,
    });
  });
</script>

<style>
  #scatterplot-container {
    position: relative;
    width: 100vw;
    height: 100vh;
  }
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
    font-size: 12px;
    z-index: 1000;
  }
</style>

<div id="scatterplot-container">
  <canvas id="scatterplot-canvas" bind:this={scatterplotElt}></canvas>
  <!-- Tooltip -->
  {#if tooltipContent}
    <div class="tooltip" style={tooltipStyle}>
      <h4>{tooltipContent.label}</h4>
      <p>ID: {tooltipContent.id}</p>
      <p>Position: {tooltipContent.position}</p>
    </div>
  {/if}
</div>
