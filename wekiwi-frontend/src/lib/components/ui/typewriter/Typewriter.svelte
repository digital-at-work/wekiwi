<script lang="ts">
	import { onMount } from 'svelte';

	export let sentences = [''];

	let currentSentence: string;
	let position = 0;
	let cursorBlink = true;
	let blinkInterval: NodeJS.Timeout;

	function randomDelay(min = 60, max = 120) {
		return Math.random() * (max - min) + min;
	}

	function startCursorBlink() {
		cursorBlink = true; // Start with cursor visible for blinking
		clearInterval(blinkInterval); // Clear any previous interval to avoid duplicates
		blinkInterval = setInterval(() => {
			cursorBlink = !cursorBlink; // Toggle cursor visibility for blinking
		}, 500); // Set the blinking interval to 500ms
	}

	function stopCursorBlink() {
		clearInterval(blinkInterval); // Stop the blinking interval
		cursorBlink = true; // Keep the cursor visible when not blinking
	}

	function typeSentence() {
		if (position < currentSentence.length) {
			stopCursorBlink(); // Ensure cursor is visible and not blinking while typing
			position++;
			const delay = randomDelay();
			setTimeout(() => {
				if (position < currentSentence.length) {
					typeSentence();
				} else {
					// After the last letter is added, start blinking
					startCursorBlink();
					setTimeout(deleteSentence, 2000); // Delay before starting to remove text
				}
			}, delay);
		}
	}

	function deleteSentence() {
		if (position > 0) {
			position--;
			if (position === 0) {
				// Once deletion is about to start, ensure cursor blinks
				startCursorBlink();
				setTimeout(() => {
					// Pick a new sentence randomly and start typing it after a brief pause
					currentSentence = sentences[Math.floor(Math.random() * sentences.length)];
					typeSentence();
				}, 1000);
			} else {
				setTimeout(deleteSentence, randomDelay(40, 80));
			}
		}
	}

	onMount(() => {
		currentSentence = sentences[Math.floor(Math.random() * sentences.length)];
		typeSentence();
	});
</script>

<h1 class="text-2xl md:text-4xl">
	{#if currentSentence}
		<div>
			{currentSentence?.substring(0, position)}<span
				class="cursor"
				style="opacity: {cursorBlink ? '1' : '0'}">|</span
			>
		</div>
	{/if}
</h1>
