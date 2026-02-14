---
name: backend-routes
description: Build backend APIs by generating routes, handling requests/responses, and connecting to databases.
---

# Backend API Development

## Instructions

1. **Route structure**
   - RESTful route naming
   - Clear separation of concerns
   - Versioned API paths (e.g. /api/v1)

2. **Request & response handling**
   - Validate request body, params, and query
   - Use proper HTTP status codes
   - Return consistent JSON responses

3. **Database integration**
   - Connect to database (SQL / NoSQL)
   - Perform CRUD operations
   - Handle async operations safely

## Best Practices

- Follow REST conventions
- Use try/catch for error handling
- Never expose sensitive data
- Keep controllers thin, logic in services
- Use environment variables for secrets

## Example Structure

```ts
// route.ts
import { Router } from "express";
import { getUsers, createUser } from "./controller";

const router = Router();

router.get("/users", getUsers);
router.post("/users", createUser);

export default router;
```
