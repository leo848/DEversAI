<script lang="ts">
	import TokenList from '$lib/components/TokenList.svelte';
	import vocabulary from '$lib/tokenizing/german50000';
</script>

<div class="m-4 flex flex-col gap-8 xl:mx-16">
	<div class="text-4xl font-bold">Token-Liste</div>
	<TokenList {vocabulary} />
	<div class="h-20"></div>
</div>
