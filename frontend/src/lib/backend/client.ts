import type { Token } from '$lib/tokenizing/token';
import { TokenInfo } from './types';

const pathUtils = {
	join: function (...paths: string[]) {
		let totalPath = paths[0] ?? '';
		for (const path of paths.slice(1)) {
			if (path.startsWith('/')) {
				totalPath = path;
			} else if (totalPath.endsWith('/')) {
				totalPath += path;
			} else {
				totalPath += '/' + path;
			}
		}
		return totalPath;
	}
};

export class Client {
	base: string;
	constructor({ base }: { base?: string } = {}) {
		if (base) {
			this.base = base;
		} else if (import.meta.env.DEV) {
			this.base = 'http://127.0.0.1:8000/v0';
		} else if (import.meta.env.PROD) {
			this.base = 'https://deversai.uber.space/v0';
		} else {
			throw new RangeError('invalid vite value');
		}
	}

	async getTokenInfo(token: Token): Promise<TokenInfo> {
		const apiPath = pathUtils.join(this.base, 'token', token.id().toString(), 'info');
		const response = await fetch(apiPath);
		const json = await response.json();
		const tokenInfo = await TokenInfo.safeParseAsync(json);
		if (tokenInfo.success) {
			return tokenInfo.data;
		} else {
			return Promise.reject('Could not parse response');
		}
	}
}
