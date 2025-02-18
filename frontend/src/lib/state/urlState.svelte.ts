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
