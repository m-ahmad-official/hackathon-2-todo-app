# Todo Application Frontend

This is the frontend for the Todo application, built with Next.js 16+ using the App Router. It provides a secure, full-stack task management application with user authentication and data isolation.

## Features

- **User Authentication**: Secure login and signup with JWT tokens using Better Auth
- **Task Management**: Create, read, update, and delete tasks with completion toggling
- **User Data Isolation**: Users can only access their own tasks
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Secure Session Management**: Automatic logout on token expiration

## Tech Stack

- Next.js 16+ (App Router)
- React 18+
- TypeScript
- Tailwind CSS
- Better Auth (for authentication)
- React Hook Form (for form handling)
- SWR (for data fetching)

## Getting Started

### Prerequisites

- Node.js 18+
- npm, yarn, or pnpm

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd todo-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. Create a `.env.local` file based on `.env.example`:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

4. Run the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   # or
   bun dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```text
frontend/
├── app/                    # Next.js App Router pages
│   ├── (auth)/            # Authentication-related routes
│   │   ├── sign-in/       # Sign in page
│   │   └── sign-up/       # Sign up page
│   ├── dashboard/         # Dashboard layout and page
│   ├── globals.css        # Global styles
│   └── layout.tsx         # Root layout
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── auth/          # Authentication components
│   │   ├── tasks/         # Task management components
│   │   └── layout/        # Layout components
│   ├── models/            # Data models and interfaces
│   ├── services/          # API service layer
│   ├── providers/         # React context providers
│   └── lib/               # Utility functions
├── public/                # Static assets
├── tests/                 # Test files
└── docs/                  # Documentation
```

## API Integration

The frontend communicates with the backend API at the URL specified in the environment variables. All API requests include the JWT token in the Authorization header automatically.

## Authentication Flow

1. Users sign up or sign in through the auth pages
2. Upon successful authentication, a JWT token is stored securely
3. The token is automatically attached to all API requests
4. The application verifies user identity and enforces data isolation
5. Session automatically expires when the token expires

## Development

### Running Tests

```bash
npm run test
# or for specific test files
npm run test -- --watch
```

### Building for Production

```bash
npm run build
```

### Linting and Formatting

```bash
npm run lint
npm run format
```

## Environment Variables

- `NEXT_PUBLIC_API_BASE_URL`: Base URL for the backend API (e.g., `http://localhost:8000`)
- `NEXT_PUBLIC_JWT_EXPIRATION_DELTA`: Token expiration time in seconds (default: 604800 for 7 days)

## Security Features

- JWT token validation and expiration checks
- User data isolation - users can only access their own tasks
- Secure token storage and transmission
- Proper error handling and logging
- Protected routes that require authentication

## Deployment

This application can be deployed to any hosting service that supports Next.js applications, such as Vercel, Netlify, or AWS.

For Vercel deployment:
```bash
vercel --prod
```

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
