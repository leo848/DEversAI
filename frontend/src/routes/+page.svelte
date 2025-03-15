<script lang="ts">
	const title =
		'DEversAI: Training und Visualisierung deutsch lokalisierter direktionalkomplementärer LLMs';
	const showNew = true;
	const shortDescOld = `Large Language Models (LLMs) sind spätestens seit ChatGPT Teil des Alltags geworden. In diesem Projekt trainiere ich selbst LLM-Basismodelle mit PyTorch über die LLM-HOSTed-Infrastruktur der Hochschule Stralsund, jedoch nicht nur wie bisher mit dem Ziel, das nächste Token vorherzusagen (GPT), sondern primär, das vorherige zu inferieren - "Direktionalkomplementarität". Als Datengrundlage werden deutsche Textkorpora gesammelt und verwendet. Ich stelle die Hypothese auf, dass es signifikante Unterschiede zwischen dem Training in Rückwärts- und in Vorwärtsrichtung gibt, und vergleiche diese empirisch auf Basis aktueller Metriken. Zudem wird eine interaktive App entwickelt, in der alle trainierten Modelle ausprobiert, verglichen, evaluiert und visualisiert werden können. Weiterführende zu verfolgende Ansätze liegen im Fine-Tuning der Modelle auf Teilgebiete der deutschen Sprache anhand von Bundestagsreden, Gesetzen oder Literatur, sowie einem Vergleich zwischen Transformer und Mamba/S4.`;
	const shortDescNew = `Im Projekt DEversAI untersuche ich, ob KI-Sprachmodelle besser funktionieren, wenn sie Texte vorwärts oder rückwärts verarbeiten. Dazu habe ich zwei KI-Modelle auf Deutsch trainiert: eines erzeugt Text vorwärts, das andere rückwärts. Ziel ist es, herauszufinden, ob Rückwärts-Modelle neue Möglichkeiten eröffnen und ob Erkenntnisse aus englischer Forschung im Deutschen gelten.

Die Ergebnisse sind vielversprechend. Das Vorwärts-Modell liefert präzisere Vorhersagen, aber das neue Rückwärts-Modell kann auch gute Texte vom Ende aus verfassen - so bei Kochrezepten, Gesetzen und Bundestagsreden. Eigene komplexe Visualisierungen der Modellstrukturen zeigen, dass beide sprachliche Muster lernen, aber sich in Aufbau und Ausgabe unterscheiden.

In der entwickelten interaktiven Webanwendung kann die KI ausprobiert und getestet werden. Die Resultate belegen, dass Textverarbeitungsrichtung einen wesentlichen Einfluss auf die Leistungsfähigkeit von KI in der Sprachverarbeitung hat.`;

	const shortDesc = $derived(showNew ? shortDescNew : shortDescOld);
</script>

<div class="container min-h-[100vh] min-w-full bg-slate-100 py-8">
	<div class="prose mx-auto rounded-xl bg-white p-8 shadow-lg">
		<h1>{title}</h1>
		{#each shortDesc.split('\n\n') as par}
			<p>{par}</p>
		{/each}
	</div>
</div>
