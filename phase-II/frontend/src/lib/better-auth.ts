import { betterAuth } from "better-auth";

// Initialize Better Auth with configuration
export const auth = betterAuth({
  database: {
    provider: "sqlite",
    url: process.env.DATABASE_URL || "./todo_app.db",
  },
  // Add JWT configuration
  jwt: {
    expiresIn: "7d", // 7 days expiration
    secret:
      process.env.BETTER_AUTH_SECRET ||
      "fallback-dev-secret-change-in-production",
  },
  // User configuration
  user: {
    fields: {
      // Define custom fields if needed
    },
  },
  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days in seconds
  },
  // Add custom email/password authentication
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // For simplicity in this implementation
  },
  // OAuth providers can be added here if needed
  socialProviders: {
    // google: {
    //   clientId: process.env.GOOGLE_CLIENT_ID!,
    //   clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    // },
  },
});
