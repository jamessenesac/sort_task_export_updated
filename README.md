# sort_task_export

This repository now provides a small toolchain for organizing task export
archives and visualizing the results.

## Prerequisites

* Python 3.9 or later
* `pip` for installing Python dependencies

Install the required Python packages (BeautifulSoup for HTML parsing):

```bash
pip install -r requirements.txt
```

## 1. Build the consolidated task index

Run the parser against the directory that contains the extracted HTML export.
You can execute it from the root of this repository:

```bash
python tools/build_task_index.py /path/to/task-export
```

Key behaviour:

* Every `*.html` file under the export directory is parsed for metadata such as
  task ID, label, result, severity, and timestamps.
* The consolidated data is written to `data/tasks.json` by default (pass
  `--output-json` to override). You can also emit a CSV file with
  `--output-csv data/tasks.csv` if desired.
* The `source_path` field in the JSON points back to the original HTML file,
  relative to the export directory, so you can click through from the dashboard.

Re-run the command whenever you download a fresh export.

## 2. Explore results in the dashboard

The dashboard is a static HTML page located at `web/index.html`. It loads the
JSON index produced in step 1 and renders a sortable, filterable table using
DataTables. Rows are colour coded to highlight failures (red), warnings (amber),
and pending/running jobs (teal).

To view the dashboard, launch a small HTTP server from the repository root so
that the browser can fetch `data/tasks.json`:

```bash
python -m http.server 8000
```

Then open <http://localhost:8000/web/index.html> in your browser. Use the
Result/Severity dropdowns and the built-in DataTables search box to focus on the
items you care about. Clicking a Task ID or Source link opens the original HTML
report in a new tab.

---

The legacy `sort_task_export.bash` script is still available if you want to
perform manual filesystem sorting, but the JSON index + dashboard workflow above
is now the recommended approach.
