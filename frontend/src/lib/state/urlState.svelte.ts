import { goto } from '$app/navigation';
import { page } from '$app/state';
import { toStore, type Writable } from 'svelte/store';

export function urlStringStore(key: string, options?: { default?: string }): Writable<string> {
	const stateDefault = options?.default || '';
	if (page.url.searchParams.get(key) == null) {
		let encoded = encodeURIComponent(stateDefault);
		goto(`?${key}=${encoded}`);
	}
	return toStore(
		() => {
			let urlParam = page.url.searchParams.get(key);
			if (urlParam == null) return stateDefault;
			return decodeURIComponent(urlParam);
		},
		(value: string) => {
			let encoded = encodeURIComponent(value);
			goto(`?${key}=${encoded}`, { replaceState: true, keepFocus: true, noScroll: true });
		}
	);
}

function writableDerived<I, O>(
	base: Writable<I>,
	convert: (value: I) => O,
	reflect: (value: O) => I,
): Writable<O> {
	const { subscribe, set: baseSet, update: baseUpdate } = base;
	return {
		subscribe: (run, invalidate?) =>
			subscribe((value: I) => run(convert(value)), invalidate),
		set: (newValue: O) => baseSet(reflect(newValue)),
		update: (updater: (current: O) => O) =>
			baseUpdate((current: I) => reflect(updater(convert(current)))),
	};
}

export function urlNullableNumberStore(key: string): Writable<null | number> {
	const inner = urlStringStore(key, { default: "" });
	return writableDerived(
		inner,
		string => (Number.isFinite(+string) && string) ? +string : null,
		num => num == null ? "" : num.toString(),
	)
}
