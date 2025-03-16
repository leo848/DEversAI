<script context="module" lang="ts">
	declare let process: {
		env: {
			VERCEL: 1 | undefined;
			VERCEL_GIT_COMMIT_SHA: string | undefined;
			VERCEL_GIT_COMMIT_MESSAGE: string | undefined;
		};
	};
</script>

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
		<div class="flex flex-row items-center gap-2">
			<div class="h-4 w-4 rounded-full opacity-40" style:background-color="#0a0"></div>
			<div class="opacity-50">{commitHash}</div>
			<div class="opacity-90">
				<SimpleLink href={commitLink}>{commitMsg}</SimpleLink>
			</div>
		</div>
	</div>
{/if}
