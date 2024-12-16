## Running locally

required setup:
```bash
- install typescript if you don't have it:  sudo npm install -g typescript
- install VS Code extension 'Svelte for VS Code'
- change etc hosts file with the following ssh command: echo localhost www.wekiwi.de" | sudo tee -a /etc/hosts
    this re-routes url calls for www.wekiwi.de to localhost. 
```
## Using the Example Vite Config

To use the example Vite configuration for development or customization:

1. Copy the `vite.config.example.ts` file.
2. Rename it to `vite.config.ts`.
3. Update the placeholders with your project-specific details.

## 

To run in dev mode:

```bash
npm install
nvm use node # this command is only necessary if several node versions are installed on your computer
npm run dev -- --host=localhost # You might want to use the actual ip adress if this does not work
```

To build and start in prod mode:

```bash
npm run build
npm run preview
```

## STANDARDS:
```
- Layout mit Tailwind CSS und design tokens (primary etc. siehe wekiwi_theme) -> Skeleton UI
- Keine neuen Dependencies ohne Rücksprache.
- Keine Komponenten in den Routes benutzen, es sei denn, diese werden NUR für diese Route benutzt. Sonst unter $lib ablegen
- Keine Stores, State von oben nach unten oder über Routes, wenn es geht mit searchParams, props und reactive statements arebeiten
- Mehr als 3-Fach verschachtelte Funktionen und Abfragen vermeiden
```


## READ:
```
- https://joyofcode.xyz/sveltekit-data-flow
- https://khromov.se/the-comprehensive-guide-to-locals-in-sveltekit/
- https://svelte.dev/examples/hello-world
- https://www.youtube.com/watch?v=MaF8kRbHbi0
- https://www.sveltelab.dev/
- https://svelte.dev/examples/hello-world
- https://docs.directus.io/blog/getting-started-directus-sveltekit.html
- https://directus.io/tv/stack-up/sveltekit
```