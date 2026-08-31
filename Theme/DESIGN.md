---
name: Crested Intelligence
colors:
  surface: '#f9faf6'
  surface-dim: '#dadad7'
  surface-bright: '#f9faf6'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f1'
  surface-container: '#eeeeeb'
  surface-container-high: '#e8e8e5'
  surface-container-highest: '#e2e3e0'
  on-surface: '#1a1c1a'
  on-surface-variant: '#414844'
  inverse-surface: '#2f312f'
  inverse-on-surface: '#f1f1ee'
  outline: '#717973'
  outline-variant: '#c1c8c2'
  surface-tint: '#3f6654'
  primary: '#1d4434'
  on-primary: '#ffffff'
  primary-container: '#355c4a'
  on-primary-container: '#a8d3bc'
  inverse-primary: '#a6d0b9'
  secondary: '#486552'
  on-secondary: '#ffffff'
  secondary-container: '#c7e8d0'
  on-secondary-container: '#4c6956'
  tertiary: '#5b3231'
  on-tertiary: '#ffffff'
  tertiary-container: '#764847'
  on-tertiary-container: '#f8bab8'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#c1ecd5'
  primary-fixed-dim: '#a6d0b9'
  on-primary-fixed: '#002114'
  on-primary-fixed-variant: '#274e3d'
  secondary-fixed: '#caead2'
  secondary-fixed-dim: '#afceb7'
  on-secondary-fixed: '#042012'
  on-secondary-fixed-variant: '#314d3b'
  tertiary-fixed: '#ffdad8'
  tertiary-fixed-dim: '#f5b7b5'
  on-tertiary-fixed: '#331111'
  on-tertiary-fixed-variant: '#663b3a'
  background: '#f9faf6'
  on-background: '#1a1c1a'
  surface-variant: '#e2e3e0'
  ink: '#17201F'
  mineral: '#F3F1EA'
  bone: '#FAF9F5'
  graphite: '#59615E'
  clay: '#A56F55'
  mist: '#D9DDD7'
  critical: '#B9534B'
  success: '#4F765E'
  dark-canvas: '#111716'
  dark-surface: '#18201E'
  dark-elevated: '#202925'
  dark-text: '#E8ECE7'
  dark-muted: '#9BA7A0'
  dark-brand: '#7FA88E'
  dark-accent: '#B98468'
typography:
  page-title:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  section-title:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '600'
    lineHeight: '1.3'
  card-title:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  metadata:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.01em
  ai-response:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.75'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  margin-canvas: 2rem
  gutter: 1.5rem
  sidebar-width: 260px
  header-height: 64px
---

# CleverCrest — Distinctive UI Design System
## `design.md` — Stitch UI Direction

Purpose: This document defines the visual identity and UI rules for CleverCrest. Use it as the primary visual-design instruction when generating or refining CleverCrest screens.

Core requirement: Do NOT use generic SaaS presets such as default blue enterprise, orange/sand themes, or neon cyberpunk themes. CleverCrest must have its own recognizable visual language.

---

# 1. Product Personality

CleverCrest is a secure organizational AI knowledge platform.

The visual identity should communicate:

- intelligent, but not futuristic
- premium, but not luxurious
- technical, but approachable
- secure, but not intimidating
- calm, but not boring
- structured, but not rigid
- modern, but not trend-dependent

The UI should feel like a product between:
**editorial knowledge software + enterprise operations software + intelligent AI assistant**

It should NOT look like:
- a generic admin dashboard
- a banking dashboard
- a crypto/Web3 interface
- a gaming UI
- a cyberpunk AI interface
- a colorful education app
- a copy of Notion
- a copy of Linear
- a copy of NotebookLM
- a generic Tailwind template

The design should remain recognizable even if the CleverCrest logo and text are removed.

---

# 2. Signature Visual Concept — "Crested Intelligence"

Use the visual concept **Crested Intelligence**.

The name CleverCrest should subtly influence the visual language.

Do NOT use literal crown illustrations everywhere.

Instead, use a restrained geometric motif based on:
- a rising crest
- two converging planes
- an asymmetric peak
- a subtle shield/crest silhouette
- layered knowledge blocks

Use this motif subtly in:
- empty states
- section dividers
- active navigation indicators
- loading states
- authentication artwork
- AI response accents
- background patterns

