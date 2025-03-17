import { z } from 'zod';

export const TokenInfo = z.object({
	id: z.number(),
	examples: z.array(z.tuple([z.string(), z.string()])),
	embedding_768d: z.record(z.string(), z.array(z.number().finite())),
	occurrences: z.object({
		total: z.number(),
		tokens: z.record(
			z.coerce.number().nonnegative(),
			z.object({
				count_direct: z.number().nonnegative(),
				count_transitive: z.number().nonnegative()
			})
		)
	}),
	nearest_neighbors: z.object({
		causal1: z.record(
			z.string(),
			z.object({
				neighbors: z.array(z.number().int().nonnegative()),
				distances: z.array(z.number().int().nonnegative())
			})
		)
	})
});
export type TokenInfo = z.infer<typeof TokenInfo>;

export const EmbeddingDimInfo = z.object({
	dim: z.number(),
	token_values: z.array(z.number().finite())
});
export type EmbeddingDimInfo = z.infer<typeof EmbeddingDimInfo>;

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

export const InferenceConfig = z.object({
	num_tokens: z.number().int().optional(),
	temperature: z.number().min(0).max(5).optional(),
	top_k: z.number().int().optional(),
	synthetic_wait: z.number().int().nonnegative().optional()
});
export type InferenceConfig = z.infer<typeof InferenceConfig>;

export const InferenceRequest = z.object({
	request_id: z.string(),
	action: z.object({
		type: z.literal('autoregressiveInference'),
		model_id: z.string(),
		token_input: z.array(z.number()),
		config: InferenceConfig
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
