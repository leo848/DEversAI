import { z } from 'zod';
import { GeminiInfo } from './geminiTypes';

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
	nearest_neighbors: z.record(
		z.string(),
		z.object({
			neighbors: z.array(z.number().int().nonnegative()),
			distances: z.array(z.number().finite())
		})
	),
	gemini_info: z.optional(GeminiInfo)
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

export const GeminiColumnResponse = z.object({
	column: z.array(z.union([z.number(), z.string()]).nullable())
});
export type GeminiColumnResponse = z.infer<typeof GeminiColumnResponse>;

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
		token_input: z.array(z.number().int()),
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

export const BirthyearRequest = z.object({
	first_name: z.string(),
	last_name: z.string().optional(),
	day: z.string().optional()
})
export type BirthyearRequest = z.infer<typeof BirthyearRequest>;

export const BirthyearResponse = z.object({
	year_data: z.record(z.coerce.number(), z.number()),
	decade_results: z.record(z.coerce.number(), z.number()),
	stats: z.object({
		mean: z.number(),
		mode: z.number(),
		std: z.number(),
		skew: z.number(),
	}),
	prob_sum: z.number(),
	discarded_prob_ratio: z.number(),
})
export type BirthyearResponse = z.infer<typeof BirthyearResponse>;

export const ForcedRequest = z.object({
	token_input: z.array(z.number().int()),
});
export type ForcedRequest = z.infer<typeof ForcedRequest>;

export const ForcedResponse = z.object({
	total_logprob: z.number(),
	steps: z.array(z.object({
		logit: z.number(),
		k: z.number().int(),
		alternatives: z.array(z.object({
			token_id: z.number().int(),
			logit: z.number(),
		})),
	}))
})
export type ForcedResponse = z.infer<typeof ForcedResponse>;
