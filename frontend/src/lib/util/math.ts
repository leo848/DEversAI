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

