export const normalize =
	([x1, x2]: [number, number]) =>
	(n: number) =>
		(n - x1) / (x2 - x1);

export const denormalize =
	([y1, y2]: [number, number]) =>
	(n: number) =>
		y1 + n * (y2 - y1);

export const remap =
	([x1, x2]: [number, number], [y1, y2]: [number, number]) =>
	(n: number) =>
		y1 + ((n - x1) * (y2 - y1)) / (x2 - x1);

export const clamp =
	([min, max]: [number, number]) =>
	(n: number) =>
		n <= min ? min : n >= max ? max : n;

export function euclideanDist(a: number[], b: number[]): number {
	let [a1, a2] = [a, b].map(array => array.slice());
	let shorterArray = a1.length >= a2.length ? a1 : a2;
	while (a1.length != a2.length) {
		shorterArray.push(0);
	}
	let distSum = 0;
	for (let i = 0; i < a1.length; i++) {
		distSum += (a1[i] - a2[i]) ** 2;
	}
	return Math.sqrt(distSum);
}