Keep it abstract, geometric, and restrained.

---

# 3. Color Philosophy

Do not use a conventional white-background + blue-primary-button system.
Do not use a conventional beige + orange system.
Do not use black + neon cyan/purple cyberpunk styling.

Use a **warm mineral-neutral foundation with a deep ink accent and a controlled botanical intelligence accent**.

Core palette:

- Ink: `#17201F` — primary text, strong headings, dark navigation
- Deep Moss: `#355C4A` — primary brand accent, primary actions, active navigation, AI identity
- Living Sage: `#789681` — subtle highlights and supporting indicators
- Mineral: `#F3F1EA` — main application canvas
- Bone: `#FAF9F5` — cards, panels, inputs, modals
- Graphite: `#59615E` — secondary text
- Clay: `#A56F55` — warnings/attention and selected metadata, used sparingly
- Mist: `#D9DDD7` — borders and dividers
- Critical: `#B9534B` — errors
- Success: `#4F765E` — success

The interface should remain mostly **Ink + Mineral + Bone + Deep Moss**. Use Clay and semantic colors only where needed.

---

# 4. Dark Mode

Dark mode must not simply invert the light theme.

Use a warm charcoal foundation:

- Dark Canvas: `#111716`
- Dark Surface: `#18201E`
- Dark Elevated: `#202925`
- Dark Text: `#E8ECE7`
- Dark Muted: `#9BA7A0`
- Dark Brand: `#7FA88E`
- Dark Accent: `#B98468`

Dark mode should feel like **a quiet studio at night**, not a hacker terminal.

No neon glow.

---

# 5. Background Treatment

Avoid completely flat backgrounds.

Use:
- extremely subtle mineral texture
- faint radial tonal variation
- occasional soft crest geometry
- almost invisible grid/line structures

The background effect should be noticed only subconsciously.

Never use obvious gradients.
Never use large colorful blobs.

Content must remain dominant.

---

# 6. Typography

Preferred font:
**Plus Jakarta Sans**

Alternative:
**Manrope**

Do not use overly futuristic fonts.

Typography should feel intelligent, editorial, premium, and readable.

Suggested hierarchy:
- Page title: 28–34px
- Section title: 20–24px
- Card title: 15–18px
- Body: 14–15px
- Metadata: 12–13px
- Large AI response: 15–16px with generous line height

Avoid excessive font-weight changes.

---

# 7. Layout Philosophy

CleverCrest should NOT feel like a traditional admin panel where every area is boxed.

Use:
**open canvas + structured surfaces**

rather than:
**boxes inside boxes inside boxes**

The layout should breathe.

Use a desktop-first responsive SaaS structure with:
- quiet sidebar
- compact header
- open main content canvas
- contextual surfaces only where useful

---

# 8. Navigation Design

Use a quiet navigation rail/sidebar.

Do not use heavy filled navigation pills for every item.

Default:
- transparent/background-neutral
- subtle text
- small icon
- restrained spacing

Active state:
- thin Deep Moss asymmetric vertical marker
- subtle tinted background
- slightly stronger typography

Create a unique active-state shape inspired by the crest motif rather than the common blue rounded rectangle.

---

# 9. Cards

Avoid excessive cards.

Use cards only when content needs grouping.

Cards:
- Bone surface
- Mist border
- very soft shadow
- 10–14px radius
- generous internal spacing

Avoid:
- huge rounded cards
- heavy shadows
- colorful card backgrounds
- gradient cards

Prefer editorial information blocks over decorative KPI tiles.

---

# 10. Buttons

Primary:
- Deep Moss background
- light text
- medium radius
- compact height

Secondary:
- Bone/transparent
- Mist border
- Ink text

Tertiary:
- text-only action
- Deep Moss hover

Destructive:
- restrained red

Avoid pill-shaped buttons except compact tags/filters.

---

# 11. Inputs and Forms

Inputs should feel like quiet document fields.

Use:
- Bone background
- Mist border
- 9–10px radius
- subtle Deep Moss focus treatment
- clear labels
- helpful descriptions

Do not use bright blue browser-like focus rings.

---

# 12. Tables

Tables are important for:
- Documents
- Members
- Roles
- Approvals
- Audit Logs
- Processing Jobs

