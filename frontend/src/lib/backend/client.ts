import type { Token } from '$lib/tokenizing/token';
import { LogitsResponse, TokenEmbeddings, TokenInfo } from './types';

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
	embeddingCache: Record<string, TokenEmbeddings>;

	constructor({ base }: { base?: string } = {}) {
		this.embeddingCache = {};
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
			return Promise.reject('Could not parse response: ' + tokenInfo.error);
		}
	}

	async getTokenEmbeddings(modelName: string): Promise<TokenEmbeddings> {
		const cached = this.embeddingCache[modelName];
		if (cached != null) {
			return cached;
		}
		const apiPath = pathUtils.join(this.base, 'tokens', modelName, 'embeddings');
		const response = await fetch(apiPath);
		const json = await response.json();
		const tokenEmbeddings = await TokenEmbeddings.safeParseAsync(json);
		if (tokenEmbeddings.success) {
			this.embeddingCache[modelName] = tokenEmbeddings.data;
			return tokenEmbeddings.data;
		} else {
			return Promise.reject('Could not parse response: ' + tokenEmbeddings.error);
		}
	}

	async modelLogits(modelName: string, tokens: Token[]): Promise<LogitsResponse> {
		const apiPath = pathUtils.join(this.base, 'model', modelName, 'logits');
		const response = await fetch(apiPath, {
			method: "POST",
			body: JSON.stringify({
				token_input: tokens.map(t => t.id())
			})
		});
		const json = await response.json();
		const logitsResponse = await LogitsResponse.safeParseAsync(json);
		if (logitsResponse.success) {
			return logitsResponse.data;
		} else {
			return Promise.reject("Could not parse response: " + logitsResponse.error);
		}
	}
}
