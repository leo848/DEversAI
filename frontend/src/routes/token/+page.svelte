<script lang="ts">
	import { goto } from '$app/navigation';
	import vocabulary from '$lib/tokenizing/german50000';

	const randomToken = Math.floor(Math.random() * vocabulary.tokens.length);

	goto(`/token/${randomToken}`, { replaceState: true });
</script>
