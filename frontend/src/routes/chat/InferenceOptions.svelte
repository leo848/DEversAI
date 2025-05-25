<script lang="ts">
	import type { ModelId } from '$lib/backend/models';

	let {
		value = $bindable()
	}: {
		value: {
			maxTokens_log: number;
			temperature: number;
			topK_log: number;
			syntheticWait_millis: number;
			respectEot: boolean;
			modelId: ModelId;
		};
	} = $props();
</script>

<div class="flex flex-col gap-4 text-lg">
	<div class="flex flex-col">
		<div>Ausgewähltes Modell</div>
		<select bind:value={value.modelId}>
			<option value="1"> OSCAR (1) </option>
			<option value="-fw2"> FineWeb (2) </option>
			<option value="-fw2-laws1"> FineWeb / Finetune Gesetzestexte </option>
			<option value="-fw2-wikipedia1"> FineWeb / Finetune Wikipedia </option>
		</select>
	</div>
	<div class="flex flex-col">
		<div>Maximal erzeugte Tokens: <b>{Math.round(Math.exp(value.maxTokens_log))}</b></div>
		<input
			type="range"
			bind:value={value.maxTokens_log}
			min={Math.log(1)}
			max={Math.log(1001)}
			step={0.001}
		/>
	</div>
	<div class="flex flex-col">
		<div>Temperatur: <b>{value.temperature}</b></div>
		<input type="range" bind:value={value.temperature} min={0.1} max={1.5} step={0.025} />
	</div>
	<div class="flex flex-col">
		<div>
			Top-K: <b>{((v) => (v > 50200 ? '–' : v))(Math.round(Math.exp(value.topK_log)))}</b>
		</div>
		<input
			type="range"
			bind:value={value.topK_log}
			min={Math.log(1)}
			max={Math.log(50261)}
			step={0.001}
		/>
	</div>
	<div class="flex flex-col">
		<div>Wartezeit: <b>{(value.syntheticWait_millis / 1000).toFixed(1)}</b>s</div>
		<input type="range" bind:value={value.syntheticWait_millis} min={0} max={2000} step={10} />
	</div>
	<div class="flex flex-col">
		<div>EOT (0xFF) respektieren: <input type="checkbox" bind:checked={value.respectEot} /></div>
	</div>
</div>
