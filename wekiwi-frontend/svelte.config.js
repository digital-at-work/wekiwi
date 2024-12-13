import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import adapter from '@sveltejs/adapter-node';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: [vitePreprocess()],
	kit: {
		// see for deploying to nodejs https://kit.svelte.dev/docs/adapter-node
		adapter: adapter({
			precompress: true
		}),
	},
	vitePlugin: {
		// set to true for defaults or customize with object
		inspector:
		{
		  toggleKeyCombo: 'meta-shift',
		  showToggleButton: 'always',
		  toggleButtonPos: 'bottom-right'
		}
	}
};

export default config;
