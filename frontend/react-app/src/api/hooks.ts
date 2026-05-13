import { useMutation, useQuery } from '@tanstack/react-query';
import { customInstance } from '@/api/axios-instance';
import type {
  LoginFormData,
  RegisterFormData,
} from '@/lib/validation';

// ========================
//  API Types (ручные, на базе OpenAPI)
// ========================

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
}

export interface MessageResponse {
  message: string;
}

export interface ImageSnake {
  id: number;
  url: string;
  create_at: number;
}

export interface FullProfileSnake {
  user_id: number;
  username: string;
  avatar_image: ImageSnake | null;
  bio: string;
  age: number;
  sign: string;
  city: string;
  relationship_type: number;
  search_for: string;
  tags: string[];
  images: ImageSnake[];
}

export interface ShortProfileSnake {
  user_id: number;
  username: string;
  avatar_image: ImageSnake | null;
  bio: string;
  age: number;
  sign: string;
  city: string;
  tags: string[];
  images: ImageSnake[];
}

export interface GetProfileResponse {
  profile_data: FullProfileSnake;
}

export interface GetProfilesResponse {
  profiles_data: ShortProfileSnake[];
}

export interface ShortProfileProtoJson {
  userId: string;
  username: string;
  avatarImage: { id: string; url: string; createAt: string } | null;
  bio: string;
  age: string;
  sign: string;
  city: string;
  tags: string[];
  images: { id: string; url: string; createAt: string }[];
}

export interface GetRecommendationsResponse {
  profilesData: ShortProfileProtoJson[];
}

export interface ChatSummaryItem {
  chat_id: string;
  peer_user_id: number;
  last_message_at: string | null;
  last_message_preview: string | null;
}

export interface ChatMessageItem {
  id: string;
  sender_id: number;
  body: string | null;
  image_storage_key: string | null;
  created_at: string;
}

export interface ChatWithMessagesResponse {
  chat_id: string;
  peer_user_id: number;
  messages: ChatMessageItem[];
}

export interface CreateProfileRequestBody {
  username: string;
  bio: string;
  birthday: number;
  gender: string;
  relationship_type: string;
  avatar_image_id?: number;
  sign?: string;
  city?: string;
  search_for?: string;
  tags?: string[];
}

export interface UploadImagesResponse {
  user_id: number;
  images: ImageSnake[];
}

export interface CompatibilityTextItem {
  userId: string;
  text: string;
}

// ========================
//  Auth API hooks
// ========================

export const useRegister = () =>
  useMutation<AuthResponse, Error, { email: string; password: string }>({
    mutationFn: (data) =>
      customInstance<AuthResponse>({
        url: '/auth/register',
        method: 'POST',
        data,
      }),
  });

export const useLogin = () =>
  useMutation<AuthResponse, Error, { email: string; password: string }>({
    mutationFn: (data) =>
      customInstance<AuthResponse>({
        url: '/auth/login',
        method: 'POST',
        data,
      }),
  });

export const useLogout = () =>
  useMutation<MessageResponse, Error, { refresh_token: string }>({
    mutationFn: (data) =>
      customInstance<MessageResponse>({
        url: '/auth/logout',
        method: 'POST',
        data,
      }),
  });

export const useDeleteAccount = () =>
  useMutation<MessageResponse, Error, { refresh_token: string }>({
    mutationFn: (data) =>
      customInstance<MessageResponse>({
        url: '/auth/me',
        method: 'DELETE',
        data,
      }),
  });

// ========================
//  Profile API hooks
// ========================

export const useGetMyProfile = (enabled = true) =>
  useQuery<GetProfileResponse>({
    queryKey: ['profile', 'me'],
    queryFn: () =>
      customInstance<GetProfileResponse>({
        url: '/profiles/me',
        method: 'GET',
      }),
    enabled,
    retry: 1,
  });

export const useGetProfileById = (userId: number) =>
  useQuery<GetProfileResponse>({
    queryKey: ['profile', userId],
    queryFn: () =>
      customInstance<GetProfileResponse>({
        url: `/profiles/${userId}`,
        method: 'GET',
      }),
    enabled: !!userId,
  });

