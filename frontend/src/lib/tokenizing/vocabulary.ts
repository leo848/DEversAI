import { Token } from './token';
import { assert } from '$lib/util/typed';
import { chunks, chunksExact } from '$lib/util/array';

export interface BiSplit {
	left: Token;
	right: Token;
}

export interface MergeRule extends BiSplit {
	result: Token;
}

export class Vocabulary {
	mergeRules: MergeRule[];
	tokens: Token[];

	constructor(mergeRules: [number, number][]) {
		this.tokens = [];
		this.mergeRules = [];

		while (this.tokens.length < 256) {
			const token = this.mintByteToken();
			token.composition = null;
		}
		for (const [leftIndex, rightIndex] of mergeRules) {
			assert(leftIndex < this.tokens.length && rightIndex < this.tokens.length, 'Merge rule on unknown token');
			
			const [left, right] = [leftIndex, rightIndex].map(index => this.tokens[index]);
			const token = this.mintMergedToken(left, right);
			token.composition = { left, right };

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
		const token = new Token(
			this.tokens.length,
			new Uint8Array([this.tokens.length]),
			this
		)
		this.tokens.push(token);
		return token;
	}

	mintMergedToken(left: Token, right: Token): Token {
		const token = new Token(
			this.tokens.length,
			mergeUintArrays(left.value, right.value),
			this
		);
		this.tokens.push(token);
		return token;
	}
}

function mergeUintArrays(array1: Uint8Array, array2: Uint8Array): Uint8Array {
	const array = new Uint8Array(array1.length + array2.length);
	array.set(array1, 0);
	array.set(array2, array1.length);
	return array;
}
