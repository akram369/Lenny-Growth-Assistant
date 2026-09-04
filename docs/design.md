# UI/UX Design Specification
## The Lenny Growth Assistant

**Document Version:** 1.0.0  
**Status:** Approved  
**Author:** Forward Deployed Engineer (FDE)  

---

## 1. Design Philosophy & Core Principles

The Lenny Growth Assistant is an executive intelligence tool built for Product Managers and Growth Leaders. The interface is optimized for speed, clarity, and deep content consumption rather than superficial chat interactions.

### 1.1 Core Principles
1. **Side-by-Side Co-Presence:** Conversations and generated artifacts (essays, calculators, wireframes) must coexist. Users should never have to switch tabs or navigate away to read a 1,250-word essay or test an HTML tool.
2. **First-Class Citations:** Evidence must be tactile and verifiable. Citations appear as clean, clickable badges that reveal exact quotes, timestamps, and episode links without cluttering the main reading flow.
3. **Transparent Model Observability:** The user must always know which model is thinking (Local Ollama vs. Cloud Claude/OpenAI) and have instant 1-click toggle control directly from the header.
4. **Dark Mode & Glassmorphism:** A sleek, developer-grade aesthetic featuring deep slate backgrounds, subtle translucent borders, and focused typography to reduce fatigue during deep work sessions.

---

## 2. Visual Design System & Tokens

### 2.1 Color Palette
- **Background Primary:** `#0a0d14` (Deep obsidian slate)
- **Background Secondary / Cards:** `#111622` (Subtle elevated charcoal)
- **Surface Translucent:** `rgba(255, 255, 255, 0.04)` (Glassmorphic panels)
- **Border / Dividers:** `rgba(255, 255, 255, 0.08)` (Crisp hairline borders)
- **Primary Accent (Lenny Orange / Amber):** `#f59e0b` / `#fbbf24` (Energy, growth, warmth)
- **Secondary Accent (Indigo / Violet):** `#6366f1` (Intelligence, agentic actions)
- **Success / Healthy:** `#10b981` (Online models, high-confidence citations)
- **Text Primary:** `#f8fafc` (High contrast, crisp legibility)
- **Text Muted:** `#94a3b8` (Timestamps, metadata, secondary instructions)

### 2.2 Typography
- **Primary Font:** Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif.
- **Code / Monospace:** JetBrains Mono, Fira Code, "Cascadia Code", Menlo, monospace.
- **Hierarchy:**
  - `h1` (Display): 28px / 36px line-height, bold.
  - `h2` (Section): 20px / 28px line-height, semibold.
  - `h3` (Card): 16px / 24px line-height, medium.
  - Body Text: 14px / 22px line-height, regular.
  - Metadata / Badges: 12px / 16px line-height, medium.

---

## 3. Information Architecture & Layout

The desktop interface utilizes a balanced dual-pane layout with a collapsible navigation sidebar:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Header: [Brand Badge]  [Active Model Toggle: Ollama / Cloud]  [Health Dot]   │
├──────────────┬───────────────────────────────┬──────────────────────────────┤
│ Sidebar      │ Left Pane: Conversational Q&A │ Right Pane: Artifact Viewer  │
│ (Collapsible)│                               │ (Collapsible / Resizable)    │
│              │ ┌───────────────────────────┐ │ ┌──────────────────────────┐ │
│ [+ New Chat] │ │ User: How does Elena Verna│ │ │ [Preview] [Code] [Copy]  │ │
│              │ │ define product-led sales? │ │ ├──────────────────────────┤ │
│ Chat History │ ├───────────────────────────┤ │ │                          │ │
│ • Pricing    │ │ Assistant: [Elena Verna]  │ │ │ Rendered Ship 30 Essay   │ │
│ • Retention  │ │ In B2B growth, sales and  │ │ │ or Sandboxed HTML        │ │
│ • Org Design │ │ product loops converge... │ │ │                          │ │
│              │ │ [Citations: Elena Verna]  │ │ │                          │ │
│              │ └───────────────────────────┘ │ │                          │ │
│              │ ┌───────────────────────────┐ │ │                          │ │
│              │ │ [Ship 30 Essay Action]    │ │ │                          │ │
│              │ │ [Prompt Input Area...]    │ │ └──────────────────────────┘ │
└──────────────┴───────────────────────────────┴──────────────────────────────┘
```

### 3.1 Sidebar (Navigation & Sessions)
- **Width:** 260px (desktop), collapsible to 0px or off-canvas drawer on mobile.
- **Features:** "+ New Chat" CTA, chronological session groupings (Today, Yesterday, Previous 7 Days), session deletion icon, transcript archive ingestion stats.

### 3.2 Conversational Pane (Center)
- **Width:** Flexible (takes 50%–60% when Artifact Viewer is open, 100% when closed).
- **Message List:** Smooth autoscroll, user prompts displayed in subtle pill containers, assistant responses formatted with Markdown, code highlighting, and citation badges.
- **Quick-Action Chips:**
  - *"Generate Ship 30 for 30 Essay"*
  - *"Explain Will Larson's Engineering Mindset"*
  - *"Compare Elena Verna vs. Brian Balfour on Growth"*
  - *"Build an Interactive Pricing Calculator HTML Artifact"*
- **Chat Input Bar:** Multi-line auto-expanding textarea, model badge indicator, keyboard shortcuts (`Enter` to submit, `Shift+Enter` for newline).

### 3.3 Artifact Viewer (Right Drawer)
- **Width:** 45%–50% split screen, with 1-click collapse/expand (`X` close button, maximize button).
- **Tabbed Toolbar:**
  - **Preview Tab:** Native Markdown rendering or sandboxed iframe preview.
  - **Code Tab:** Monospaced source code with syntax highlighting and line numbers.
  - **Copy Action:** 1-click copy with "Copied!" feedback state.
  - **Download Action:** Downloads file with appropriate extension (`.md` or `.html`).
- **Artifact History Switcher:** Dropdown allowing users to toggle between multiple artifacts generated in the same session.

---

## 4. Key Interaction States

1. **Empty / Fresh State:**
   - Welcomes the user with a curated set of starter growth questions.
   - Displays live status indicator of Ollama and PostgreSQL connection.
2. **Retrieval & Ingestion State:**
   - Displays an animated pulse badge: *"Searching Lenny's Podcast archive..."*
3. **Streaming Generation State:**
   - Real-time token streaming with smooth caret animation.
   - Citations pop in smoothly as retrieval metadata arrives.
4. **Artifact Detection & Slide-In:**
   - As soon as `<artifact>` tag is received, the right-hand Artifact Viewer slides in from the right edge with a 250ms ease-out spring animation.
5. **Out-of-Domain Refusal State:**
   - Clean, respectful refusal message explaining that Lenny's archive does not cover the topic, accompanied by suggested related topics.

---

## 5. Security & Accessibility Considerations

### 5.1 Sandboxed HTML Isolation
- The `HtmlSandbox` component wraps generated HTML into a blob URL or `srcdoc` iframe.
- Sandboxed with `allow-scripts` while strictly omitting `allow-same-origin`.
- The iframe contains a top banner indicating: *"Sandboxed Preview (Isolated Origin)"* to give evaluators visual confidence in security boundaries.

### 5.2 Accessibility (WCAG 2.1 AA)
- **Contrast Ratios:** All text elements exceed 4.5:1 contrast against their respective card and body backgrounds.
- **Keyboard Navigation:** Full tab order throughout the chat input, quick chips, session list, and artifact tabs.
- **Focus Rings:** Distinct `#6366f1` focus outline on all interactive inputs and buttons.
