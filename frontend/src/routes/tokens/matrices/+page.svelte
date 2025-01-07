<script lang="ts">
	import vocabulary from '$lib/tokenizing/german50000';
	import type { Token } from '$lib/tokenizing/token';
	import { Gradient } from '$lib/util/color';

	const colorToken = (number: number) => {
		const numberNormalized =
			(Math.log10(number) - Math.log10(255)) /
			(Math.log10(vocabulary.tokens.length) - Math.log10(255));
		const color = Gradient.Viridis.sample(numberNormalized);
		return color;
	};

	const charToToken = (char: string) => {
		return vocabulary.displaySet.get(char)!;
	};

	const options = {
		small: {
			title: 'Kleinbuchstaben',
			symbols: 'a b c',
			tokens: [...'abcdefghijklmnopqrstuvwxyzäöüß'].map(charToToken)
		},
		capital: {
			title: 'Großbuchstaben',
			symbols: 'A B C',
			tokens: [...'ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ'].map(charToToken)
		},
		digits: {
			title: 'Ziffern',
			symbols: '1 2 3',
			tokens: [...'0123456789'].map(charToToken)
		},
		symbols: {
			title: 'Symbole',
			symbols: '. ! ?',
			tokens: [...'.,;:!?§$€%&()[]{}-+*/#\'"'].map(charToToken)
		},
		title: {
			title: 'Erste zusammengefügte Tokens',
			symbols: 'en er',
			tokens: vocabulary.tokens.slice(256, 256 + 20)
		},
		digitPairs: {
			title: 'Zweiziffrige Zahlen',
			symbols: '00 01',
			tokens: new Array(10)
				.fill(-1)
				.map((_, i) => i.toString())
				.flatMap((i) =>
					new Array(10)
						.fill(-1)
						.map((_, i) => i.toString())
						.map((j) => i + j)
				)
				.map(charToToken)
		}
	} as const satisfies Record<string, { title: string; symbols: string; tokens: Token[] }>;

	let entry: [keyof typeof options, keyof typeof options] = $state(['small', 'small']);
</script>

<div class="m-4 flex flex-col gap-8 xl:mx-16">
	<div class="text-4xl font-bold">Matrizen</div>

	<div class="grid grid-cols-2">
		{#each { length: 2 } as _, i}
			{@const title = ['Zeilen', 'Spalten'][i]}
			<div>
				<div class="col-span-2 text-2xl font-bold xl:col-span-1">{title}</div>
				<div class="flex flex-row gap-4 text-2xl">
					{#each Object.keys(options) as (keyof typeof options)[] as optionKey}
						<button
							class="bg-primary-2 h-20 w-20 rounded-xl border border-2 p-2 transition-all hover:bg-fire-300"
							class:bg-fire-300={entry[1 - i] == optionKey}
							onclick={() => {
								entry[1 - i] = optionKey;
							}}>{options[optionKey].symbols}</button
						>
					{/each}
				</div>
			</div>
		{/each}
	</div>

	<div class="grid grid-cols-12 gap-4">
		<div class="col-span-12 lg:col-span-6">
			<table class="font-mono text-sm">
				<tbody>
					{#each { length: options[entry[1]].tokens.length + 1 } as _, i}
						<tr>
							{#each { length: options[entry[0]].tokens.length + 1 } as _, j}
								{#if i == 0 && j == 0}
									<td class="p-1"> \ </td>
								{:else if i == 0}
									<td class="p-1">
										<span class="inline-block h-8"
											>{options[entry[0]].tokens[j - 1].toStringDebug()}</span
										>
									</td>
								{:else if j == 0}
									<td class="p-1">
										<span class="inline-block w-8"
											>{options[entry[1]].tokens[i - 1].toStringDebug()}</span
										>
									</td>
								{:else}
									{@const tokenString = `${options[entry[1]].tokens[i - 1]}${options[entry[0]].tokens[j - 1]}`}
									{@const token = vocabulary.displaySet.get(tokenString)}
									{#if token != undefined}
										{@const color = colorToken(token.id())}
										<td
											style:background-color={color.toString()}
											style:color={color.readable().toString()}
										>
											<a href={`/token/${token.id()}`}>{token.toStringDebug()}</a>
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
		</div>
	</div>
</div>

<style>
	td {
		border: 0.5px solid #00000033;
	}
</style>
