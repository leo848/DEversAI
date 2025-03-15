<script lang="ts">
	import { Gradient } from '$lib/util/color';
</script>

<a
	class="deversai-logo display-block group m-4 inline-block w-[444px] rounded-2xl border border-4 border-gray-200 p-8 text-left text-white transition-all hover:scale-105"
	href="/"
	style:background={Gradient.Viridis.reverse().css('-45deg')}
>
	<div class="group-hover:rotate-x-50 group-hover:rotate-x-15 text-4xl font-bold transition-all">
		DEversAI
	</div>
	<div class="text-2xl">
		Training und Visualisierung<br />
		deutsch lokalisierter<br />
		direktionalkomplementärer LLMs
	</div>
</a>
