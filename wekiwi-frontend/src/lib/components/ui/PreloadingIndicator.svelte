<script>
	import { onMount } from 'svelte';
	let p = 0;
	let visible = false;
	onMount(() => {
		visible = true;
		function next() {
			p += 0.1;
			const remaining = 1 - p;
			if (remaining > 0.15) setTimeout(next, 500 / remaining);
		}
		setTimeout(next, 250);
	});
</script>

{#if visible}
	<div class="progress-container">
		<div class="progress" style="width: {p * 100}%" />
	</div>
{/if}

{#if p >= 0.4}
	<div class="fade" />
{/if}

<style>
	.progress-container {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 4px;
		z-index: 999;
	}

	.progress {
		position: absolute;
		left: 0;
		top: 0;
		height: 100%;
		background-color: #209810;
		transition: width 0.4s;
	}

	.fade {
		position: fixed;
		width: 100%;
		height: 100%;
		background-color: rgba(255, 255, 255, 0.3);
		pointer-events: none;
		z-index: 998;
		animation: fade 0.4s;
	}

	@keyframes fade {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}
</style>



<!-- Svg Animation -->
<!-- <script>
let interval;

let rotation = 0;
let rotating = false;

function toggleRotation() {
	if (rotating) {
		clearInterval(interval);
	} else {
		interval = setInterval(() => {
			rotation += 1;
		}, 1);
	}
	rotating = !rotating;
}
</script>

<button on:click={toggleRotation}>
{rotating ? 'Stop Rotation' : 'Start Rotation'}
</button>

<svg viewBox="0 0 100 100" style="transform: rotate({rotation}deg);">
<rect x="25" y="25" width="50" height="50" fill="blue"/>
</svg>

<style>
svg {
	width: 200px;
	height: 200px;
	border: 1px solid black;
	margin-top: 10px;
}
</style> -->
