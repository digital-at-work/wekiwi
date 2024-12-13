
import type { CustomThemeConfig } from '@skeletonlabs/tw-plugin';

function hexToRgb(hex: string): [number, number, number] {
    hex = hex.replace(/^#/, '');
    return [
        parseInt(hex.substring(0, 2), 16),
        parseInt(hex.substring(2, 4), 16),
        parseInt(hex.substring(4, 6), 16)
    ];
}

function adjustLightness([r, g, b]: [number, number, number], percentage: number): [number, number, number] {
    const amount = Math.round(2.55 * percentage); 
    return [
        Math.min(255, Math.max(0, r + amount)),
        Math.min(255, Math.max(0, g + amount)),
        Math.min(255, Math.max(0, b + amount))
    ];
}

function generateShade(baseHex: string, percentage: number): string {
    const baseRgb: [number, number, number] = hexToRgb(baseHex);
    const adjustedRgb = adjustLightness(baseRgb, percentage);
    return `${adjustedRgb[0]} ${adjustedRgb[1]} ${adjustedRgb[2]}`;
}

export const baseColor = '#209810';

export const wekiwi_theme: CustomThemeConfig = {
    name: 'wekiwi_theme',
    properties: {
		// =~= Theme Properties =~=
		"--theme-font-family-base": `system-ui`,
		"--theme-font-family-heading": `system-ui`,
		"--theme-font-color-base": "var(--color-secondary-800)",
		"--theme-font-color-dark": "255 255 255",
		"--theme-rounded-base": "9px",
		"--theme-rounded-container": "8px",
		"--theme-border-base": "1px",
		// =~= Theme On-X Colors =~=
		"--on-primary": "255 255 255",
		"--on-secondary": "255 255 255",
		"--on-tertiary": "0 0 0",
		"--on-success": "var(--color-secondary-900)",
		"--on-warning": "var(--color-secondary-900)",
		"--on-error": "255 255 255",
		"--on-surface": "0 0 0",
		// =~= Theme Colors  =~=
		// primary | #2c8820 
		"--color-primary-50": `${generateShade(baseColor, 50)}`,
		"--color-primary-100": `${generateShade(baseColor, 40)}`,
		"--color-primary-200": `${generateShade(baseColor, 30)}`,
		"--color-primary-300": `${generateShade(baseColor, 20)}`,
		"--color-primary-400": `${generateShade(baseColor, 0)}`,
		"--color-primary-500": `${generateShade(baseColor, 0)}`,
		"--color-primary-600": `${generateShade(baseColor, -10)}`,
		"--color-primary-700": `${generateShade(baseColor, -20)}`,
		"--color-primary-800": `${generateShade(baseColor, -30)}`,
		"--color-primary-900": `${generateShade(baseColor, -40)}`,
		// secondary | #5e5c64 
		"--color-secondary-50": "231 231 232", // #e7e7e8
		"--color-secondary-100": "223 222 224", // #dfdee0
		"--color-secondary-200": "215 214 216", // #d7d6d8
		"--color-secondary-300": "191 190 193", // #bfbec1
		"--color-secondary-400": "142 141 147", // #8e8d93
		"--color-secondary-500": "94 92 100", // #5e5c64
		"--color-secondary-600": "85 83 90", // #55535a
		"--color-secondary-700": "71 69 75", // #47454b
		"--color-secondary-800": "56 55 60", // #38373c
		"--color-secondary-900": "46 45 49", // #2e2d31
		// tertiary | #cccccc 
		"--color-tertiary-50": "247 247 247", // #f7f7f7
		"--color-tertiary-100": "245 245 245", // #f5f5f5
		"--color-tertiary-200": "242 242 242", // #f2f2f2
		"--color-tertiary-300": "235 235 235", // #ebebeb
		"--color-tertiary-400": "219 219 219", // #dbdbdb
		"--color-tertiary-500": "204 204 204", // #cccccc
		"--color-tertiary-600": "184 184 184", // #b8b8b8
		"--color-tertiary-700": "153 153 153", // #999999
		"--color-tertiary-800": "122 122 122", // #7a7a7a
		"--color-tertiary-900": "100 100 100", // #646464
		// success | #84cc16 
		"--color-success-50": "237 247 220", // #edf7dc
		"--color-success-100": "230 245 208", // #e6f5d0
		"--color-success-200": "224 242 197", // #e0f2c5
		"--color-success-300": "206 235 162", // #ceeba2
		"--color-success-400": "169 219 92", // #a9db5c
		"--color-success-500": "132 204 22", // #84cc16
		"--color-success-600": "119 184 20", // #77b814
		"--color-success-700": "99 153 17", // #639911
		"--color-success-800": "79 122 13", // #4f7a0d
		"--color-success-900": "65 100 11", // #41640b
		// warning | #EAB308 
		"--color-warning-50": "252 244 218", // #fcf4da
		"--color-warning-100": "251 240 206", // #fbf0ce
		"--color-warning-200": "250 236 193", // #faecc1
		"--color-warning-300": "247 225 156", // #f7e19c
		"--color-warning-400": "240 202 82", // #f0ca52
		"--color-warning-500": "234 179 8", // #EAB308
		"--color-warning-600": "211 161 7", // #d3a107
		"--color-warning-700": "176 134 6", // #b08606
		"--color-warning-800": "140 107 5", // #8c6b05
		"--color-warning-900": "115 88 4", // #735804
		// error | #c01c28 
		"--color-error-50": "247 226 228", // #f7e2e4
		"--color-error-100": "244 217 218", // #f4d9da
		"--color-error-200": "242 207 209", // #f2cfd1
		"--color-error-300": "234 178 182", // #eab2b6
		"--color-error-400": "218 121 127", // #da797f
		"--color-error-500": "202 63 72", // #ca3f48
		"--color-error-600": "182 57 65", // #b63941
		"--color-error-700": "152 47 54", // #982f36
		"--color-error-800": "121 38 43", // #79262b
		"--color-error-900": "99 31 35", // #631f23
		// surface | #dddddd 
		"--color-surface-50": "250 250 250", // #fafafa
		"--color-surface-100": "248 248 248", // #f8f8f8
		"--color-surface-200": "247 247 247", // #f7f7f7
		"--color-surface-300": "241 241 241", // #f1f1f1
		"--color-surface-400": "231 231 231", // #e7e7e7
		"--color-surface-500": "221 221 221", // #dddddd
		"--color-surface-600": "199 199 199", // #c7c7c7
		"--color-surface-700": "166 166 166", // #a6a6a6
		"--color-surface-800": "133 133 133", // #858585
		"--color-surface-900": "108 108 108", // #6c6c6c
		
	}
}