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
