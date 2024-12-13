export function assert(value: any, message?: string): asserts value {
	if (!value) {
		throw new Error("Assertion failed: " + (message ?? ""));
	}
}

export function assertNever(value: never): never {
	assert(false, `Asserted never was not, in fact, never, but ${value}`);
}
