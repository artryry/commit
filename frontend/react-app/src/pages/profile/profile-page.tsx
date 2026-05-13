import { useGetMyProfile, useUpdateProfile, useUploadImages, useDeleteImages, useAttachTags, useDetachTags, type GetProfileResponse } from '@/api/hooks';
import { useState, useRef, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';

const MINIO_PUBLIC_BASE = import.meta.env.VITE_MINIO_URL ?? 'http://localhost:9000';
function profileImageUrl(storageKey: string): string {
  const path = `profile/${storageKey}`.split('/').map(encodeURIComponent).join('/');
  return `${MINIO_PUBLIC_BASE.replace(/\/$/, '')}/${path}`;
}

const RELATIONSHIP_OPTIONS = [
  { value: 'RELATIONSHIP', label: 'Партнёра' },
  { value: 'FRIENDSHIP', label: 'Друга' },
  { value: 'NETWORKING', label: 'Нетворкинг' },
];

function relationshipLabel(val: number | string): string {
  if (typeof val === 'number') {
    return ['Не указано', 'Друга', 'Партнёра', 'Нетворкинг'][val] || 'Не указано';
  }
  return RELATIONSHIP_OPTIONS.find(o => o.value === val)?.label || String(val);
}

export const ProfilePage = () => {
  const queryClient = useQueryClient();
  const { data, isLoading } = useGetMyProfile();
  const updateMutation = useUpdateProfile();
  const uploadImagesMutation = useUploadImages();
  const deleteImagesMutation = useDeleteImages();
  const attachTagsMutation = useAttachTags();
  const detachTagsMutation = useDetachTags();
  const profile = data?.profile_data;

  const [editField, setEditField] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');
  const [showTagInput, setShowTagInput] = useState(false);
  const [tagInput, setTagInput] = useState('');
  const [showRelDropdown, setShowRelDropdown] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const avatarInputRef = useRef<HTMLInputElement>(null);

  const refetchProfile = () => queryClient.invalidateQueries({ queryKey: ['profile', 'me'] });

  const handleSaveField = useCallback(async (field: string, value?: string) => {
    try {
      await updateMutation.mutateAsync({ [field]: value ?? editValue });
      refetchProfile();
      setEditField(null);
    } catch { /* silent */ }
  }, [editValue, updateMutation]);

  const startEdit = (field: string, currentValue: string) => {
    setEditField(field);
    setEditValue(currentValue);
  };

  const handlePhotoUpload = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files?.length) return;
    const formData = new FormData();
    formData.append('images', files[0]);
    try {
      await uploadImagesMutation.mutateAsync(formData);
      refetchProfile();
    } catch { /* silent */ }
  }, [uploadImagesMutation]);

  const handleAvatarUpload = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files?.length) return;
    const formData = new FormData();
    formData.append('images', files[0]);
    try {
      const res = await uploadImagesMutation.mutateAsync(formData);
      if (res.images?.[0]) {
        await updateMutation.mutateAsync({ avatar_image_id: res.images[0].id });
        refetchProfile();
      }
    } catch { /* silent */ }
  }, [uploadImagesMutation, updateMutation]);

  const handleDeleteImage = useCallback(async (imageId: number) => {
    // Optimistic update: remove image from cache immediately
    queryClient.setQueryData<GetProfileResponse | undefined>(['profile', 'me'], (old) => {
      if (!old?.profile_data) return old;
      return {
        ...old,
        profile_data: {
          ...old.profile_data,
          images: (old.profile_data.images || []).filter((img) => img.id !== imageId),
        },
      };
    });
    try {
      await deleteImagesMutation.mutateAsync({ image_ids: [imageId] });
      refetchProfile();
    } catch { /* silent */ }
  }, [deleteImagesMutation, queryClient]);

  const handleAddTag = useCallback(async () => {
    const val = tagInput.trim();
    if (!val) return;
    try {
      await attachTagsMutation.mutateAsync({ tags: [val] });
      refetchProfile();
    } catch { /* silent */ }
    setTagInput('');
    setShowTagInput(false);
  }, [tagInput, attachTagsMutation]);

  const handleRemoveTag = useCallback(async (tag: string) => {
    try {
      await detachTagsMutation.mutateAsync({ tags: [tag] });
      refetchProfile();
    } catch { /* silent */ }
  }, [detachTagsMutation]);

  const handleRelationshipChange = useCallback(async (val: string) => {
    setShowRelDropdown(false);
    try {
      await updateMutation.mutateAsync({ relationship_type: val });
      refetchProfile();
    } catch { /* silent */ }
  }, [updateMutation]);

  if (isLoading) {
    return (
      <section className="commit-page" style={{ justifyContent: 'center', alignItems: 'center' }}>
        <div className="poster-logo animate-scale-in">
          <img src="/assets/icons/Logo.png" className="poster-logo-img" alt="Загрузка" style={{ maxWidth: '120px' }} />
          <p className="poster-logo-text" style={{ fontSize: '1rem' }}>Загрузка...</p>
        </div>
      </section>
    );
  }

  if (!profile) {
    return (
      <section className="commit-page" style={{ justifyContent: 'center', alignItems: 'center' }}>
        <p style={{ color: 'var(--dark-color)', fontSize: 'var(--fs-24)' }}>Профиль не найден</p>
      </section>
    );
  }

  const avatarSrc = profile.avatar_image?.url ? profileImageUrl(profile.avatar_image.url) : '/assets/photos/man_portret (4).png';

  return (
    <section className="commit-page" id="my-profile">
      {/* Left: Photo Gallery Card — ONE upload template 3:4 */}
      <section className="photo-gallery-card glass-card">
        <div className="photo-grid">
          {/* Upload template */}
          <div className="photo-slot photo-slot--add" onClick={() => fileInputRef.current?.click()} style={{ cursor: 'pointer' }}>
            <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
              <path d="M40 0V40M40 40V80M40 40H80M40 40H0" stroke="#FF5777" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <input ref={fileInputRef} type="file" accept="image/jpeg,image/png,image/webp" style={{ display: 'none' }} onChange={handlePhotoUpload} />
          </div>
          {/* Loaded photos */}
          {(profile.images || []).map((img) => (
            <div className="photo-slot" key={img.id}>
              <img src={profileImageUrl(img.url)} alt="Фото профиля" />
              <button
                className="photo-slot-delete"
                aria-label="Удалить фото"
                onClick={() => handleDeleteImage(img.id)}
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M12 4L4 12M4 4L12 12" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Right: Profile Info Card */}
      <section className="profile-info-card glass-card">
        {/* Header row: avatar + name */}
        <div className="profile-header">
          <div className="profile-avatar">
            <img src={avatarSrc} alt="Аватар" className="avatar-img" />
            <button className="btn-edit avatar-edit" aria-label="Редактировать аватар" onClick={() => avatarInputRef.current?.click()}>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M13.23 2.232L16.77 5.768M14.73 0.732C15.71 -0.244 17.29 -0.244 18.27 0.732C19.24 1.709 19.24 3.291 18.27 4.268L4.5 18.035H1V14.464L14.73 0.732Z" stroke="#3C344B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </button>
            <input ref={avatarInputRef} type="file" accept="image/jpeg,image/png,image/webp" style={{ display: 'none' }} onChange={handleAvatarUpload} />
          </div>
          <div className="profile-name-group">
            <h1 className="profile-name">{profile.username}, {profile.age}</h1>
            {profile.sign && (
              <span className="profile-name-decoration">
                <img src="/assets/main-icons/zodiac-aquarius.png" alt="" />
                <p className="profile-zodiak-mobile">{profile.sign}</p>
              </span>
            )}
          </div>
        </div>

        {/* Описание — editable */}
        <div className="profile-item-frame">
          <div className="profile-bio-labels"><span className="bio-label">Ваше описание</span></div>
          <div className="profile-field-card glass-card-inner">
            <div className="field-content" onClick={() => startEdit('bio', profile.bio)}>
              {editField === 'bio' ? (
                <textarea value={editValue} onChange={(e) => setEditValue(e.target.value)} onBlur={() => handleSaveField('bio')} onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSaveField('bio')} autoFocus style={{ border: 'none', outline: '2px solid var(--main-color)', borderRadius: '8px', padding: '8px', fontFamily: 'inherit', fontSize: 'var(--fs-18)', resize: 'none', minHeight: '60px', width: '100%' }} />
              ) : (
                <p className="field-text">{profile.bio || 'Нажмите чтобы добавить описание'}</p>
              )}
            </div>
            <button className="btn-edit field-edit" aria-label="Редактировать" onClick={() => startEdit('bio', profile.bio)}>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M13.23 2.232L16.77 5.768M14.73 0.732C15.71 -0.244 17.29 -0.244 18.27 0.732C19.24 1.709 19.24 3.291 18.27 4.268L4.5 18.035H1V14.464L14.73 0.732Z" stroke="#3C344B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </button>
          </div>
        </div>

        {/* Локация — editable */}
        <div className="profile-item-frame">
          <div className="profile-bio-labels"><span className="bio-label">Локация</span></div>
          <div className="profile-field-card glass-card-inner">
            <div className="field-content" onClick={() => startEdit('city', profile.city)}>
              {editField === 'city' ? (
                <input type="text" value={editValue} onChange={(e) => setEditValue(e.target.value)} onBlur={() => handleSaveField('city')} onKeyDown={(e) => e.key === 'Enter' && handleSaveField('city')} autoFocus style={{ border: 'none', outline: '2px solid var(--main-color)', borderRadius: '8px', padding: '8px', fontFamily: 'inherit', fontSize: 'var(--fs-18)', width: '100%' }} />
              ) : (
                <p className="field-text">{profile.city || 'Не указано'}</p>
              )}
            </div>
            <button className="btn-edit field-edit" aria-label="Редактировать" onClick={() => startEdit('city', profile.city)}>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M13.23 2.232L16.77 5.768M14.73 0.732C15.71 -0.244 17.29 -0.244 18.27 0.732C19.24 1.709 19.24 3.291 18.27 4.268L4.5 18.035H1V14.464L14.73 0.732Z" stroke="#3C344B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </button>
          </div>
        </div>

        {/* Вы ищите — dropdown */}
        <div className="profile-item-frame">
          <div className="profile-bio-labels"><span className="bio-label">Вы ищите</span></div>
          <div className="profile-field-card glass-card-inner" style={{ position: 'relative' }}>
            <div className="field-content">
              <p className="field-text">{relationshipLabel(profile.relationship_type)}</p>
            </div>
            <button className="btn-edit field-edit field-dropdown" aria-label="Раскрыть" onClick={() => setShowRelDropdown(!showRelDropdown)}>
              <svg width="14" height="8" viewBox="0 0 14 8" fill="none" style={{ transform: showRelDropdown ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.3s' }}>
                <path d="M7 5.314L11.95 0.364C12.14 0.177 12.4 0.071 12.67 0.071C12.93 0.071 13.19 0.177 13.38 0.364C13.57 0.551 13.67 0.814 13.67 1.084C13.67 1.355 13.57 1.617 13.38 1.804L7.71 7.435C7.52 7.622 7.27 7.728 7 7.728C6.73 7.728 6.48 7.622 6.29 7.435L0.64 1.804C0.45 1.617 0.34 1.355 0.34 1.084C0.34 0.814 0.45 0.551 0.64 0.364C0.83 0.177 1.09 0.071 1.36 0.071C1.63 0.071 1.89 0.177 2.08 0.364L7 5.314Z" fill="#3C344B" />
              </svg>
            </button>
            {showRelDropdown && (
              <div className="custom-dropdown-options" style={{ position: 'absolute', top: '100%', left: 0, width: '100%', zIndex: 10, display: 'block' }}>
                {RELATIONSHIP_OPTIONS.map((opt) => (
                  <div key={opt.value} className="custom-dropdown-option" onClick={() => handleRelationshipChange(opt.value)}>{opt.label}</div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Какого человека вы ищите — editable */}
        <div className="profile-item-frame">
          <div className="profile-bio-labels"><span className="bio-label">Какого человека вы ищите?</span></div>
          <div className="profile-field-card glass-card-inner">
            <div className="field-content" onClick={() => startEdit('search_for', profile.search_for)}>
              {editField === 'search_for' ? (
                <textarea value={editValue} onChange={(e) => setEditValue(e.target.value)} onBlur={() => handleSaveField('search_for')} onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSaveField('search_for')} autoFocus style={{ border: 'none', outline: '2px solid var(--main-color)', borderRadius: '8px', padding: '8px', fontFamily: 'inherit', fontSize: 'var(--fs-18)', resize: 'none', minHeight: '60px', width: '100%' }} />
              ) : (
                <p className="field-text">{profile.search_for || 'Не указано'}</p>
              )}
            </div>
            <button className="btn-edit field-edit" aria-label="Редактировать" onClick={() => startEdit('search_for', profile.search_for)}>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M13.23 2.232L16.77 5.768M14.73 0.732C15.71 -0.244 17.29 -0.244 18.27 0.732C19.24 1.709 19.24 3.291 18.27 4.268L4.5 18.035H1V14.464L14.73 0.732Z" stroke="#3C344B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </button>
          </div>
        </div>

        {/* Интересы — add/remove */}
        <div className="profile-item-frame">
          <div className="profile-bio-labels"><span className="bio-label">Интересы</span></div>
          <div className="interests-container">
            {(profile.tags || []).map((tag, i) => (
              <span className="interest-tag" key={i} onClick={() => handleRemoveTag(tag)} style={{ cursor: 'pointer' }} title="Нажмите чтобы удалить">#{tag}</span>
            ))}
            {showTagInput ? (
              <span className="interest-tag" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                #<input type="text" value={tagInput} onChange={(e) => setTagInput(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAddTag(); } if (e.key === 'Escape') setShowTagInput(false); }} onBlur={handleAddTag} autoFocus style={{ border: 'none', background: 'transparent', fontFamily: 'inherit', fontSize: 'inherit', outline: 'none', width: '80px' }} />
              </span>
            ) : (
              <button className="interest-add-btn" aria-label="Добавить интерес" onClick={() => setShowTagInput(true)}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 1V8M8 8V15M8 8H15M8 8H1" stroke="#FF5777" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" /></svg>
              </button>
            )}
          </div>
        </div>
      </section>
    </section>
  );
};
