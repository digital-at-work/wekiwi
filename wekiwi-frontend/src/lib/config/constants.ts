export const MAX_FILE_SIZE = 5000000;
export const MAX_IMAGE_SIZE = 3000000;
export const MAX_LENGTH_SUBCONTENT = 200;
export const MAX_LENGTH_CONTENT = 100;
export const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
export const ACCEPTED_FILE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp", "application/pdf"];
export const PAGE_SIZE = 10;
export const FEED_CHECKMORE_TIMEOUT = 3000;
export const FEED_BUTTOM_THRESHOLD_LOADMORE_PX = 300;
export const DEFAULT_PLACEHOLDER_AVATAR = 'https://ui-avatars.com/api/?name='; // e.g. https://ui-avatars.com/api/?name=John+Doe
export const DEFAULT_EDITOR_TXT = ``;

// <div>
// <p><strong>Schreibe Deinen Beitrag:</strong> Nutzen Sie Formatierungsoptionen, um Ihren Text zu gestalten.</p>
// <p><strong>Bilder und Dokumente hinzufügen:</strong> Klicken Sie auf das Bild- oder Dokumentsymbol, um Dateien einzufügen.</p>
// <p><strong>Circle auswählen:</strong> Wählen Sie einen Circle für die Veröffentlichung Ihres Beitrags.</p>
// </div>`

export const DEFAULT_EDITOR_TXT1 = `Schreibe hier Deinen Beitrag ...`;
export enum ReactionType {
    Helpful = 'helpful',
    Inaccurate = 'inaccurate',
    NeedsImprovement = 'needs_improvement',
    Like = 'like',
    Dislike = 'dislike',
  }