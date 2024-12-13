<script lang="ts">
	import {goto} from "$app/navigation";
	import demoVocabulary from "$lib/tokenizing/demoVocabulary";

	const randomToken = Math.floor(Math.random() * demoVocabulary.tokens.length);

	goto(`/token/${randomToken}`, { replaceState: true })
</script>
