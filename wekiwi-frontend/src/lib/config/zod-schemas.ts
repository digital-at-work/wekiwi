import { z } from 'zod';

import { ACCEPTED_IMAGE_TYPES, ACCEPTED_FILE_TYPES } from '$lib/config/constants';
import { MAX_FILE_SIZE, MAX_IMAGE_SIZE } from '$lib/config/constants';

export const userSchema = z.object({
    first_name: z
        .union([
            z.string({ required_error: 'Vorname ist erforderlich.' })
                .min(1, { message: 'Vorname ist erforderlich.' })
                .trim(),
            z.null()
        ]),
    last_name: z
        .union([
            z.string({ required_error: 'Nachname ist erforderlich.' })
                .min(1, { message: 'Nachname ist erforderlich.' })
                .trim(),
            z.null()
        ]),
    username: z
        .string({ required_error: 'Benutzername ist erforderlich.' })
        .min(3, { message: 'Benutzername muss mindestens 3 Zeichen lang sein.' })
        .regex(/^[a-zA-Z0-9]*$/, { message: 'Benutzername darf keine Leerzeichen oder Sonderzeichen enthalten.' })
        .trim(),
    email: z
        .string({ required_error: 'E-Mail ist erforderlich.' })
        .email({ message: 'Bitte geben Sie eine gültige E-Mail-Adresse ein.' })
        .trim(),
    password: z
        .string({ required_error: 'Passwort ist erforderlich.' })
        .min(10, { message: 'Passwort muss mindestens 10 Zeichen lang sein.' })
        .regex(/^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[\W_]).{10,}$/, {
            message: 'Passwort muss mindestens einen Großbuchstaben, einen Kleinbuchstaben, eine Zahl und ein Sonderzeichen enthalten.',
        })
        .trim(),
    confirmPassword: z
        .string({ required_error: 'Passwort ist erforderlich.' })
        .min(10, { message: 'Passwort muss mindestens 10 Zeichen lang sein.' })
        .regex(/^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[\W_]).{10,}$/, {
            message: 'Passwort muss mindestens einen Großbuchstaben, einen Kleinbuchstaben, eine Zahl und ein Sonderzeichen enthalten.',
        })
        .trim(),
    terms: z.boolean({ required_error: 'Sie müssen die Auftragsverarbeitungsvereinbarung und Datenschutzbestimmungen akzeptieren.' }),
    role: z
        .enum(['USER', 'PREMIUM', 'ADMIN'], { required_error: 'Sie müssen eine Rolle haben.' })
        .default('USER'),
    verified: z.boolean().default(false),
    bio: z.union([
        z.string()
            .max(250, "Die Länge deiner Bio kann maxmimal 250 Zeichen betragen.")
            .optional(),
        z.null()
    ]),
    avatar: z.union([
        z.instanceof(File, { message: 'Bitte lade eine Datei hoch.' })
            .refine((f) => f.size <= MAX_FILE_SIZE, `Die maximale Dateigröße ist 2MB.`)
            .refine(
                (f) => ACCEPTED_FILE_TYPES.includes(f.type),
                "Nur die Dateiformate .jpg, .jpeg, .png und .pdf werden unterstützt."
            ),
        z.null()
    ]),
    token: z.string().trim(),
    receiveEmail: z.boolean().default(true),
    createdAt: z
        .date()
        .optional(),
    updatedAt: z
        .date()
        .optional()
});

const circleSchema = z.object({
    circle_id: z.number(),
    role: z.enum(['CircleUser', 'CircleAdmin'], { required_error: 'Sie müssen eine Rolle angeben.' }).default('CircleUser')
});

export const inviteSchema = z.object({
    recipientEmail: z
        .string({ required_error: 'E-Mail des Empfängers ist erforderlich.' })
        .email({ message: 'Bitte geben Sie eine gültige E-Mail-Adresse ein.' }),
    message: z
        .string()
        .max(500, { message: 'Die Nachricht kann maximal 500 Zeichen lang sein.' })
        .optional(),
    circles: z
        .array(circleSchema)
        .min(1, { message: 'Bitte wähle mindestens einen "Circle" aus.' })
});

