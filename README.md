# philjay.cc

The static site behind https://philjay.cc. The home page lists the projects, `mpandroidchart/` is the landing page for the chart library. Plain HTML and CSS. The stylesheets live in `styles.css` and `mpandroidchart/docs.css` and are stamped into every page so nothing blocks the first paint. Run `python3 _inline_css.py` after editing one; `docs/_build.py` does that for the guide pages itself.

Preview locally with `python3 -m http.server 8000` in this folder and open http://localhost:8000.

Deploys as GitHub Pages from the `master` branch, root folder. The `CNAME` file binds the custom domain.

The German pages live under `de/`: the home page, the MPAndroidChart page and the legal pages. They are hand written copies of the English pages, so a text change goes into both. The guides stay English only. `consent.js` picks the banner language from the `lang` of the page.

`llms.txt` describes the site for AI agents. `docs/_build.py` also writes every chapter as `index.md` next to its page and all chapters into `mpandroidchart/docs/llms-full.txt`.
