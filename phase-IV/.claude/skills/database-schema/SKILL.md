---
name: database-schema
description: Design scalable database schemas with tables, migrations, and relationships. Use for production-ready applications.
---

# Database Schema Design

## Instructions

1. **Table structure**
   - Use clear, descriptive table names
   - Define primary keys (`id`)
   - Choose correct data types
   - Add timestamps (`created_at`, `updated_at`)

2. **Relationships**
   - One-to-one, one-to-many, many-to-many
   - Use foreign keys
   - Apply cascading rules where needed
   - Normalize data to avoid duplication

3. **Migrations**
   - Create versioned migrations
   - Separate create, update, and delete migrations
   - Ensure migrations are reversible
   - Keep migrations small and focused

4. **Schema constraints**
   - NOT NULL where required
   - UNIQUE for emails, usernames, slugs
   - Index frequently queried columns
   - Use defaults wisely

## Best Practices
- Design schema before writing queries
- Follow consistent naming conventions
- Avoid premature optimization
- Index only what you query
- Keep schemas database-agnostic when possible

## Example Structure
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