export const userUpdatePasswordSchema = userSchema
    .pick({ password: true, confirmPassword: true })
    .superRefine(({ confirmPassword, password }, ctx) => {
        if (confirmPassword !== password) {
            ctx.addIssue({
                code: 'custom',
                message: 'Passwort und Passwortbestätigung müssen übereinstimmen',
                path: ['password']
            });
            ctx.addIssue({
                code: 'custom',
                message: 'Passwort und Passwortbestätigung müssen übereinstimmen',
                path: ['confirmPassword']
            });
        }
    });

export const signUpSchema = userSchema.pick({
    username: true,
    first_name: true,
    last_name: true,
    email: true,
    password: true,
    terms: true
});

export const signInSchema = userSchema.pick({
    email: true,
    password: true
});

export const profileSchema = userSchema.pick({
    first_name: true,
    last_name: true,
    username: true,
    email: true,
    bio: true,
    avatar: true
});

export const resetPasswordSchema = userSchema.pick({ email: true });

export const imageUploadSchema = z.object({
    image: z
        .instanceof(File, { message: 'Bitte lade ein Bild hoch.' })
        .refine((f) => f.size <= MAX_FILE_SIZE, `Die maximale Bildgröße ist 3MB.`)
        .refine(
            (f) => ACCEPTED_IMAGE_TYPES.includes(f.type),
            "Nur Formate im .jpg, .jpeg, und .png werden unterstützt."
        )
});

export const contentSchema = z.object({
    title: z
        .string().regex(new RegExp(/^[\s\S]*?(\S+\s+){1}\S+[\s\S]*$/), { message: 'Der Titel muss aus mindestens 2 Wörtern bestehen.' }).optional(),
    text: z
        .string().regex(new RegExp(/^[\s\S]*?(\S+\s+){2}\S+[\s\S]*$/), { message: 'Der Inhalt muss aus mindestens 3 Wörtern bestehen.' }),
    mentions: z.union([
        z.string(),  // For form submission as JSON string
        z.array(z.object({
            id: z.number().optional(),  // Make id optional since it might not be present
            username: z.string(),
            first_name: z.string().optional(),
            last_name: z.string().optional()
        }))
    ]).optional().default([]),
});

export const contentCreateSchema = contentSchema.pick({
    title: true,
    text: true,
    mentions: true
}).extend({
    files: z
        .instanceof(File, { message: 'Bitte lade eine Datei hoch.' })
        .refine((f) => f.size <= MAX_FILE_SIZE, `Die maximale Dateigröße ist 10MB.`) // Updated message
        .refine(
            (f) => ACCEPTED_FILE_TYPES.includes(f.type),
            "Nur die Dateiformate .jpg, .jpeg, .png und .pdf werden unterstützt."
        ).array(),
    circles: z.number().array().min(1, { message: 'Bitte wähle mindestens einen "Circle" aus.' }).max(5, { message: 'Du kannst maximal 5 "Circle" auswählen.' }),
    to_be_parsed_by_directus_flow: z.boolean().optional().default(false)
});

export const contentEditSchema = contentCreateSchema.pick({
    title: true,
    text: true,
    mentions: true,
    files: true,
    circles: true
}).extend({
    // include child_ids and their attachment_ids (in case circles changed)
    child_ids: z.array(z.object({ content_id: z.number(), attachment_ids: z.array(z.number())})).optional()
});

export const recipientSchema = z.union([z.string().email(), z.string()]);

export const contentShareSchema = z
    .object({
        emails: z.array(userSchema.pick({ email: true }).shape.email),
        usernames: z.array(userSchema.pick({ username: true }).shape.username),
        date_end: z.date().transform((date) => date.toISOString()),
        maxUses: z.number().int().positive().optional(),
        password: z.string().optional()
    })
    .partial()
    .refine(
        data => (data.emails && data.emails.length > 0) || (data.usernames && data.usernames.length > 0),
        'Bitte gebe mindestens eine Email oder einen Usernamen ein.',
    );
