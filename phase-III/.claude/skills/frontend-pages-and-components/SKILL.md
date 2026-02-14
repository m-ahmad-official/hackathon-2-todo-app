---
name: frontend-pages-and-components
description: Build complete frontend pages with reusable components, clean layouts, and modern styling. Use for scalable web applications.
---

# Frontend Pages & Components

## Instructions

1. **Page structure**
   - Semantic HTML layout
   - Clear section separation (header, main, footer)
   - Responsive grid or flex-based structure

2. **Components**
   - Reusable UI components (buttons, cards, navbars)
   - Props-based configuration
   - Isolated and maintainable styles

3. **Layout system**
   - Flexbox and CSS Grid
   - Consistent spacing and alignment
   - Mobile-first responsiveness

4. **Styling**
   - Modern CSS (Flexbox, Grid, variables)
   - Utility-first or component-based styles
   - Hover, focus, and active states

## Best Practices

- Build reusable components first
- Keep components small and focused
- Use consistent spacing and typography
- Design mobile-first, enhance for desktop
- Avoid inline styles for scalability

## Example Structure

```html
<main class="page-container">
  <header class="navbar">
    <h1 class="logo">Brand</h1>
    <nav class="nav-links">
      <a href="#">Home</a>
      <a href="#">About</a>
      <a href="#">Contact</a>
    </nav>
  </header>

  <section class="content-grid">
    <div class="card">
      <h2>Card Title</h2>
      <p>Card description text</p>
      <button class="btn-primary">Action</button>
    </div>
  </section>

  <footer class="footer">
    <p>© 2026 All rights reserved</p>
  </footer>
</main>
```
