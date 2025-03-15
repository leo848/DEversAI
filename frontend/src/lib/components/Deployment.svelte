<script lang="ts">
	import SimpleLink from '$lib/components/SimpleLink.svelte';

	const isDeployed = process.env.VERCEL;

	const fullCommitHash = process.env.VERCEL_GIT_COMMIT_SHA;
	const commitHash = fullCommitHash?.slice(0, 7);
	const commitMsg = process.env.VERCEL_GIT_COMMIT_MESSAGE;

	const commitLink = `https://github.com/leo848/deversai/commit/${fullCommitHash}`;
</script>

{#if isDeployed}
	<div class="mt-4">
		<div class="flex flex-row gap-2 items-center">
			<div class="opacity-50">{commitHash}</div>
			<div class="opacity-90">
				<SimpleLink href={commitLink}>{commitMsg}</SimpleLink>
			</div>
		</div>
	</div>
{/if}
