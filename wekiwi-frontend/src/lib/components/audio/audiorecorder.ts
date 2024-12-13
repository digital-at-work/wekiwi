// export function audioRecorder(node: any, { onStart, onStop }: { onStart: () => void, onStop: (audioBlob: Blob) => void }) {
//     let mediaRecorder: MediaRecorder | undefined;
//     let audioChunks: Blob[] = [];
//     let stream: MediaStream;

//     async function initRecorder() {
//         stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//         mediaRecorder = new MediaRecorder(stream);

//         mediaRecorder.ondataavailable = event => {
//             audioChunks.push(event.data);
//         };

//         mediaRecorder.onstop = () => {
//             const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
//             onStop(audioBlob);
//             audioChunks = [];
//         };
//     }

//     initRecorder();

//     return {
//         start() {
//             audioChunks = [];
//             mediaRecorder?.start();
//             onStart();
//         },
//         stop() {
//             mediaRecorder?.stop();
//         },
//         destroy() {
//             stream.getTracks().forEach(track => track.stop());
//         }
//     };
// }
