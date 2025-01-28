<script lang="ts">
	import type { Tuple } from '$lib/util/array';
	import ScatterPlot3D from './ScatterPlot3D.svelte';

	const toData = (data: Tuple<3, number>[]) => {
		return data.map((pos, i) => ({ id: i, position: pos, label: `token ${i}` }));
	};

	const randomData = toData(
		Array.from(
			{ length: 50000 },
			(_) => Array.from({ length: 3 }, (_) => Math.random() - 0.5) as Tuple<3, number>
		)
	);
</script>

<div>
	<ScatterPlot3D points={randomData} />
</div>