export const useCreateProfile = () =>
  useMutation<{ success: boolean }, Error, CreateProfileRequestBody>({
    mutationFn: (data) =>
      customInstance<{ success: boolean }>({
        url: '/profiles',
        method: 'POST',
        data,
      }),
  });

export const useUpdateProfile = () =>
  useMutation<GetProfileResponse, Error, Partial<CreateProfileRequestBody>>({
    mutationFn: (data) =>
      customInstance<GetProfileResponse>({
        url: '/profiles/me',
        method: 'PUT',
        data,
      }),
  });

export const useUploadImages = () =>
  useMutation<UploadImagesResponse, Error, FormData>({
    mutationFn: (formData) =>
      customInstance<UploadImagesResponse>({
        url: '/profiles/images',
        method: 'POST',
        data: formData,
        headers: { 'Content-Type': 'multipart/form-data' },
      }),
  });

export const useDeleteImages = () =>
  useMutation<{ success: boolean }, Error, { image_ids: number[] }>({
    mutationFn: (data) =>
      customInstance<{ success: boolean }>({
        url: '/profiles/images',
        method: 'DELETE',
        data,
        headers: { 'Content-Type': 'application/json' },
      }),
  });

export const useAttachTags = () =>
  useMutation<{ success: boolean }, Error, { tags: string[] }>({
    mutationFn: (data) =>
      customInstance<{ success: boolean }>({
        url: '/profiles/tags',
        method: 'POST',
        data,
      }),
  });

export const useDetachTags = () =>
  useMutation<{ success: boolean }, Error, { tags: string[] }>({
    mutationFn: (data) =>
      customInstance<{ success: boolean }>({
        url: '/profiles/tags',
        method: 'DELETE',
        data,
      }),
  });

// ========================
//  Recommendations API hooks
// ========================

export const useGetRecommendations = (enabled = true) =>
  useQuery<GetRecommendationsResponse>({
    queryKey: ['recommendations'],
    queryFn: () =>
      customInstance<GetRecommendationsResponse>({
        url: '/recommendations',
        method: 'GET',
      }),
    enabled,
  });

export const useGetCompatibility = () =>
  useMutation<{ items: CompatibilityTextItem[] }, Error, { user_ids: number[] }>({
    mutationFn: (data) =>
      customInstance<{ items: CompatibilityTextItem[] }>({
        url: '/recommendations/compatibility',
        method: 'POST',
        data,
      }),
  });

// ========================
//  Swipes API hooks
// ========================

export const useSwipeAction = () =>
  useMutation<{ success: boolean }, Error, { target_user_id: number; liked: boolean }>({
    mutationFn: (data) =>
      customInstance<{ success: boolean }>({
        url: '/swipes',
        method: 'POST',
        data,
      }),
  });

// ========================
//  Matches API hooks
// ========================

export const useGetMatches = (enabled = true) =>
  useQuery<GetProfilesResponse>({
    queryKey: ['matches'],
    queryFn: () =>
      customInstance<GetProfilesResponse>({
        url: '/matches',
        method: 'GET',
      }),
    enabled,
  });

// ========================
//  Chats API hooks
// ========================

export const useGetChats = (enabled = true) =>
  useQuery<ChatSummaryItem[]>({
    queryKey: ['chats'],
    queryFn: () =>
      customInstance<ChatSummaryItem[]>({
        url: '/chats',
        method: 'GET',
      }),
    enabled,
  });

export const useGetChatMessages = (peerUserId: number | null) =>
  useQuery<ChatWithMessagesResponse>({
    queryKey: ['chats', peerUserId],
    queryFn: () =>
      customInstance<ChatWithMessagesResponse>({
        url: `/chats/${peerUserId}`,
        method: 'GET',
      }),
    enabled: !!peerUserId,
  });

export const useSendMessage = () =>
  useMutation<ChatMessageItem, Error, { peerUserId: number; body: string }>({
    mutationFn: ({ peerUserId, body }) =>
      customInstance<ChatMessageItem>({
        url: `/chats/${peerUserId}/messages`,
        method: 'POST',
        data: { body },
      }),
  });

export const useDeleteChat = () =>
  useMutation<void, Error, number>({
    mutationFn: (peerUserId) =>
      customInstance<void>({
        url: `/chats/${peerUserId}`,
        method: 'DELETE',
      }),
  });
