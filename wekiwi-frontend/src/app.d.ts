import type { DirectusClient, AuthenticationClient, RestClient } from "@directus/sdk";
import type { CustomDirectusTypes } from '$lib/directus/directus.types'

// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare global {
	namespace App {
		interface Locals {
			user: {
				id: string;
				circles: Array<{
					name: string;
					id: string;
				}>;
				token?: string;
			},
			directusInstance: DirectusClient<CustomDirectusTypes> & AuthenticationClient<CustomDirectusTypes> & RestClient<CustomDirectusTypes>;
		}
		interface PageState {
			contentCreate?: any;
			contentSelect?: any;
		}
		interface PageData {
			flash?: { type: 'success' | 'error' | 'warning' | 'info'; message: string, timeout?: number };
		}
		// interface Error {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
