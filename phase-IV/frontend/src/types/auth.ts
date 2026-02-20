export interface User {
  id: string;
  email: string;
  name?: string;
  createdAt?: Date;
}

export interface Session {
  id: string;
  userId: string;
  expiresAt: Date;
}

export interface ApiUser {
  id: string | number;
  email: string;
  name?: string;
  role?: string;
}

export interface AuthResponse {
  access_token: string;
  user: ApiUser;
}
