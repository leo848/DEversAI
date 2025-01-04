<script lang="ts">
	import BorderSection from '$lib/components/BorderSection.svelte';
	import vocabulary from '$lib/tokenizing/german50000';
	import { Gradient } from '$lib/util/color';

	const smallLetters = [...'abcdefghijklmnopqrstuvwxyzäöüß'];
	const capitalLetters = [...'ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ'];
	const digits = [...'0123456789'];
	const commonSymbols = [...'.,;:!?§$€%&()[]{}-+*/#\'"'];
	const twentyMergedTokens = vocabulary.tokens.slice(256, 256 + 20).map(t => t.toString());

	const colorToken = (number: number) => {
		const numberNormalized =
			(Math.log10(number) - Math.log10(255)) /
			(Math.log10(vocabulary.tokens.length) - Math.log10(255));
		const color = Gradient.Viridis.sample(numberNormalized);
		return color;
	};

	const entries = [
		{ title: 'Kleinbuchstaben', columns: smallLetters, rows: smallLetters },
		{ title: 'Großbuchstaben', columns: capitalLetters, rows: capitalLetters },
		{ title: 'Ziffern', columns: digits, rows: digits },
		{ title: 'Symbole', columns: commonSymbols, rows: commonSymbols },
		{ title: 'Groß- → Kleinbuchstabe', columns: capitalLetters, rows: smallLetters },
		{ title: '20 erste gemergete Tokens', columns: twentyMergedTokens, rows: twentyMergedTokens },
	] satisfies { title: string; columns: string[]; rows: string[] }[];
</script>

<div class="m-4 flex flex-col gap-8 xl:mx-16">
	<div class="text-4xl font-bold">Matrizen</div>

	<div class="grid grid-cols-12 gap-4">
		{#each entries as entry}
			<div class="col-span-12 lg:col-span-6">
				<BorderSection title={entry.title}>
					<table class="font-mono text-sm">
						<tbody>
							{#each { length: entry.columns.length + 1 } as _, i}
								<tr>
									{#each { length: entry.rows.length + 1 } as _, j}
										{#if i == 0 && j == 0}
											<td class="p-1"> \ </td>
										{:else if i == 0}
											<td class="p-1">
												<span class="inline-block h-8">{entry.rows[j - 1]}</span>
											</td>
										{:else if j == 0}
											<td class="p-1">
												<span class="inline-block w-8">{entry.columns[i - 1]}</span>
											</td>
										{:else}
											{@const tokenString = `${entry.columns[i - 1]}${entry.rows[j - 1]}`}
											{@const token = vocabulary.displaySet.get(tokenString)}
											{#if token != undefined}
												{@const color = colorToken(token.id())}
												<td
													style:background-color={color.toString()}
													style:color={color.readable().toString()}
												>
													<a href={`/token/${token.id()}`}>{tokenString}</a>
												</td>
											{:else}
												<td> </td>
											{/if}
										{/if}
									{/each}
								</tr>
							{/each}
						</tbody>
					</table>
				</BorderSection>
			</div>
		{/each}
	</div>
</div>

<style>
	td {
		border: 0.5px solid #00000033
	}
</style>
