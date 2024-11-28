<script lang="ts">
	const title = "DEversAI: Training und Visualisierung deutsch lokalisierter direktionalkomplementärer LLMs"
	const shortDesc = `Large Language Models (LLMs) sind spätestens seit ChatGPT Teil des Alltags geworden. In diesem Projekt trainiere ich selbst LLM-Basismodelle mit PyTorch über die LLM-HOSTed-Infrastruktur der Hochschule Stralsund, jedoch nicht nur wie bisher mit dem Ziel, das nächste Token vorherzusagen (GPT), sondern primär, das vorherige zu inferieren - "Direktionalkomplementarität". Als Datengrundlage werden deutsche Textkorpora gesammelt und verwendet. Ich stelle die Hypothese auf, dass es signifikante Unterschiede zwischen dem Training in Rückwärts- und in Vorwärtsrichtung gibt, und vergleiche diese empirisch auf Basis aktueller Metriken. Zudem wird eine interaktive App entwickelt, in der alle trainierten Modelle ausprobiert, verglichen, evaluiert und visualisiert werden können. Weiterführende zu verfolgende Ansätze liegen im Fine-Tuning der Modelle auf Teilgebiete der deutschen Sprache anhand von Bundestagsreden, Gesetzen oder Literatur, sowie einem Vergleich zwischen Transformer und Mamba/S4.`
</script>

<div class="container py-8 bg-slate-100 min-w-full min-h-[100vh]">
	<div class="prose mx-auto shadow-lg rounded-xl p-8 bg-white">
		<h1>{title}</h1>
		<p>{shortDesc}</p>
	</div>
</div>
