# philjay.cc

The static site behind https://philjay.cc. The home page lists the projects, `mpandroidchart/` is the landing page for the chart library. Plain HTML and CSS, no build step.

Preview locally with `python3 -m http.server 8000` in this folder and open http://localhost:8000.

Deploys as GitHub Pages from the `master` branch, root folder. The `CNAME` file binds the custom domain.
