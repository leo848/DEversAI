<script lang="ts">
	const {
	title, entries
	}: {
	title: string,
	entries: [string, string|null|undefined][]
	} = $props();
</script>

<div class="border-t pt-4">
<h3 class="text-md font-semibold text-gray-700 mb-2">{title}</h3>
<div class="grid grid-cols-2 gap-2 text-sm text-gray-800">
  {#each entries as [label, value]}
	{#if value}
	  <div><span class="font-medium">{label}:</span> {value}</div>
	{/if}
  {/each}
</div>
</div>
