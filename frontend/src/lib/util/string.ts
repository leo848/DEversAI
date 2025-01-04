export function leftPad(base: string, char: string, minLen: number) {
	if (base.length >= minLen) return base;
	return char.repeat(((minLen - base.length) / char.length) | 0) + base;
}
