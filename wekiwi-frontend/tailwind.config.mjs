import { join } from 'path';
import forms from '@tailwindcss/forms';
import typography from '@tailwindcss/typography';
import { skeleton } from '@skeletonlabs/tw-plugin';
import { wekiwi_theme } from './themes.ts';

const config = {
    darkMode: 'class',
    content: [
        './src/**/*.{html,js,svelte,ts}',
        join(require.resolve(
            '@skeletonlabs/skeleton'),
            '../**/*.{html,js,svelte,ts}'
        )
    ],
    /* corePlugins: {
        preflight: false,  // Disable Tailwind's preflight styles
    }, */
    plugins: [
        // https://www.skeleton.dev/elements/forms
        forms,
        typography,
        // Append the Skeleton plugin (after other plugins)
        // https://www.skeleton.dev/docs/themes
        skeleton({
            themes: {
                custom: [
                    wekiwi_theme
                ]
            }
        })
    ],
    theme: {
        extend: {
            typography: (theme) => ({
                DEFAULT: {
                    css: {
                        lineHeight: '1.3',
                        'ul, ol': {
                            lineHeight: '1.2',  // Lists in prose
                        
                        },
                    },
                },
            }),
        },
    },
};

export default config;
