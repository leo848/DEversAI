import { Token } from './token';
import { assert } from '$lib/util/typed';
import { chunksExact } from '$lib/util/array';
import { LinkedList } from '$lib/util/linkedList';

export interface BiSplit<T = Token> {
	left: T;
	right: T;
}

export interface MergeRule extends BiSplit {
	result: Token;
}

export class Vocabulary {
	mergeRules: MergeRule[];
	tokens: Token[];
	displaySet: Map<string, Token>;

	constructor(mergeRules: [number, number][]) {
		this.tokens = [];
		this.mergeRules = [];
		this.displaySet = new Map();

		while (this.tokens.length < 256) {
			const token = this.mintByteToken();
			token.composition = null;
		}
		for (const [leftIndex, rightIndex] of mergeRules) {
			assert(
				leftIndex < this.tokens.length && rightIndex < this.tokens.length,
				'Merge rule on unknown token'
			);

			const [left, right] = [leftIndex, rightIndex].map((index) => this.tokens[index]);
			const token = this.mintMergedToken(left, right);
			token.composition = { left, right };
			left.children.left.push(token);
			right.children.right.push(token);

			this.mergeRules.push({
				left,
				right,
				result: token
			});
		}
	}

	static fromBase64(base64: string): Vocabulary {
		// Function to decode a Python base64-encoded string and convert to Uint16Array
		function base64ToUint16Array(encodedStr: string) {
			// Decode the base64 string to raw binary data
			const binaryStr = atob(encodedStr);

			// Create a Uint8Array from the binary string
			const rawBytes = new Uint8Array(binaryStr.length);
			for (let i = 0; i < binaryStr.length; i++) {
				rawBytes[i] = binaryStr.charCodeAt(i);
			}

			// Prepare a Uint16Array with twice fewer elements (2 bytes per element)
			const uint16Array = new Uint16Array(rawBytes.length / 2);

			// Combine each pair of bytes into a Uint16 element
			for (let i = 0; i < uint16Array.length; i++) {
				const hi = rawBytes[i * 2]; // High byte
				const lo = rawBytes[i * 2 + 1]; // Low byte
				uint16Array[i] = (hi << 8) | lo; // Combine hi and lo into uint16
			}

			return uint16Array;
		}
		const tokenPairs = chunksExact([...base64ToUint16Array(base64)], 2);
		return new Vocabulary(tokenPairs);
	}

	mintByteToken(): Token {
		const token = new Token(this.tokens.length, new Uint8Array([this.tokens.length]), this);
		this.tokens.push(token);
		this.displaySet.set(token.toString(), token);
		return token;
	}

	mintMergedToken(left: Token, right: Token): Token {
		const token = new Token(this.tokens.length, mergeUintArrays(left.value, right.value), this);
		this.tokens.push(token);
		this.displaySet.set(token.toString(), token);
		return token;
	}

	tokenize(input: string, options?: { lastAppliedMergeRule?: number }) {
		const lastAppliedMergeRule = options?.lastAppliedMergeRule ?? Infinity;

		const bytes = new TextEncoder().encode(input);
		const tokenList: LinkedList<number> = LinkedList.fromIterable(bytes);

		const reverseMergeRules: Record<string, number> = {};
		for (const rule of this.mergeRules) {
			reverseMergeRules[`${rule.left.id()} ${rule.right.id()}`] = rule.result.id();
		}

		let firstApplicableRule = Infinity;
		while (true) {
			firstApplicableRule = Infinity;
			for (let listNode = tokenList.head(); listNode != null; listNode = listNode.next) {
				if (listNode.next != null) {
					firstApplicableRule = Math.min(
						firstApplicableRule,
						reverseMergeRules[`${listNode.value} ${listNode.next!.value}`] ?? Infinity
					);
				}
			}
			if (firstApplicableRule == Infinity) break;
			if (firstApplicableRule > lastAppliedMergeRule) break;

			const rule = this.mergeRules[firstApplicableRule - 256];

			if (tokenList.size() < 2) {
				break;
			}

			for (let listNode = tokenList.head(); listNode != null; listNode = listNode.next) {
				if (listNode.next == null) {
					break;
				}
				if (listNode.value == rule.left.id() && listNode.next!.value == rule.right.id()) {
					listNode.value = rule.result.id();
					listNode.next!.remove();
				}
			}

			let debugString = '';
			tokenList.forEach((t) => (debugString += ' ' + t));
		}

		const tokenIds = tokenList.toArray();
		return tokenIds.map((id) => this.tokens[id]);
	}
}

function mergeUintArrays(array1: Uint8Array, array2: Uint8Array): Uint8Array {
	const array = new Uint8Array(array1.length + array2.length);
	array.set(array1, 0);
	array.set(array2, array1.length);
	return array;
}
