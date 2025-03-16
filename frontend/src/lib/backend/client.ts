import type { Token } from '$lib/tokenizing/token';
import { assert } from '$lib/util/typed';
import { v4 as uuidv4 } from 'uuid';
import {
	InferenceConfig,
	InferenceRequest,
	InferenceResponse,
	LogitsResponse,
	TokenEmbeddings,
	TokenInfo,
	EmbeddingDimInfo
} from './types';

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
	httpsBase: string;
	wsUrl: string;
	embeddingCache: Record<string, TokenEmbeddings>;

	constructor({ base }: { base?: string } = {}) {
		this.embeddingCache = {};
		if (base) {
			this.httpsBase = `https://${base}/v0`;
			this.wsUrl = `wss://${base}/ws`;
		} else if (import.meta.env.PROD || import.meta.env.DEV) {
			const base = 'deversai.uber.space';
			this.httpsBase = `https://${base}/v0`;
			this.wsUrl = `wss://${base}/ws`;
		} else {
			throw new RangeError('invalid vite value');
		}
	}

	async getTokenInfo(token: Token): Promise<TokenInfo> {
		const apiPath = pathUtils.join(this.httpsBase, 'token', token.id().toString(), 'info');
		const response = await fetch(apiPath);
		const json = await response.json();
		const tokenInfo = await TokenInfo.safeParseAsync(json);
		if (tokenInfo.success) {
			return tokenInfo.data;
		} else {
			return Promise.reject('Could not parse response: ' + tokenInfo.error);
		}
	}

	async getEmbeddingDimInfo(modelName: string, dim: number): Promise<EmbeddingDimInfo> {
		const apiPath = pathUtils.join(this.httpsBase, 'embedding', modelName, dim.toString(), 'info');
		const response = await fetch(apiPath);
		const json = await response.json();
		const embeddingDimInfo = await EmbeddingDimInfo.safeParseAsync(json);
		if (embeddingDimInfo.success) {
			return embeddingDimInfo.data;
		} else {
			return Promise.reject('Could not parse response: ' + embeddingDimInfo.error);
		}
	}

	async getTokenEmbeddings(modelName: string): Promise<TokenEmbeddings> {
		const cached = this.embeddingCache[modelName];
		if (cached != null) {
			return cached;
		}
		const apiPath = pathUtils.join(this.httpsBase, 'tokens', modelName, 'embeddings');
		const response = await fetch(apiPath);
		const json = await response.json();
		console.log(json);
		const tokenEmbeddings = await TokenEmbeddings.safeParseAsync(json);
		if (tokenEmbeddings.success) {
			this.embeddingCache[modelName] = tokenEmbeddings.data;
			return tokenEmbeddings.data;
		} else {
			return Promise.reject('Could not parse response: ' + tokenEmbeddings.error);
		}
	}

	async modelLogits(modelName: string, tokens: Token[]): Promise<LogitsResponse> {
		const apiPath = pathUtils.join(this.httpsBase, 'model', modelName, 'logits');
		const response = await fetch(apiPath, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				token_input: tokens.map((t) => t.id())
			})
		});
		const json = await response.json();
		const logitsResponse = await LogitsResponse.safeParseAsync(json);
		if (logitsResponse.success) {
			return logitsResponse.data;
		} else {
			return Promise.reject('Could not parse response: ' + logitsResponse.error);
		}
	}

	async *autoregressiveInference(
		modelName: string,
		tokens: Token[],
		config: InferenceConfig = {},
		controller?: AbortController
	) {
		const ws = new WebSocket(this.wsUrl);
		const queue: string[] = [];
		let resolveMsg: ((value: string | PromiseLike<string>) => void) | null = null;

		ws.onmessage = (evt) => {
			if (controller?.signal.aborted) return ws.close();
			const message = evt.data;
			if (resolveMsg) {
				resolveMsg(message);
				resolveMsg = null;
			} else {
				queue.push(message);
			}
		};

		ws.onerror = (error) => {
			console.error('WS-Fehler: ', error);
		};

		ws.onclose = () => {
			console.log('WS-Verbindung geschlossen.');
		};

		const request: InferenceRequest = {
			request_id: uuidv4(),
			action: {
				type: 'autoregressiveInference',
				model_id: modelName,
				token_input: tokens.map((t) => t.id()),
				config: config
			}
		};

		ws.onopen = () => {
			ws.send(JSON.stringify(request));
		};

		try {
			while (!controller?.signal.aborted) {
				const message =
					queue.length > 0
						? queue.shift()!
						: await new Promise<string>((resolve) => (resolveMsg = resolve));

				const decoded = await InferenceResponse.safeParseAsync(JSON.parse(message));
				assert(decoded.success);

				yield decoded.data.tokens;

				if (decoded.data.done) {
					ws.close();
					return;
				}
			}
		} finally {
			ws.close();
		}
	}
}
