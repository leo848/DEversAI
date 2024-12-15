import { assert } from '$lib/util/typed';
import { Vocabulary, type BiSplit } from './vocabulary';

export type TokenHistory = {
	name: string;
	id: number;
	children?: TokenHistory[];
};

export class Token {
	index: number;

	value: Uint8Array;
	displayString: string;
	composition: BiSplit | null;
	children: BiSplit<Token[]>;

	vocab?: Vocabulary;

	constructor(index: number, value: Uint8Array, vocab?: Vocabulary) {
		if (vocab) {
			assert(!vocab.tokens[index], `Token already exists: <${index}>`);
		}
		this.index = index;
		this.value = value;
		this.vocab = vocab;
		this.displayString = displayToken(this.value, this.index);
		this.composition = null;
		this.children = { left: [], right: [] };
	}

	id() {
		return this.index;
	}

	toString() {
		return this.displayString;
	}

	toStringDebug() {
		return this.toString().replaceAll(' ', '⎵').replaceAll('\n', '\\n');
	}

	historyTree(): TokenHistory {
		assert(this.vocab, 'No vocabulary for token');
		const result = this.composition;
		const children =
			result == null ? undefined : [result.left.historyTree(), result.right.historyTree()];
		return {
			name: this.toStringDebug(),
			id: this.index,
			children
		};
	}
}

function displayToken(value: Uint8Array, index: number): string {
	const decoder = new TextDecoder();
	try {
		return decoder.decode(value);
	} catch {
		return `<${index}>`;
	}
}