Use an editorial data-table style.

Header:
- small muted labels
- generous horizontal spacing

Rows:
- subtle separators
- no excessive boxes
- faint Mineral hover

Status should use compact semantic badges.

Do not use bright rainbow badges.

---

# 13. Status Language

Use consistent semantic colors:

- Approved → Deep Moss / Success
- Processing → Sage
- Pending → Clay
- Rejected → Critical
- Draft → Graphite
- Archived → muted Graphite
- Failed → Critical

Never rely only on color; combine color with text and/or an icon.

---

# 14. AI Assistant — Signature Experience

The AI Assistant is the visual centerpiece of CleverCrest.

It must NOT look like a normal ChatGPT clone and must NOT look like NotebookLM.

It should feel like **asking an intelligent organizational knowledge system**.

Empty state:
- subtle crest-inspired geometric mark
- minimal composition
- calm copy
- prominent composer

Do not use:
- robot icons
- glowing brains
- excessive AI sparkles
- futuristic neon graphics

Example copy:

**CleverCrest**
Ask about your organization's knowledge.

Composer:
**Ask CleverCrest anything...**

Suggested prompts:
- Summarize the latest policy
- Explain the project requirements
- What is the process for requesting leave?
- Generate questions from available knowledge
- Explain this topic in simple terms

---

# 15. AI Composer

Make the composer one of the strongest components.

Use:
- Bone surface
- Mist border
- subtle elevation
- Deep Moss send button
- optional attachment/context icon
- keyboard shortcut hint

It should be large enough to feel important but not oversized.

---

# 16. AI Messages

User messages should be compact.

AI messages should be spacious and editorial.

Do not trap AI answers inside giant rounded colored bubbles.

Use:

CleverCrest

Answer content with:
- paragraphs
- headings
- bullets
- numbered lists
- tables where useful

Then:

Sources used
- Leave Policy · Version 2 · Approved
- Employee Handbook · Version 1 · Approved

---

# 17. Source References

Sources are metadata for normal users.

Users must NOT receive confidential document contents simply because a source was used.

Use a compact metadata treatment such as:

**Sources used**
- Leave Policy — Version 2
- Employee Handbook — Version 1

Do not make sources look like document previews.

---

# 18. Collection Visual Language

Collections are logical knowledge groups, not generic file-system folders.

They should feel like **knowledge shelves**.

Example:
- HR Policies
- Projects
- IT Guidelines
- Company Information
- Accountancy
- Economics

Use subtle abstract icons based on:
- stacked planes
- crest
- grid
- document layers

Do not use emoji.

---

# 19. Document Management

Documents are controlled organizational knowledge assets, not merely files.

Show:
- file type icon
- document name
- collection
- uploader
- status
- version
- updated time
- actions

Avoid making the interface look like Google Drive.

---

# 20. Upload Experience

The upload interface should feel like a controlled knowledge-intake process.

Use an elegant drop zone with a subtle crest motif.

Concept:

Add knowledge

Drop files here or browse

PDF · DOCX · PPTX · XLSX · Images

Then:
- Collection
- Optional description
- Submit for approval

Do not expose embeddings/vector databases/RAG concepts to normal users.

---

# 21. Approval Queue

Approval is a core CleverCrest concept.

The UI should feel like a content-governance console.

Show:
- queue count
- document metadata
- uploader
- collection
- submission time
- review actions

Review screen:
- file information
- uploader
- collection
- version
- upload date
- approval history
- reviewer
- status
- approve
- reject

Only authorized reviewers should see review content.

---

# 22. Processing Jobs

Use a clean processing timeline:

Upload
↓
Extract
↓
Chunk
↓
Embed
↓
Index
↓
Knowledge Ready

Completed stages use the success/moss language.
Current stage uses Living Sage.
Failed stages use Critical.

Use the crest motif subtly as the progress indicator.

No spinning rainbow loaders.

---

# 23. Dashboard

The dashboard should have an editorial introduction.

Example:

Good morning.

Here's what is happening across your organization.

Then useful operational metrics:
- Members
- Collections
- Documents
- Pending Approvals
- Processing Jobs
- AI Conversations

Include recent activity and operational sections.

Do not fill the first screen with many colorful KPI cards.

---

# 24. Authentication

