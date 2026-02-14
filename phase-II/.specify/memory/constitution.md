<!-- SYNC IMPACT REPORT:
Version change: N/A -> 1.0.0
Modified principles: N/A (new constitution)
Added sections: All sections
Removed sections: None
Templates requiring updates: ✅ .specify/templates/plan-template.md, ✅ .specify/templates/spec-template.md, ✅ .specify/templates/tasks-template.md
Follow-up TODOs: None
-->
# Todo Full-Stack Web Application Constitution

## Core Principles

### Reliability
All backend API endpoints must handle data correctly and consistently.
- Backend API endpoints must follow consistent request/response patterns
- Data validation and error handling must be implemented for all operations
- Database transactions must maintain ACID properties for data integrity
- Services must be designed to handle failures gracefully with appropriate fallbacks

### Security
User data is isolated, and authentication is enforced via JWT.
- All API endpoints require valid JWT tokens for access (except public auth endpoints)
- User data must be properly isolated so users can only access their own resources
- Authentication must be implemented using Better Auth with secure JWT tokens
- Secrets must be stored in environment variables, never hardcoded in source code

### Usability
Frontend is responsive and intuitive across devices.
- Frontend components must be responsive and work well on mobile, tablet, and desktop
- User interfaces must follow accessibility best practices
- Navigation and interaction patterns must be intuitive and consistent
- Loading states and error messages must be clearly communicated to users

### Maintainability
Code is modular, reusable, and follows best practices for Next.js + FastAPI + SQLModel.
- Code organization must follow established patterns for each technology stack
- Components and modules should be reusable and follow separation of concerns
- Code must include appropriate documentation and type hints where applicable
- Architecture must support easy maintenance and future enhancements

### Spec-Driven Development
All implementations follow the Agentic Dev Stack workflow (Spec → Plan → Tasks → Claude Code).
- All development must follow the prescribed workflow: Specification → Planning → Task breakdown → Implementation
- Manual coding outside the Spec-Kit Plus workflow is prohibited
- All changes must be traceable through the agentic development process
- Commit history must reflect the iterative nature of spec-driven development

### API Standards

API endpoints follow RESTful conventions and database operations are transactional and validated.
- RESTful endpoints must follow standard HTTP methods and status codes
- Database operations must use SQLModel with proper validation and error handling
- Frontend components must be responsive and tested for user flows
- Code must be version-controlled with clear commit history following conventional commits

## Key Standards

- API endpoints follow RESTful conventions with proper HTTP methods and status codes
- JWT tokens securely authenticate all requests post-authentication
- Database operations are transactional and validated using SQLModel
- Frontend components are responsive and tested for user flows across devices
- Code is version-controlled with clear commit history and follows conventional commits
- No manual coding outside the Spec-Kit Plus workflow (Spec → Plan → Tasks → Claude Code)

## Constraints

- Backend: Python FastAPI + SQLModel + Neon PostgreSQL
- Frontend: Next.js 16+ (App Router)
- Authentication: Better Auth with JWT tokens
- All API calls require valid JWT tokens post-authentication
- No hardcoded secrets; use environment variables exclusively
- Spec-driven iterative development only (no direct manual coding)
- All implementations must follow the Agentic Dev Stack workflow

## Success Criteria

- All CRUD operations functional and user-specific with proper authentication
- JWT authentication implemented and enforced for all API endpoints
- Frontend displays tasks per user correctly, with full CRUD and completion toggle
- Responsive UI across desktop and mobile devices with intuitive navigation
- End-to-end workflow demonstrable via agentic prompts and iterations
- No security or data integrity issues detected in testing
- Complete traceability from specification through implementation

## Governance

- This constitution supersedes all other development practices and guidelines
- All code reviews must verify compliance with these principles and constraints
- Any deviation from these principles requires explicit approval and documentation
- Amendments to this constitution require formal proposal, discussion, and approval process
- Use Spec-Kit Plus tools and Claude Code for all development activities

**Version**: 1.0.0 | **Ratified**: 2026-02-04 | **Last Amended**: 2026-02-04