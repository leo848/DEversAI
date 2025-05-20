export const models = {
	"1": {
		vocab: "german50000",
	},
	"-fw2": {
		vocab: "fineweb2",
	},
	"-fw2-laws1": {
		vocab: "fineweb2",
	},
	"-fw2-wikipedia1": {
		vocab: "fineweb2",
	}
} as const;

export type ModelId = keyof typeof models;
