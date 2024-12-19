<script lang="ts">
	import BorderSection from '$lib/components/BorderSection.svelte';
	import Token from '$lib/components/Token.svelte';
	import vocabulary from '$lib/tokenizing/german50000';

	let string = $state('Gib oben den Text ein, unten im Ausgabefeld erscheint dann die Token-Repräsentation.');

	let tokens = $derived(vocabulary.tokenize(string));
</script>

<div class="m-4 flex flex-col gap-8 xl:mx-16">
	<div class="text-4xl font-bold">Tokenisierung</div>

	<div class="grid grid-cols-12 gap-8">
		<div class="col-span-8">
			<BorderSection title="Eingabe">
				<textarea
					class="w-full rounded-xl border-2 border-gray-200 p-4 text-2xl transition-all focus:border-gray-500"
					bind:value={string}
				>
				</textarea>
			</BorderSection>
		</div>
		<div class="col-span-4 row-span-2"></div>

		<div class="col-span-8">
			<BorderSection title="Tokens">
				<div class=" flex flex-row flex-wrap gap-0 gap-y-4">
					{#each tokens as token, index}
						{@const color = token.isByte()
							? 'gray'
							: (['pastelBlue', 'pastelPink', 'pastelYellow', 'pastelGreen'] as const)[index % 4]}
						<div>
							<Token {token} rawString noPad {color} />
						</div>
					{/each}
				</div>
			</BorderSection>
		</div>
	</div>
</div>
