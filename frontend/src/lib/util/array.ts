export type Tuple<N extends number, T, Acc extends unknown[] = []> = number extends N
	? T[]
	: Acc['length'] extends N
		? Acc
		: Tuple<N, T, [T, ...Acc]>;

export function chunks<T>(arr: T[], n: number): T[][] {
	return Array.from(new Array(Math.ceil(arr.length / n)), (_, i) => arr.slice(i * n, i * n + n));
}

export function chunksExact<N extends number, T>(arr: T[], n: N): Tuple<N, T>[] {
	return chunks(arr, n)
		.filter((chunk) => chunk.length == n)
		.map((t) => t as Tuple<N, T>);
}

export function shuffleArray<T>(arr: T[]): T[] {
	const array = [...arr];
	for (let i = array.length - 1; i >= 1; i--) {
		const j = Math.floor(Math.random() * i);
		[array[i], array[j]] = [array[j], array[i]];
	}
	return array;
}

export function sortByKey<T, K = T>(
	arr: T[],
	key: (element: T) => K,
	{ reverse }: { reverse: boolean } = { reverse: false }
): T[] {
	let reverseFactor = reverse ? -1 : 1;
	return arr.slice().sort((a, b) => {
		const keyA = key(a);
		const keyB = key(b);

		if (keyA < keyB) {
			return -1 * reverseFactor;
		} else if (keyA > keyB) {
			return 1 * reverseFactor;
		} else {
			return 0;
		}
	});
}
