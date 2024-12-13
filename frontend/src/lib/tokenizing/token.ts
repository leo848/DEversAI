import { assert } from '$lib/util/typed';
import { Vocabulary } from './vocabulary';

export type TokenHistory = {
	name: string;
	id: number;
	children?: TokenHistory[];
};

export class Token {
	index: number;
	vocab?: Vocabulary;

	constructor(index: number, vocab?: Vocabulary) {
		if (vocab) {
			assert(!vocab.tokens[index], `Token already exists: <${index}>`);
		}
		this.index = index;
		this.vocab = vocab;
	}

	id() {
		return this.index;
	}

	toString() {
		if (this.vocab) {
			return this.vocab.displayStrings[this.index];
		} else {
			return `<${this.index}>`;
		}
	}

	toStringDebug() {
		return this.toString().replaceAll(' ', '⎵').replaceAll("\n", "\\n");
	}

	historyTree(): TokenHistory {
		assert(this.vocab, 'No vocabulary for token');
		const result = this.vocab.unmergeRules.get(this);
		const children =
			result == null ? undefined : [result.left.historyTree(), result.right.historyTree()];
		return {
			name: this.toStringDebug(),
			id: this.index,
			children
		};
	}
}
