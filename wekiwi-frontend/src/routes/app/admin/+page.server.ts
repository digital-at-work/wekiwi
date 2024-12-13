// import type { PageServerLoad } from './$types';

// import { setFlash } from 'sveltekit-flash-message/server';


// export const load: PageServerLoad = async ({ locals, url, params, setHeaders }) => {

//     // get all circles the user is admin in
//     // const circles = await event.locals.directusInstance.request(readItems('circles', {
//     //     filter: {
//     //         'user_circle': { 'role': { '_eq': 'admin' } }
//     //     },
//     //     fields: ['circle_id', 'circle_name', circle_avatar, 'user_created', 'description', 'date_created']
//     // }));

//     return {
//         // circles,
//     };
// };


// export const actions = {
// 	updateCircle: async ({ locals, params, url, request, cookies }) => {

//         try{

// 			setFlash({ type: 'success', message: 'Circle erfolgreich geändert.' }, cookies);
// 		} catch (err) {
// 			setFlash({ type: 'error', message: `Fehler beim updaten: ${(err as Error).message}` }, cookies);
// 		}
// 	},
//     createCircle: async ({ locals, params, url, request, cookies }) => {

//         try{

// 			setFlash({ type: 'success', message: 'Circle erfolgreich erstellt.' }, cookies);
// 		} catch (err) {
// 			setFlash({ type: 'error', message: `Fehler beim erstellen: ${(err as Error).message}` }, cookies);
// 		}
// 	}
// };
