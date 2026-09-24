# haebeom.com

Personal academic homepage of Haebeom Jung. A single static page with no build step.

## Structure

| Path                                | Purpose                                            |
| ----------------------------------- | -------------------------------------------------- |
| `index.html`                        | Home: hero, bio, latest news, selected pubs/honors |
| `news/`, `publications/`, `honors/` | Full-list pages (each an `index.html`)             |
| `assets/css/style.css`              | Styles (light/dark via CSS variables)              |
| `assets/js/main.js`                 | Theme toggle, hover video previews, BibTeX toggles |
| `assets/img/papers/`                | Paper thumbnails: `<name>.jpg` + `.webm` + `.mp4`  |
| `assets/pdf/`                       | CV                                                 |
| `cv/`, `honors_and_awards/`         | Redirect stubs preserving old al-folio URLs        |

## Editing

The home page shows a subset (latest 4 news, selected honors); the sub-pages show everything. Content lives in plain HTML, so an item that should appear in both places is added in both files.

- **News**: add an `<li>` to `<ul class="news">` in `news/index.html`, and to `index.html` if it is among the latest 4 (remove the oldest there).
- **Publication**: copy an existing `<li class="card pub">` block into `publications/index.html` (and `index.html` if selected); drop `name.jpg`, `name.webm`, `name.mp4` into `assets/img/papers/`.
- **Honors**: add an `<li class="card">` to `<ul class="honors">` in `honors/index.html` (year-descending), and to `index.html` if selected.
- **Nav**: the header is duplicated in each page; keep the four copies in sync.
- **CV**: replace `assets/pdf/CV_HaebeomJung.pdf`.

Preview locally with any static server, e.g. `python3 -m http.server 8000`.

## Deploy

Pushing to `main` runs `.github/workflows/deploy.yml`, which checks Prettier formatting and publishes the repository root to the `gh-pages` branch. `CNAME` keeps the custom domain `www.haebeom.com`.

Before pushing, run `npx prettier . --check` (also enforced by the `pre-push` hook in `.githooks/`; enable with `git config core.hooksPath .githooks`).

The previous al-folio (Jekyll) version is preserved on the `al-folio-legacy` branch.
