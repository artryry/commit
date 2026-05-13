import { useState, useCallback, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { BackgroundElements } from '@/components/background-elements';
import { Logo } from '@/components/logo';
import { ProgressIndicator } from '@/components/progress-indicator';
import { useAuthStore } from '@/stores/auth-store';
import { useRegister, useLogin, useCreateProfile, useAttachTags, useUploadImages } from '@/api/hooks';
import {
  loginSchema,
  registerSchema,
  aboutYourselfSchema,
  lookingForSchema,
  type LoginFormData,
  type RegisterFormData,
  type AboutYourselfFormData,
  type LookingForFormData,
} from '@/lib/validation';
import '@/styles/poster.css';

/**
 * Шаги Poster flow:
 * 0 = Landing (Вход / Регистрация)
 * 1 = Вход
 * 2 = Регистрация
 * 3 = Расскажите о себе
 * 4 = Добавьте интересы
 * 5 = Добавьте фото
 * 6 = С кем хотите познакомиться
 * 7 = Поздравляем! (после полного заполнения)
 */
type PosterStep = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7;

const ONBOARDING_TOTAL_STEPS = 4; // шаги 3–6

// ---- MinIO URL builder ----
const MINIO_PUBLIC_BASE = import.meta.env.VITE_MINIO_URL ?? 'http://localhost:9000';
const MINIO_BUCKET = 'profile';

function profileImageUrl(storageKey: string): string {
  const path = `${MINIO_BUCKET}/${storageKey}`
    .split('/')
    .map(encodeURIComponent)
    .join('/');
  return `${MINIO_PUBLIC_BASE.replace(/\/$/, '')}/${path}`;
}

export const PosterPage = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<PosterStep>(0);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [tags, setTags] = useState<string[]>(['Imagine Dragons', 'Спорт', 'Сериалы']);
  const [tagInput, setTagInput] = useState('');
  const [showTagInput, setShowTagInput] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // Auth store
  const setTokens = useAuthStore((s) => s.setTokens);
  const setHasProfile = useAuthStore((s) => s.setHasProfile);

  // API mutations
  const registerMutation = useRegister();
  const loginMutation = useLogin();
  const createProfileMutation = useCreateProfile();
  const attachTagsMutation = useAttachTags();
  const uploadImagesMutation = useUploadImages();

  // ---- Forms ----
  const loginForm = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  });

  const registerForm = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: '', password: '', confirmPassword: '' },
  });

  const aboutForm = useForm<AboutYourselfFormData>({
    resolver: zodResolver(aboutYourselfSchema),
    defaultValues: { username: '', city: '', bio: '', birthday: undefined, gender: '', sign: '' },
  });

  const lookingForForm = useForm<LookingForFormData>({
    resolver: zodResolver(lookingForSchema),
    defaultValues: { relationship_type: '', search_for: '' },
  });

  // ---- Handlers ----
  const handleLogin = useCallback(async (data: LoginFormData) => {
    setError(null);
    try {
      const res = await loginMutation.mutateAsync({
        email: data.email,
        password: data.password,
      });
      setTokens(res.access_token, res.refresh_token);
      navigate('/discover');
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Ошибка входа. Проверьте данные.');
    }
  }, [loginMutation, navigate, setTokens]);

  /**
   * handleRegister — НЕ вызывает API.
   * Только валидирует email/пароль и переходит к заполнению профиля.
   * Реальный POST /auth/register будет на шаге 7.
   */
  const handleRegister = useCallback((_data: RegisterFormData) => {
    setError(null);
    // Данные сохранены в форме registerForm — отправим на шаге 7
    setStep(3);
  }, []);

  /**
   * handleFinishLookingFor — вызывается на шаге 6 ("Завершить").
   * НЕ вызывает API — только валидирует и переходит на шаг 7.
   */
  const handleFinishLookingFor = useCallback((_data: LookingForFormData) => {
    setError(null);
    setStep(7);
  }, []);

  /**
   * handleFinalSubmit — вызывается на шаге 7 ("Продолжить").
   * Отправляет ВСЕ данные в БД в правильном порядке:
   * 1. POST /auth/register — получаем токены
   * 2. POST /profiles/images — загружаем аватарку, получаем image id
   * 3. POST /profiles — создаём профиль с avatar_image_id
   */
  const handleFinalSubmit = useCallback(async () => {
    setError(null);
    setIsSubmitting(true);
    const regData = registerForm.getValues();
    const about = aboutForm.getValues();
    const lookingFor = lookingForForm.getValues();

    try {
      // 1) Регистрация — POST /auth/register
      const authRes = await registerMutation.mutateAsync({
        email: regData.email,
        password: regData.password,
      });
      setTokens(authRes.access_token, authRes.refresh_token);

      // 2) Загружаем аватарку — POST /profiles/images
      let avatarImageId: number | undefined;
      if (selectedFiles.length > 0) {
        const formData = new FormData();
        selectedFiles.forEach((file) => formData.append('images', file));
        const uploadRes = await uploadImagesMutation.mutateAsync(formData);
        if (uploadRes.images?.[0]) {
          avatarImageId = uploadRes.images[0].id;
        }
      }

      // 3) Создаём профиль — POST /profiles (с id аватарки)
      await createProfileMutation.mutateAsync({
        username: about.username,
        bio: about.bio,
        birthday: about.birthday,
        gender: about.gender,
        sign: about.sign,
        relationship_type: lookingFor.relationship_type,
        city: about.city,
        search_for: lookingFor.search_for || '',
        avatar_image_id: avatarImageId,
        tags,
      });

      // 4) Прикрепляем теги
      if (tags.length > 0) {
        await attachTagsMutation.mutateAsync({ tags });
      }

      setHasProfile(true);
      navigate('/discover');
    } catch (e: any) {
      setError(e.response?.data?.error || e.response?.data?.detail || 'Ошибка создания профиля.');
    } finally {
      setIsSubmitting(false);
    }
  }, [registerForm, aboutForm, lookingForForm, tags, selectedFiles, registerMutation, createProfileMutation, attachTagsMutation, uploadImagesMutation, setTokens, setHasProfile, navigate]);

  const handleAddTag = useCallback(() => {
    const val = tagInput.trim();
    if (val && !tags.includes(val)) {
      setTags((prev) => [...prev, val]);
    }
    setTagInput('');
    setShowTagInput(false);
  }, [tagInput, tags]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      setSelectedFiles([file]);
      setPreviewUrl(URL.createObjectURL(file));
    }
  }, []);

  const currentOnboardingStep = step >= 3 && step <= 6 ? step - 3 : 0;

  // ---- Render ----
  return (
    <>
      <main>
        {/* Step 0: Landing */}
        {step === 0 && (
          <div className="poster animate-scale-in" style={{ padding: 'clamp(24px, 5vw, 64px) clamp(16px, 5vw, 128px)' }}>
            <img id="hi" src="/assets/background/Group 14.png" alt="" />
            <Logo />
            <div className="poster-slogan">
              <h1 className="poster-slogan-text"><span className="dark-text">Найди Свой</span></h1>
              <h1 className="poster-slogan-text"><span className="accent-text">Коммит</span></h1>
            </div>
            <div className="poster-buttons">
              <button className="poster-button" onClick={() => setStep(1)}>Вход</button>
              <p className="poster-button-text">или</p>
              <button className="poster-button" onClick={() => setStep(2)}>Регистрация</button>
            </div>
          </div>
        )}

        {/* Step 1: Login */}
        {step === 1 && (
          <div className="poster-login animate-fade-in" style={{ display: 'flex' }}>
            <Logo />
            <div className="action-name">
              <h1 className="action-text">Вход</h1>
            </div>
            <form className="form" onSubmit={loginForm.handleSubmit(handleLogin)}>
              <div className="data-area">
                <div className="input-area">
                  <label htmlFor="login-email">E-mail</label>
                  <input
                    type="email"
                    id="login-email"
                    placeholder="example@mail.ru"
                    {...loginForm.register('email')}
                  />
                  {loginForm.formState.errors.email && (
                    <p className="error">{loginForm.formState.errors.email.message}</p>
                  )}
                </div>
                <div className="input-area">
                  <label htmlFor="login-password">Пароль</label>
                  <input
                    minLength={8}
                    type="password"
                    id="login-password"
                    placeholder="Введите пароль"
                    {...loginForm.register('password')}
                  />
                  {loginForm.formState.errors.password && (
                    <p className="error">{loginForm.formState.errors.password.message}</p>
                  )}
                </div>
              </div>
              {error && <p className="error" style={{ textAlign: 'center', width: '100%' }}>{error}</p>}
              <div className="poster-buttons second">
                <button
                  type="submit"
                  className="poster-button"
                  disabled={loginMutation.isPending}
                >
                  {loginMutation.isPending ? 'Входим...' : 'Войти'}
                </button>
                <p className="poster-button-text">
                  Ещё нет аккаунта?{' '}
                  <a href="#" onClick={(e) => { e.preventDefault(); setStep(2); setError(null); }}>
                    Регистрация
                  </a>
                </p>
              </div>
            </form>
          </div>
        )}

        {/* Step 2: Register */}
        {step === 2 && (
          <div className="poster-registration animate-fade-in" style={{ display: 'flex' }}>
            <Logo />
            <div className="action-name">
              <h1 className="action-text">Регистрация</h1>
            </div>
            <form className="form" onSubmit={registerForm.handleSubmit(handleRegister)}>
              <div className="data-area">
                <div className="input-area">
                  <label htmlFor="reg-email">E-mail</label>
                  <input
                    type="email"
                    id="reg-email"
                    placeholder="example@mail.ru"
                    {...registerForm.register('email')}
                  />
                  {registerForm.formState.errors.email && (
                    <p className="error">{registerForm.formState.errors.email.message}</p>
                  )}
                </div>
                <div className="input-area">
                  <label htmlFor="reg-password">Пароль</label>
                  <input
                    minLength={8}
                    type="password"
                    id="reg-password"
                    placeholder="Введите пароль"
                    {...registerForm.register('password')}
                  />
                  <p className="error">Пароль должен содержать не менее 8 символов</p>
                  {registerForm.formState.errors.password && (
                    <p className="error">{registerForm.formState.errors.password.message}</p>
                  )}
                </div>
                <div className="input-area">
                  <label htmlFor="reg-confirm">Повторите пароль</label>
                  <input
                    minLength={8}
                    type="password"
                    id="reg-confirm"
                    placeholder="Повторите пароль"
                    {...registerForm.register('confirmPassword')}
                  />
                  {registerForm.formState.errors.confirmPassword && (
                    <p className="error">{registerForm.formState.errors.confirmPassword.message}</p>
                  )}
                </div>
              </div>
              {error && <p className="error" style={{ textAlign: 'center', width: '100%' }}>{error}</p>}
              <div className="poster-buttons second">
                <button
                  type="submit"
                  className="poster-button"
                >
                  Зарегистрироваться
                </button>
                <p className="poster-button-text">
                  Уже есть аккаунт?{' '}
                  <a href="#" onClick={(e) => { e.preventDefault(); setStep(1); setError(null); }}>
                    Войти
                  </a>
                </p>
              </div>
            </form>
          </div>
        )}

        {/* Step 3: About Yourself */}
        {step === 3 && (
          <div className="poster-yourself animate-slide-up" style={{ display: 'flex' }}>
            <ProgressIndicator currentStep={currentOnboardingStep} totalSteps={ONBOARDING_TOTAL_STEPS} />
            <div className="action-name">
              <div className="message-area">
                <h1 className="action-text">Расскажите о себе</h1>
                <form
                  className="form"
                  onSubmit={aboutForm.handleSubmit(() => setStep(4))}
                >
                  <div className="data-area">
                    <div className="input-area">
                      <label htmlFor="name">Ваше имя</label>
                      <input
                        type="text"
                        id="name"
                        placeholder="Введите ваше имя"
                        {...aboutForm.register('username')}
                      />
                      <p className="p-text">Ваше имя будет видно всем пользователям</p>
                      {aboutForm.formState.errors.username && (
                        <p className="error">{aboutForm.formState.errors.username.message}</p>
                      )}
                    </div>
                    <div className="input-area">
                      <label htmlFor="location">Локация</label>
                      <input
                        type="text"
                        id="location"
                        placeholder="Введите ваш город"
                        {...aboutForm.register('city')}
                      />
                      {aboutForm.formState.errors.city && (
                        <p className="error">{aboutForm.formState.errors.city.message}</p>
                      )}
                    </div>
                    <div className="input-area">
                      <label htmlFor="describe">Опишите себя</label>
                      <textarea
                        id="describe"
                        placeholder="Расскажите о себе"
                        {...aboutForm.register('bio')}
                      />
                      {aboutForm.formState.errors.bio && (
                        <p className="error">{aboutForm.formState.errors.bio.message}</p>
                      )}
                    </div>
                    <div className="input-area">
                      <label htmlFor="birthday">День рождения (Unix)</label>
                      <input
                        type="number"
                        id="birthday"
                        placeholder="Например, 946684800"
                        {...aboutForm.register('birthday', { valueAsNumber: true })}
                      />
                      {aboutForm.formState.errors.birthday && (
                        <p className="error">{aboutForm.formState.errors.birthday.message}</p>
                      )}
                    </div>
                    <div className="input-area">
                      <label>Пол</label>
                      <CustomDropdown
                        options={[
                          { value: '', label: 'Выберите' },
                          { value: 'MALE', label: 'Мужской' },
                          { value: 'FEMALE', label: 'Женский' },
                        ]}
                        value={aboutForm.watch('gender') || ''}
                        onChange={(val) => aboutForm.setValue('gender', val, { shouldValidate: true })}
                      />
                      {aboutForm.formState.errors.gender && (
                        <p className="error">{aboutForm.formState.errors.gender.message}</p>
                      )}
                    </div>
                    <div className="input-area">
                      <label>Знак зодиака</label>
                      <CustomDropdown
                        options={[
                          { value: '', label: 'Выберите' },
                          { value: 'ARIES', label: 'Овен' },
                          { value: 'TAURUS', label: 'Телец' },
                          { value: 'GEMINI', label: 'Близнецы' },
                          { value: 'CANCER', label: 'Рак' },
                          { value: 'LEO', label: 'Лев' },
                          { value: 'VIRGO', label: 'Дева' },
                          { value: 'LIBRA', label: 'Весы' },
                          { value: 'SCORPIO', label: 'Скорпион' },
                          { value: 'SAGITTARIUS', label: 'Стрелец' },
                          { value: 'CAPRICORN', label: 'Козерог' },
                          { value: 'AQUARIUS', label: 'Водолей' },
                          { value: 'PISCES', label: 'Рыбы' },
                        ]}
                        value={aboutForm.watch('sign') || ''}
                        onChange={(val) => aboutForm.setValue('sign', val, { shouldValidate: true })}
                      />
                      {aboutForm.formState.errors.sign && (
                        <p className="error">{aboutForm.formState.errors.sign.message}</p>
                      )}
                    </div>
                  </div>
                  <div className="poster-buttons second">
                    <button type="submit" className="poster-button">Продолжить</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Tags */}
        {step === 4 && (
          <div className="poster-tags animate-slide-up" style={{ display: 'flex' }}>
            <ProgressIndicator currentStep={currentOnboardingStep} totalSteps={ONBOARDING_TOTAL_STEPS} />
            <div className="action-name">
              <div className="message-area">
                <h1 className="action-text">Добавьте ваши интересы</h1>
                <form className="form" onSubmit={(e) => { e.preventDefault(); setStep(5); }}>
                  <div className="data-area-tags">
                    <div className="tags-container">
                      <div className="add-tags">
                        {tags.map((tag, i) => (
                          <div className="tag" key={i} onClick={() => setTags(tags.filter((_, j) => j !== i))} style={{ cursor: 'pointer' }}>
                            <p>#{tag}</p>
                          </div>
                        ))}
                        {showTagInput ? (
                          <div className="tag-input-container">
                            <span>#</span>
                            <input
                              type="text"
                              className="tag-input"
                              placeholder="тэг"
                              value={tagInput}
                              onChange={(e) => setTagInput(e.target.value)}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') { e.preventDefault(); handleAddTag(); }
                                if (e.key === 'Escape') setShowTagInput(false);
                              }}
                              onBlur={handleAddTag}
                              autoFocus
                            />
                          </div>
                        ) : (
                          <div className="tag-add" onClick={() => setShowTagInput(true)}>
                            <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                              <path d="M20 9V33" stroke="#BB8DFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                              <path d="M8 21H32" stroke="#BB8DFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="poster-buttons second">
                    <button type="submit" className="poster-button">Продолжить</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Step 5: Photo Upload */}
        {step === 5 && (
          <div className="poster-photo-add animate-slide-up" style={{ display: 'flex' }}>
            <ProgressIndicator currentStep={currentOnboardingStep} totalSteps={ONBOARDING_TOTAL_STEPS} />
            <div className="action-name">
              <div className="message-area">
                <h1 className="action-text">Добавьте ваше фото</h1>
                <form className="form" onSubmit={(e) => { e.preventDefault(); setStep(6); }}>
                  <div className="photo-add-conatiner">
                    <label className="photo-background" style={{ cursor: 'pointer' }}>
                      <input
                        type="file"
                        accept="image/jpeg,image/png,image/webp"
                        style={{ display: 'none' }}
                        onChange={handleFileSelect}
                      />
                      <div className="photo">
                        {previewUrl ? (
                          <img
                            src={previewUrl}
                            alt="Превью"
                            style={{
                              width: '100%',
                              height: '100%',
                              objectFit: 'cover',
                              borderRadius: '12px',
                            }}
                          />
                        ) : (
                          <svg width="100" height="100" viewBox="0 0 40 40" fill="none">
                            <path d="M20 9V33" stroke="#BB8DFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <path d="M8 21H32" stroke="#BB8DFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                          </svg>
                        )}
                      </div>
                    </label>
                  </div>
                  <div className="poster-buttons second">
                    <button type="submit" className="poster-button">Продолжить</button>
                  </div>
                </form>
              </div>
              {/* <form className="form" onSubmit={(e) => { e.preventDefault(); setStep(6); }}>
                <div className="photo-add-conatiner">
                  <label className="photo-background" style={{ cursor: 'pointer' }}>
                    <input
                      type="file"
                      accept="image/jpeg,image/png,image/webp"
                      style={{ display: 'none' }}
                      onChange={handleFileSelect}
                    />
                    <div className="photo">
                      {previewUrl ? (
                        <img
                          src={previewUrl}
                          alt="Превью"
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                            borderRadius: '12px',
                          }}
                        />
                      ) : (
                        <svg width="100" height="100" viewBox="0 0 40 40" fill="none">
                          <path d="M20 9V33" stroke="#BB8DFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                          <path d="M8 21H32" stroke="#BB8DFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      )}
                    </div>
                  </label>
                </div>
                <div className="poster-buttons second">
                  <button type="submit" className="poster-button">Продолжить</button>
                </div>
              </form> */}
            </div>
          </div>
        )}

        {/* Step 6: Looking For — только валидация, без API */}
        {step === 6 && (
          <div className="poster-looking-for animate-slide-up" style={{ display: 'flex' }}>
            <ProgressIndicator currentStep={currentOnboardingStep} totalSteps={ONBOARDING_TOTAL_STEPS} />
            <div className="action-name">
              <div className="message-area">
                <h1 className="action-text">С кем вы хотите познакомиться?</h1>
                <form className="form" onSubmit={lookingForForm.handleSubmit(handleFinishLookingFor)}>
                  <div className="data-area">
                    <div className="input-area">
                      <label>Вы ищите</label>
                      <CustomDropdown
                        options={[
                          { value: '', label: 'Выберите' },
                          { value: 'RELATIONSHIP', label: 'Партнёра' },
                          { value: 'FRIENDSHIP', label: 'Друга' },
                          { value: 'NETWORKING', label: 'Нетворкинг' },
                        ]}
                        value={lookingForForm.watch('relationship_type')}
                        onChange={(val) => lookingForForm.setValue('relationship_type', val, { shouldValidate: true })}
                      />
                      {lookingForForm.formState.errors.relationship_type && (
                        <p className="error">{lookingForForm.formState.errors.relationship_type.message}</p>
                      )}
                    </div>
                    <div className="input-area">
                      <label htmlFor="search-for">Опишите, какого человека вы ищете</label>
                      <textarea
                        id="search-for"
                        placeholder="Любовь всей своей жизни с двумя кошками и страстью к настольным играм"
                        {...lookingForForm.register('search_for')}
                      />
                    </div>
                  </div>
                  <div className="poster-buttons second">
                    <button type="submit" className="poster-button">Завершить</button>
                  </div>
                </form>
              </div>
              {/* <form className="form" onSubmit={lookingForForm.handleSubmit(handleFinishLookingFor)}>
                <div className="data-area">
                  <div className="input-area">
                    <label>Вы ищите</label>
                    <CustomDropdown
                      options={[
                        { value: '', label: 'Выберите' },
                        { value: 'RELATIONSHIP', label: 'Партнёра' },
                        { value: 'FRIENDSHIP', label: 'Друга' },
                        { value: 'NETWORKING', label: 'Нетворкинг' },
                      ]}
                      value={lookingForForm.watch('relationship_type')}
                      onChange={(val) => lookingForForm.setValue('relationship_type', val, { shouldValidate: true })}
                    />
                    {lookingForForm.formState.errors.relationship_type && (
                      <p className="error">{lookingForForm.formState.errors.relationship_type.message}</p>
                    )}
                  </div>
                  <div className="input-area">
                    <label htmlFor="search-for">Опишите, какого человека вы ищете</label>
                    <textarea
                      id="search-for"
                      placeholder="Любовь всей своей жизни с двумя кошками и страстью к настольным играм"
                      {...lookingForForm.register('search_for')}
                    />
                  </div>
                </div>
                <div className="poster-buttons second">
                  <button type="submit" className="poster-button">Завершить</button>
                </div>
              </form> */}
            </div>
          </div>
        )}

        {/* Step 7: Поздравляем — кнопка «Продолжить» отправляет ВСЕ данные */}
        {step === 7 && (
          <div className="poster-success animate-scale-in" style={{ display: 'flex' }}>
            <Logo />
            <div className="action-name">
              <div className="message-area">
                <h1 className="action-text">Поздравляем!</h1>
                <p>Вы успешно зарегистрировались!</p>
              </div>
              <p>Давайте перейдём к вашему первому знакомству!</p>
              {error && <p className="error" style={{ textAlign: 'center', width: '100%' }}>{error}</p>}
              <button
                type="button"
                className="poster-button"
                disabled={isSubmitting}
                onClick={handleFinalSubmit}
              >
                {isSubmitting ? 'Отправляем...' : 'Продолжить'}
              </button>
            </div>
          </div>
        )}
      </main>
      <BackgroundElements />
    </>
  );
};

// ---- Custom Dropdown ----
interface DropdownOption {
  value: string;
  label: string;
}

const CustomDropdown = ({
  options,
  value,
  onChange,
}: {
  options: DropdownOption[];
  value: string;
  onChange: (val: string) => void;
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const selectedLabel = options.find((o) => o.value === value)?.label || 'Выберите';

  // Закрываем при клике вне dropdown
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  return (
    <div className="custom-dropdown" ref={dropdownRef} style={{ position: 'relative' }}>
      <div
        className="custom-dropdown-selected"
        onClick={() => setIsOpen(!isOpen)}
      >
        {selectedLabel}
        <svg
          width="24" height="24" viewBox="0 0 24 24" fill="none"
          className="arrow-down-icon"
          style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.3s ease' }}
        >
          <path d="M6 9L12 15L18 9" stroke="#3C344B" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
      {isOpen && (
        <div className="custom-dropdown-options" style={{ display: 'block' }}>
          {options.map((option) => (
            <div
              key={option.value}
              className="custom-dropdown-option"
              onClick={() => {
                onChange(option.value);
                setIsOpen(false);
              }}
            >
              {option.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
