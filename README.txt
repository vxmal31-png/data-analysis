QUANTIX-STYLE FLASK DASHBOARD REBUILD
====================================

Package contents
----------------
templates/base.html                 Updated Quantix-style application shell
 templates/index.html               Updated dashboard with reference-style sample content
 templates/analytics.html           Existing visitor analytics page (preserved)
 templates/prediction.html           Existing model prediction form (preserved)
 templates/dataset.html              Existing dataset page (preserved)
 templates/performance.html          Existing model performance page (preserved)
 templates/about.html               Existing about page (preserved)
static/css/style.css                New full stylesheet for the Quantix-style interface
static/js/quantix-dashboard.js      Sidebar/theme controls and sample revenue donut chart

Installation
------------
1. Back up your current templates/ and static/css/style.css.
2. Copy the templates/ folder from this package into your Flask project, replacing
   the corresponding templates. The five non-dashboard templates are included
   unchanged from the supplied archive.
3. Copy static/css/style.css into your project's static/css/style.css.
4. Copy static/js/quantix-dashboard.js into your project's static/js/ folder.
5. Keep your existing static/js/script.js. It is deliberately not replaced because
   it was not included in the upload and may contain your dataset/prediction API logic.
6. Keep app.py, model files, CSV/JSON data, and all existing Flask routes unchanged.
7. Restart Flask and hard-refresh the browser (Ctrl+F5).

Important notes
---------------
- The main Dashboard (/ route) now contains illustrative Quantix-style sample figures
  and sample system integrations, as requested. These are presentation/demo values,
  not live billing, CRM, or integration data.
- Existing Visitor AI routes and template variables are retained in the supplied
  non-dashboard pages. Sidebar items such as Payment, Product, Invoice, Settings,
  Security, and Help are visual labels mapped onto the closest existing Visitor AI
  pages because no separate routes for those products were supplied.
- The original app.py and static/js/script.js were not uploaded. Therefore this package
  does not alter or claim to validate the Python backend or the existing prediction
  and dataset JavaScript workflows.
- Chart.js and Google Fonts are loaded from CDNs as in the supplied project setup;
  internet access is needed for those external assets. The dashboard's flow diagram,
  cards, gradients, and decorations are CSS/SVG/HTML and need no extra image files.
