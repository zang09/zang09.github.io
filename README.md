# haebeom.com

Personal academic homepage of Haebeom Jung. A single static page with no build step.

## Structure

| Path                    | Purpose                                            |
| ----------------------- | -------------------------------------------------- |
| `index.html`            | The whole site: about, news, publications, honors  |
| `assets/css/style.css`  | Styles (light/dark via CSS variables)              |
| `assets/js/main.js`     | Theme toggle, hover video previews, BibTeX toggles |
| `assets/img/papers/`    | Paper thumbnails: `<name>.jpg` + `.webm` + `.mp4`  |
| `assets/pdf/`           | CV                                                 |
| `publications/`, `cv/`… | Redirect stubs preserving the old al-folio URLs    |

## Editing

- **News**: add an `<li>` to `<ul class="news">` in `index.html` (newest first).
- **Publication**: copy an existing `<li class="pub">` block, drop `name.jpg`, `name.webm`, `name.mp4` into `assets/img/papers/`.
- **Honors**: add an `<li>` to `<ul class="honors">`.
- **CV**: replace `assets/pdf/CV_HaebeomJung.pdf`.

Preview locally with any static server, e.g. `python3 -m http.server 8000`.

## Deploy

Pushing to `main` runs `.github/workflows/deploy.yml`, which checks Prettier formatting and publishes the repository root to the `gh-pages` branch. `CNAME` keeps the custom domain `www.haebeom.com`.

Before pushing, run `npx prettier . --check` (also enforced by the `pre-push` hook in `.githooks/`; enable with `git config core.hooksPath .githooks`).

The previous al-folio (Jekyll) version is preserved on the `al-folio-legacy` branch.
