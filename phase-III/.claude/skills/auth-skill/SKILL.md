---
name: auth-skill
description: Implement secure authentication systems including signup, signin, password hashing, JWT tokens, and Better Auth integration.
---

# Authentication Skill

## Instructions

1. **User Signup**
   - Collect user credentials (email, password)
   - Validate input (email format, password strength)
   - Hash passwords before storage
   - Store user securely in database

2. **User Signin**
   - Verify user credentials
   - Compare hashed passwords
   - Handle invalid login attempts
   - Return authentication response

3. **Password Security**
   - Use strong hashing algorithms (bcrypt / argon2)
   - Add salt to passwords
   - Never store plain-text passwords
   - Enforce minimum password rules

4. **JWT Authentication**
   - Generate access tokens on signin
   - Sign tokens with secret or private key
   - Set token expiration
   - Verify tokens on protected routes

5. **Better Auth Integration**
   - Configure Better Auth provider
   - Enable email/password authentication
   - Manage sessions and tokens
   - Integrate with frontend securely

## Best Practices
- Always hash passwords before saving
- Use environment variables for secrets
- Short-lived access tokens
- Protect routes with middleware
- Return generic auth errors (avoid leaking info)
- Follow OWASP authentication guidelines

## Example Structure
```ts
// signup
const hashedPassword = await bcrypt.hash(password, 10);
await db.user.create({
  email,
  password: hashedPassword,
});

// signin
const isValid = await bcrypt.compare(password, user.password);
if (!isValid) throw new Error("Invalid credentials");

// JWT
const token = jwt.sign(
  { userId: user.id },
  process.env.JWT_SECRET!,
  { expiresIn: "1h" }
);
