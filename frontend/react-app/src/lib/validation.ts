import { z } from 'zod';

/** Схема валидации формы входа */
export const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email обязателен')
    .email('Введите корректный email'),
  password: z
    .string()
    .min(8, 'Пароль должен содержать не менее 8 символов'),
});

/** Схема валидации формы регистрации */
export const registerSchema = z
  .object({
    email: z
      .string()
      .min(1, 'Email обязателен')
      .email('Введите корректный email'),
    password: z
      .string()
      .min(8, 'Пароль должен содержать не менее 8 символов'),
    confirmPassword: z
      .string()
      .min(1, 'Повторите пароль'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Пароли не совпадают',
    path: ['confirmPassword'],
  });

/** Схема для шага «О себе» */
export const aboutYourselfSchema = z.object({
  username: z
    .string()
    .min(2, 'Имя должно содержать минимум 2 символа')
    .max(50, 'Имя слишком длинное'),
  city: z
    .string()
    .min(2, 'Введите город')
    .max(100, 'Название города слишком длинное'),
  bio: z
    .string()
    .min(10, 'Опишите себя хотя бы в 10 символах')
    .max(500, 'Описание слишком длинное'),
});

/** Схема для шага «Кого ищете» */
export const lookingForSchema = z.object({
  relationship_type: z
    .string()
    .min(1, 'Выберите тип отношений'),
  search_for: z
    .string()
    .max(500, 'Описание слишком длинное')
    .optional(),
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type AboutYourselfFormData = z.infer<typeof aboutYourselfSchema>;
export type LookingForFormData = z.infer<typeof lookingForSchema>;
