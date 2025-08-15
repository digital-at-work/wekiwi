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
                // Custom variant for content on primary color backgrounds
                primary: {
                    css: {
                        '--tw-prose-body': theme('colors.white'),
                        '--tw-prose-headings': theme('colors.white'),
                        '--tw-prose-lead': theme('colors.white'),
                        '--tw-prose-links': theme('colors.white'),
                        '--tw-prose-bold': theme('colors.white'),
                        '--tw-prose-counters': theme('colors.white'),
                        '--tw-prose-bullets': theme('colors.white'),
                        '--tw-prose-hr': 'rgb(255 255 255 / 0.4)',
                        '--tw-prose-quotes': theme('colors.white'),
                        '--tw-prose-quote-borders': 'rgb(var(--color-primary-300))',
                        '--tw-prose-captions': 'rgb(255 255 255 / 0.8)',
                        '--tw-prose-code': theme('colors.white'),
                        '--tw-prose-pre-code': theme('colors.white'),
                        '--tw-prose-pre-bg': 'rgb(0 0 0 / 0.2)',
                        '--tw-prose-th-borders': 'rgb(var(--color-primary-300))',
                        '--tw-prose-td-borders': 'rgb(var(--color-primary-200))',
                    },
                },
            }),
        },
    },
};

export default config;
