import { z } from 'zod';

export const TokenInfo = z.object({
	id: z.number(),
	examples: z.array(z.tuple([z.string(), z.string()]))
});
export type TokenInfo = z.infer<typeof TokenInfo>;

export const TokenEmbeddings = z.object({
	tokenCount: z.number(),
	embeddings3D: z.array(z.tuple([z.number(), z.number(), z.number()])),
	embeddings2D: z.array(z.tuple([z.number(), z.number()]))
});
export type TokenEmbeddings = z.infer<typeof TokenEmbeddings>;

export const LogitsResponse = z.object({
	logits: z.array(z.number().finite())
});
export type LogitsResponse = z.infer<typeof LogitsResponse>;

export const InferenceRequest = z.object({
	request_id: z.string(),
	action: z.object({
		type: z.literal('autoregressiveInference'),
		model_id: z.string(),
		token_input: z.array(z.number())
	})
});
export type InferenceRequest = z.infer<typeof InferenceRequest>;

export const InferenceResponse = z.object({
	type: z.literal('autoregressiveInference'),
	request_id: z.string(),
	tokens: z.array(z.number()),
	done: z.optional(z.boolean())
});
export type InferenceResponse = z.infer<typeof InferenceResponse>;
