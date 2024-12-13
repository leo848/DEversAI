import { Token } from "./token";
import { assert } from "$lib/util/typed";
import {chunks, chunksExact} from "$lib/util/array";

export interface BiSplit {
	left: Token,
	right: Token,
}

export interface MergeRule extends BiSplit {
	result: Token,
}

export class Vocabulary {
	mergeRules: MergeRule[]
	tokens: Token[]
	tokenValues: Uint8Array[]
	displayStrings: string[]
	unmergeRules: Map<Token, BiSplit | null>

	constructor(mergeRules: [number, number][]) {
		this.displayStrings = [];
		this.tokenValues = [];
		this.tokens = [];
		this.mergeRules = [];
		this.unmergeRules = new Map();

		let tokenIndex = 0;
		for (; tokenIndex < 256; tokenIndex++) {
			this.tokens.push(new Token(tokenIndex, this))
			this.tokenValues.push(new Uint8Array([tokenIndex]));
			this.displayStrings.push(displayToken(this.tokenValues[tokenIndex], tokenIndex));
			this.unmergeRules.set(this.tokens[tokenIndex], null);
		}
		for (const [left, right] of mergeRules) {
			assert(left < tokenIndex && right < tokenIndex, "Merge rule on unknown token");

			this.tokens.push(new Token(tokenIndex, this))
			this.mergeRules.push({
				left: this.tokens[left],
				right: this.tokens[right],
				result: this.tokens[tokenIndex],
			});
			this.unmergeRules.set(this.tokens[tokenIndex], { left: this.tokens[left], right: this.tokens[right] })
			this.tokenValues.push(mergeUintArrays(this.tokenValues[left], this.tokenValues[right]));
			this.displayStrings.push(displayToken(this.tokenValues[tokenIndex], tokenIndex));
			tokenIndex += 1;
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
}

function displayToken(value: Uint8Array, index: number): string {
	const decoder = new TextDecoder();
	try {
		return decoder.decode(value);
	} catch {
		return `<${index}>`
	}
}

function mergeUintArrays(array1: Uint8Array, array2: Uint8Array): Uint8Array {
	const array = new Uint8Array(array1.length + array2.length);
	array.set(array1, 0);
	array.set(array2, array1.length);
	return array;
}
