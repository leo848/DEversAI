import { z } from "zod";

export const TokenInfo = z.object({
	id: z.number(),
	examples: z.array(z.tuple([z.string(), z.string()]))
});
export type TokenInfo = z.infer<typeof TokenInfo>;
