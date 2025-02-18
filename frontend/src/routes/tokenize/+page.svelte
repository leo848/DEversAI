<script lang="ts">
	import BorderSection from '$lib/components/BorderSection.svelte';
	import TokenComponent from '$lib/components/Token.svelte';
	import vocabulary from '$lib/tokenizing/german50000';
	import type { Token } from '$lib/tokenizing/token';
	import { urlStringStore } from '$lib/state/urlState.svelte';

	let string = urlStringStore('i', {
		default: 'Gib oben den Text ein, unten im Ausgabefeld erscheint dann die Token-Repräsentation.'
	});

	let lastAppliedMergeRule = $state(vocabulary.mergeRules.length + 256);

	let byteCount = $derived(new TextEncoder().encode($string).length);
	let tokens = $derived(vocabulary.tokenize($string, { lastAppliedMergeRule }));

	let hoveredTokenIndex: null | number = $state(null);

	function tokenColor(token: Token, index: number) {
		return token.isByte()
			? 'gray'
			: (['pastelBlue', 'pastelPink', 'pastelYellow', 'pastelGreen'] as const)[index % 4];
	}

	const colorDict = {
		gray: '#666666',
		pastelBlue: '#2874a6',
		pastelGreen: '#2e8b57',
		pastelPink: '#c71585',
		pastelYellow: '#cc9900'
	};
</script>

<div class="m-4 flex flex-col gap-8 xl:mx-16">
	<div class="text-4xl font-bold">Tokenisierung</div>

	<div class="grid grid-cols-12 gap-8">
		<div class="col-span-8">
			<BorderSection title="Eingabe">
				<textarea
					class="w-full rounded-xl border-2 border-gray-200 p-4 text-2xl transition-all focus:border-gray-500"
					bind:value={$string}
				>
				</textarea>
			</BorderSection>
		</div>
		<div class="col-span-4 row-span-3 flex flex-col gap-8">
			<BorderSection title="Statistiken">
				{#if $string.length > 0}
					<ul class="grid grid-cols-3 gap-4">
						<BorderSection innerClass="flex flex-col align-center items-center">
							<div class="text-2xl">{byteCount}</div>
							<div>Bytes</div>
						</BorderSection>
						<BorderSection innerClass="flex flex-col align-center items-center">
							<div class="text-2xl">{$string.split(/\s/).length}</div>
							<div>Wörter</div>
						</BorderSection>
						<BorderSection innerClass="flex flex-col align-center items-center">
							<div class="text-2xl">{tokens.length}</div>
							<div>Tokens</div>
						</BorderSection>
						<BorderSection innerClass="flex flex-col align-center items-center">
							<div class="text-2xl">
								{(byteCount / tokens.length).toFixed(2)}
							</div>
							<div>Bytes / Token</div>
						</BorderSection>
						<BorderSection innerClass="flex flex-col align-center items-center">
							<div class="text-2xl">
								{(tokens.length / $string.split(/\s/).length).toFixed(2)}
							</div>
							<div>Tokens / Wort</div>
						</BorderSection>
						<BorderSection innerClass="flex flex-col align-center items-center">
							<div class="text-2xl">
								{(100 - (tokens.length / byteCount) * 2 * 100).toFixed(1)}%
							</div>
							<div>Kompressionsrate</div>
						</BorderSection>
					</ul>
				{:else}
					<div class="text-disabled">Gib einen Text ein, um Statistiken anzeigen zu können.</div>
				{/if}
			</BorderSection>

			<BorderSection title="Einstellungen">
				<div>
					Letztes zusammengefügtes Token
					{#if lastAppliedMergeRule != vocabulary.tokens.length}
						<span>
							<TokenComponent token={vocabulary.tokens[lastAppliedMergeRule]} />
						</span>
					{/if}
				</div>
				<input
					type="range"
					bind:value={lastAppliedMergeRule}
					min={255}
					max={vocabulary.mergeRules.length + 256}
				/>
				<input
					type="number"
					bind:value={lastAppliedMergeRule}
					min={255}
					max={vocabulary.mergeRules.length + 256}
				/>
			</BorderSection>
		</div>

		<div class="col-span-8">
			<BorderSection title="Tokens" innerClass="flex flex-col gap-2">
				<div class="flex flex-row flex-wrap gap-0 gap-y-4">
					{#each tokens as token, index}
						{@const color = tokenColor(token, index)}
						<div
							onmousemove={() => (hoveredTokenIndex = index)}
							onmouseout={() => (hoveredTokenIndex = null)}
							onblur={() => (hoveredTokenIndex = null)}
							role="none"
						>
							<TokenComponent {token} rawString noPad {color} bold={hoveredTokenIndex == index} />
						</div>
					{/each}
				</div>
			</BorderSection>
		</div>

		<div class="col-span-8">
			<BorderSection title="Token-IDs" open={false}>
				<div class="font-mono">
					[
					{#each tokens as token, index}
						<span>
							{#if index != 0}
								<span>,</span>
							{/if}
							<span
								style:color={colorDict[tokenColor(token, index)]}
								class:font-bold={hoveredTokenIndex == index}
								class="transition-all"
								onmousemove={() => (hoveredTokenIndex = index)}
								onmouseout={() => (hoveredTokenIndex = null)}
								onblur={() => (hoveredTokenIndex = null)}
								role="none"
							>
								{token.id()}
							</span>
						</span>
					{/each}
					]
				</div>
			</BorderSection>
		</div>
	</div>
</div>
