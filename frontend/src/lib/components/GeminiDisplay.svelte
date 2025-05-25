<script lang="ts">
	import type {GeminiInfo} from '$lib/backend/geminiTypes';
	import Icon from '@iconify/svelte';
	import MorphologyBlock from './MorphologyBlock.svelte';

	const {
		info
	}: {
		info: GeminiInfo
	} = $props();
</script>


<div class="flex flex-col gap-4">
  <div class="p-4 flex flex-row gap-4 rounded-xl bg-warn-200">
      <Icon icon="ep:warn-triangle-filled" height="3em" />
      <div>
          Die folgenden Informationen stammen von <b>Gemini Flash 2.0</b> und wurden nicht verifiziert.
      </div>
  </div>

  <div class="w-full mx-auto bg-white rounded-xl overflow-hidden border border-gray-200">
    <div class="p-6 space-y-6">
      <div class="flex items-center space-x-4">
        <div class="text-3xl">{info.emoji}</div>
        <div>
          <h2 class="text-xl font-bold text-gray-900">{info.token}</h2>
          <p class="text-sm text-gray-600">{info.kurz_definition}</p>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4 text-sm text-gray-800">
        <div><span class="font-semibold">Wortart:</span> {info.wortart}</div>
        <div><span class="font-semibold">Vollständig:</span> {info.ist_komplett_vollständig ? 'Ja' : 'Nein'}</div>
        <div><span class="font-semibold">Seit:</span> {info.verwendung_seit_jahr}</div>
        <div><span class="font-semibold">Kategorie:</span> {info.kategorie}</div>
        <div><span class="font-semibold">Silben:</span> {info.silbenanzahl}</div>
        <div><span class="font-semibold">IPA:</span> <code>{info.ipa_lautschrift}</code></div>
        {#if info.typische_position_im_wort}
          <div><span class="font-semibold">Position:</span> {info.typische_position_im_wort}</div>
        {/if}
        {#if info.lemma && info.lemma != info.token}
          <div><span class="font-semibold">Lemma:</span> {info.lemma}</div>
        {/if}
      </div>

      {#if info.komposita_teile}
        <div>
          <h3 class="font-semibold text-gray-700">Komposita:</h3>
          <div class="flex flex-wrap gap-2 mt-1">
            {#each info.komposita_teile as teil}
              <span class="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm">{teil}</span>
            {/each}
          </div>
        </div>
      {/if}

      <!-- Morphologies -->
      {#if info.substantiv_morphologie}
        <MorphologyBlock title="Substantiv-Morphologie" entries={[
          ['Abstrakt/Konkret', info.substantiv_morphologie.abstrakt_oder_konkret],
          ['Genus', info.substantiv_morphologie.genus],
          ['Soziales Geschlecht', info.substantiv_morphologie.soziales_geschlecht],
          ['Numerus', info.substantiv_morphologie.numerus],
          ['Kasus', info.substantiv_morphologie.kasus],
          ['Deklinationstyp', info.substantiv_morphologie.deklinationstyp],
          ['Reguläres Suffix', info.substantiv_morphologie.reguläres_suffix ? 'Ja' : 'Nein'],
          ['Umlaut-Änderung', info.substantiv_morphologie.umlaut_änderung ? 'Ja' : 'Nein'],
          ['Stammänderung', info.substantiv_morphologie.unregelmäßige_stammänderung ? 'Ja' : 'Nein'],
          ['Trennbares Präfix', info.substantiv_morphologie.trennbares_präfix ? 'Ja' : 'Nein']
        ]} />
      {/if}

      {#if info.verb_morphologie}
        <MorphologyBlock title="Verb-Morphologie" entries={[
          ['Tempus', info.verb_morphologie.tempus],
          ['Modus', info.verb_morphologie.modus],
          ['Person', info.verb_morphologie.person],
          ['Numerus', info.verb_morphologie.numerus],
          ['Konjugationstyp', info.verb_morphologie.konjugationstyp]
        ]} />
      {/if}

      {#if info.adjektiv_morphologie}
        <MorphologyBlock title="Adjektiv-Morphologie" entries={[
          ['Steigerungsform', info.adjektiv_morphologie.steigerungsform],
          ['Deklinationstyp', info.adjektiv_morphologie.deklinationstyp],
          ['Numerus', info.adjektiv_morphologie.numerus],
          ['Kasus', info.adjektiv_morphologie.kasus],
          ['Genus', info.adjektiv_morphologie.genus],
          ['Endung', info.adjektiv_morphologie.endung],
          ['Reguläres Suffix', info.adjektiv_morphologie.reguläres_suffix ? 'Ja' : 'Nein'],
          ['Umlaut-Änderung', info.adjektiv_morphologie.umlaut_änderung ? 'Ja' : 'Nein'],
          ['Stammänderung', info.adjektiv_morphologie.unregelmäßige_stammänderung ? 'Ja' : 'Nein'],
          ['Trennbares Präfix', info.adjektiv_morphologie.trennbares_präfix ? 'Ja' : 'Nein']
        ]} />
      {/if}

      {#if info.pronomen_morphologie}
        <MorphologyBlock title="Pronomen-Morphologie" entries={[
          ['Typ', info.pronomen_morphologie.pronomen_typ],
          ['Numerus', info.pronomen_morphologie.numerus],
          ['Kasus', info.pronomen_morphologie.kasus]
        ]} />
      {/if}
    </div>
  </div>
</div>
