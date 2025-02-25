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
