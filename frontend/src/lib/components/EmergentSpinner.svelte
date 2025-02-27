<script lang="ts">
	import {Color} from "$lib/util/color";

	let {
		size = "50px",
		color = Color.luma(0.3)
	}: {
		size?: string,
		color?: Color,
	} = $props()
</script>

<style>
  .spinner-container {
    position: relative;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .spinner {
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-top: 4px solid var(--spinner-color);
    border-radius: 50%;
    width: var(--spinner-size);
    height: var(--spinner-size);
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>

<div class="spinner-container">
  <div class="spinner" style="--spinner-size: {size}; --spinner-color: {color.toString()};"></div>
</div>
