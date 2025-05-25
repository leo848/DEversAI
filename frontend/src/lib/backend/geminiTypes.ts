import { z } from 'zod';

export const GeminiInfo = z.object({
    id: z.number(),
    token: z.string(),
    emoji: z.string(),
    kurz_definition: z.string(),
    ist_komplett_vollständig: z.boolean(),
    wortart: z.enum(['Substantiv', 'Verb', 'Adjektiv', 'Adverb', 'Pronomen', 'Artikel', 'Präposition', 'Konjunktion', 'Partikel', 'Interjektion', 'Numeral', 'Determiner', 'Zeichen', 'Andere']),
    substantiv_morphologie: z.object({
        abstrakt_oder_konkret: z.enum(['Abstrakt', 'Konkret']),
        genus: z.enum(['maskulin', 'feminin', 'neutrum']),
        soziales_geschlecht: z.enum(['männlich', 'weiblich', 'nichtbinär']).nullish(),
        numerus: z.enum(['Singular', 'Plural', 'invariabel']),
        kasus: z.enum(['Nominativ', 'Genitiv', 'Dativ', 'Akkusativ']),
        deklinationstyp: z.enum(['stark', 'schwach', 'gemischt', 'unflektierbar']),
        reguläres_suffix: z.boolean(),
        umlaut_änderung: z.boolean(),
        unregelmäßige_stammänderung: z.boolean(),
        trennbares_präfix: z.boolean(),
    }).nullish(),
    verb_morphologie: z.object({
        tempus: z.enum(['Präsens', 'Präteritum', 'Perfekt', 'Plusquamperfekt', 'Futur I', 'Futur II', 'Partizip I', 'Partizip II']),
        modus: z.enum(['Indikativ', 'Konjunktiv I', 'Konjunktiv II', 'Imperativ']),
        person: z.enum(['erste Person', 'zweite Person', 'dritte Person', 'keine']),
        numerus: z.enum(['Singular', 'Plural', 'invariabel']).nullish(),
        konjugationstyp: z.enum(['regelmäßig', 'unregelmäßig', 'Modalverb', 'Hilfsverb']),
    }).nullish(),
    adjektiv_morphologie: z.object({
        steigerungsform: z.enum(['Positiv', 'Komparativ', 'Superlativ']),
        deklinationstyp: z.enum(['stark', 'schwach', 'gemischt', 'unflektierbar']),
        numerus: z.enum(['Singular', 'Plural', 'invariabel']).nullish(),
        kasus: z.enum(['Nominativ', 'Genitiv', 'Dativ', 'Akkusativ']).nullish(),
        genus: z.enum(['maskulin', 'feminin', 'neutrum']).nullish(),
        endung: z.string().nullish(),
        reguläres_suffix: z.boolean(),
        umlaut_änderung: z.boolean(),
        unregelmäßige_stammänderung: z.boolean(),
        trennbares_präfix: z.boolean(),
    }).nullish(),
    pronomen_morphologie: z.object({
        pronomen_typ: z.enum(['Personalpronomen', 'Possessivpronomen', 'Reflexivpronomen', 'Demonstrativpronomen', 'Relativpronomen', 'Interrogativpronomen', 'Indefinitpronomen', 'Reziprokpronomen']),
        numerus: z.enum(['Singular', 'Plural', 'invariabel']),
        kasus: z.enum(['Nominativ', 'Genitiv', 'Dativ', 'Akkusativ']),
    }).nullish(),
    typische_position_im_wort: z.enum(['Wortanfang', 'Wortende', 'Wortmitte', 'keine']).nullish(),
    verwendung_seit_jahr: z.number(),
    kategorie: z.enum(['Politik', 'Zeit', 'Sport', 'Geografisch', 'Gesellschaft/Familie', 'Eigenname', 'Corporate', 'Essen', 'Technisch', 'Gegenstand', 'Aktivität', 'Konzept', 'Andere']),
    lemma: z.string().nullish(),
    silbenanzahl: z.number(),
    ipa_lautschrift: z.string(),
    komposita_teile: z.array(z.string()).nullish()
});
export type GeminiInfo = z.infer<typeof GeminiInfo>;