Authentication screens should use a split/asymmetric composition rather than a plain centered login card.

Left:
- CleverCrest identity
- subtle crest geometry
- short product statement

Right:
- Login/Register form

No stock illustrations.

No generic AI artwork.

Authentication should feel premium but simple.

---

# 25. Icons

Use one coherent icon family.

Recommended:
**Lucide Icons**

Use consistent stroke-based icons.

Do not mix:
- emoji
- random SVG styles
- filled and outline icon families

Icons should communicate meaning.

---

# 26. Motion

Motion should be subtle.

Use animation for:
- page transitions
- dropdowns
- modals
- toast notifications
- AI response appearance
- processing progress

Micro-interactions approximately 150–250ms.

No bouncing.
No glowing AI effects.
No constant movement.

---

# 27. Border Radius

Use restrained rounding:

- Buttons: 8px
- Inputs: 9px
- Cards: 12px
- Large panels: 14px
- Modals: 16px
- Pills: only tags/statuses

Avoid making every component extremely rounded.

---

# 28. Shadows

Use very soft shadows.

Borders should carry most visual separation.

Do not use dark, heavy shadows.

---

# 29. Responsive Design

Desktop-first but fully responsive.

Desktop:
- persistent sidebar
- large content canvas
- multi-column layouts

Tablet:
- collapsible sidebar
- reduced table columns

Mobile:
- compact header
- drawer navigation
- stacked content
- responsive tables
- strong mobile AI composer

Do not merely shrink desktop layouts; recompose them.

---

# 30. Accessibility

Include:
- sufficient contrast
- visible keyboard focus
- meaningful labels
- icon + text where necessary
- no color-only meaning
- readable text sizes
- logical tab order

---

# 31. Product Rules That Must Influence UI

1. Users cannot directly browse confidential knowledge unless their role explicitly permits it.
2. Normal users primarily interact with knowledge through the AI Assistant.
3. Documents can require approval before becoming AI knowledge.
4. Only approved and successfully processed documents become available to RAG.
5. AI retrieval respects organization and permission boundaries.
6. Collections organize knowledge but do not automatically grant access.
7. Admins can create custom roles and permissions.
8. Audit logs record important administrative and knowledge-management activity.
9. Do not expose ChromaDB, embeddings, vector indexes or RAG implementation details to ordinary users.
10. The product must feel like a professional SaaS platform, not a student demo.

---

# 32. MVP Screens

Prioritize these screens first:

1. Login
2. Register
3. Email Verification
4. Dashboard
5. AI Assistant
6. Collections
7. Collection Details
8. Documents
9. Upload Document
10. Approval Queue
11. Processing Jobs
12. Members
13. Roles & Permissions
14. Access Requests
15. Notifications
16. Audit Logs
17. Settings

Do not overcrowd the MVP with future functionality.

---

# 33. Future Extensibility

Keep the design system extensible for future modules such as:
- advanced analytics
- AI evaluation
- knowledge quality scoring
- hybrid search
- document version comparison
- advanced access policies
- AI memory improvements
- multiple AI models
- model routing
- educational learning intelligence
- generated assessments
- MCQ generation
- organization-level AI insights
- enterprise integrations

Do not build these now.

---

# 34. Stitch Generation Rules

When generating any CleverCrest screen:

- Preserve the same color system.
- Preserve the same typography.
- Preserve the same sidebar and header.
- Preserve the same button language.
- Preserve the same status badges.
- Preserve the same radius system.
- Preserve the same spacing system.
- Reuse components across screens.
- Do not invent new visual styles for individual pages.
- Do not introduce new primary colors.
- Avoid obvious gradients.
- Do not use generic SaaS illustrations.
- Do not use stock photography.
- Do not use cartoon AI characters.
- Do not use glowing brain/robot graphics.
- Do not copy NotebookLM or ChatGPT UI patterns.
- Keep the result practical for React + Vite + TypeScript + Tailwind CSS.

Every screen must look like it belongs to the same product.

---

# 35. Final Design Statement

CleverCrest should look like:

**"A calm, intelligent command center for organizational knowledge."**

Not:

**"Another AI chatbot."**

The strongest visual impression should be:

**quiet confidence + intelligent structure + controlled knowledge.**

The interface should feel memorable without trying too hard to be futuristic.
