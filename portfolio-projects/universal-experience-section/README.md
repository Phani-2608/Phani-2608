# Universal PayPal + Cigna experience section

A reusable, self-contained section designed from the public Experience content on https://phanindra26.netlify.app/ (reviewed October 31, 2026), combined with the user's previously confirmed interview/resume details.

## Open / integrate

- **preview.html** — open locally to see the complete, responsive, interactive section.
- **experience-section.html** — one copy-paste HTML snippet, with *scoped* CSS and plain JavaScript; replace the existing `<section id="experience"> ... </section>` with it. It does **not** include a page header or footer.
- **experience-evidence.json** — canonical, job-neutral facts to preserve across future resume variants.
- **resume-tailoring-guide.md** — how to select evidence per job without changing the facts.

The component requires no frameworks, paid services, API keys, analytics, CDN, or build step. `?focus=data#experience`, `?focus=ml#experience`, `?focus=genai#experience`, `?focus=health#experience`, and `?focus=risk#experience` select a lens. It uses semantic section/article/list/button markup, keyboard-accessible controls, `aria-pressed`, and `prefers-reduced-motion`.

### Important integration details

1. Back up the old site source before replacing its Experience section.
2. Preserve the site's existing section anchor `#experience`. The component contains it already.
3. Ensure there are **not two elements with `id="experience"`** on the page.
4. If using React, Vue, or an Astro component, *adapt* the HTML rather than pasting an executable `<script>` into JSX. The JavaScript is written for ordinary static HTML and is included inside the snippet.
5. It is intentionally not linked to a particular target resume: the employer, title, employment dates, metrics, and factual claims never change; a lens only reorders which evidence appears first.
6. The card's GitHub link points to the overall profile rather than suggesting employer-owned code is public. Keep personal projects distinct from work done at PayPal/Cigna.
7. Review any self-reported impact metrics against underlying records or interview evidence before publishing. The live site contains several precise claims that are not independently verifiable from public code.

### Editorial improvements versus the original website

- Corrected the misleading attribution of the **32% fraud false-positive reduction** to "GenAI transaction monitoring." The supported story is customer-cohort analysis and segmented risk thresholds.
- Kept **PayPal Generative AI Engineer** and **Cigna Healthcare Machine Learning Engineer** with fixed, known dates; removed the vague "Cigna (Client Engagement)" label.
- Replaced the unverified claim that imaging work enabled radiologists to handle **3× more cases per shift** with a narrower model-evaluation statement.
- Added a distinction between clinical **BioBERT / ClinicalBERT extraction** and generative LLM work.
- Made every specialization a selectable display focus instead of changing or rewriting history to match a job.

### What is **not** done

This is a fully built, local website section, **not a deployed modification of phanindra26.netlify.app**. The source repo for the Netlify website was not identified among the GitHub repositories connected in this conversation. A deployment requires access to that site's source (or Netlify deployment configuration).