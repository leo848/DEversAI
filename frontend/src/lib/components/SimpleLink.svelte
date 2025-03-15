<script lang="ts">
	export let href: string;
	export let target: string = '_self';
	export let tabindex: number = 0;
</script>

<a
	{href}
	{target}
	{tabindex}
	on:click
	class="underline underline-offset-2 transition-all hover:font-bold hover:text-black hover:underline-offset-4 active:text-gray-200"
>
	<slot>{href}</slot>
</a>
