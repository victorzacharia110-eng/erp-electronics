# ERP Electronics Store (Frontend)

Vue 3 single-page application for the ERP Electronics Store — an e-commerce storefront, role-based dashboards (owner, employee, customer, superadmin, supplier), and back-office tools (inventory, accounting, commissions, reports, employee management).

## Documentation

Generated PDF documentation lives in [`docs/`](docs/):

- `User_Manual_EN.pdf` / `User_Manual_SW.pdf` — end-user manuals (English & Swahili)
- `Supplier_Manual_EN.pdf` / `Supplier_Manual_SW.pdf` — supplier portal manuals (English & Swahili)
- `Developer_Documentation.pdf` — developer & technical documentation (architecture, brand identity, API, superadmin module, security, deployment)
- `*_Documentation.pdf` — PDF companions for the diagrams below
- `*.drawio` — ERD, class, use case, and sequence diagrams (open in [diagrams.net](https://app.diagrams.net))

Regenerate the PDFs from the repo root:

```sh
python3 generate_manual.py           # user manuals
python3 generate_supplier_manual.py  # supplier manuals
python3 generate_dev_doc.py          # developer documentation
python3 generate_diagrams.py         # drawio diagrams + their PDF companions
```

Full developer notes: [`MyDocumentationNotes/PROJECT.md`](MyDocumentationNotes/PROJECT.md).

## Recommended IDE Setup

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Recommended Browser Setup

- Chromium-based browsers (Chrome, Edge, Brave, etc.):
  - [Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
  - [Turn on Custom Object Formatter in Chrome DevTools](http://bit.ly/object-formatters)
- Firefox:
  - [Vue.js devtools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)
  - [Turn on Custom Object Formatter in Firefox DevTools](https://fxdx.dev/firefox-devtools-custom-object-formatters/)

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

### Run Unit Tests with [Vitest](https://vitest.dev/)

```sh
npm run test:unit
```

### Run End-to-End Tests with [Playwright](https://playwright.dev)

```sh
# Install browsers for the first run
npx playwright install

# When testing on CI, must build the project first
npm run build

# Runs the end-to-end tests
npm run test:e2e
# Runs the tests only on Chromium
npm run test:e2e -- --project=chromium
# Runs the tests of a specific file
npm run test:e2e -- tests/example.spec.ts
# Runs the tests in debug mode
npm run test:e2e -- --debug
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```
