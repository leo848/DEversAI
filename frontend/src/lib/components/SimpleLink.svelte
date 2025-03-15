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
	class="underline underline-offset-2 hover:underline-offset-4 transition-all hover:text-black hover:font-bold active:text-gray-200"
>
	<slot>{href}</slot>
</a>
