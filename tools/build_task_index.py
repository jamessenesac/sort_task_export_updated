#!/usr/bin/env python3
"""Build a consolidated JSON/CSV index of task exports.

The tool walks an export directory, extracts task metadata from every
``*.html`` file, and writes ``data/tasks.json`` (and optionally a CSV).

It understands a handful of common HTML patterns (``<dt>/<dd>``,
``<table>`` rows, ``<strong>`` labels) so that the index works with the
existing export format without requiring manual sorting.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from bs4 import BeautifulSoup


LABEL_ALIASES: Dict[str, Sequence[str]] = {
    "task_id": ("Task ID", "TaskID", "ID"),
    "label": ("Label",),
    "result": ("Result", "Status"),
    "severity": ("Severity", "Level"),
    "created_at": ("Created At", "Created", "Creation Time"),
    "updated_at": ("Updated At", "Updated", "Last Updated"),
    "started_at": ("Started At", "Started", "Start Time"),
    "completed_at": ("Completed At", "Completed", "Finish Time"),
    "timestamp": ("Timestamp", "Time", "Date"),
}

TEXT_FALLBACK_REGEX = {
    key: tuple(
        re.compile(rf"{re.escape(label)}\s*[:|-]\s*(?P<value>.+)", re.IGNORECASE)
        for label in labels
    )
    for key, labels in LABEL_ALIASES.items()
}


@dataclass
class TaskRecord:
    """Representation of a parsed task file."""

    source_path: str
    task_id: Optional[str] = None
    label: Optional[str] = None
    result: Optional[str] = None
    severity: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    timestamp: Optional[str] = None
    extra: Dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Optional[str]]:
        data = {
            "source_path": self.source_path,
            "task_id": self.task_id,
            "label": self.label,
            "result": self.result,
            "severity": self.severity,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "timestamp": self.timestamp,
        }
        data.update(self.extra)
        return data


def normalise_label(label: str) -> str:
    return label.strip().rstrip(":").lower()


def update_record(record: TaskRecord, label: str, value: str) -> None:
    label_key = normalise_label(label)
    value = value.strip()
    if not value:
        return

    for field, aliases in LABEL_ALIASES.items():
        if any(label_key == alias.lower().rstrip(":") for alias in aliases):
            current = getattr(record, field)
            if not current:
                setattr(record, field, value)
            return

    # Store any labels we don't explicitly understand under ``extra``.
    if label_key not in record.extra:
        record.extra[label] = value


def iter_label_value_pairs(soup: BeautifulSoup) -> Iterable[Tuple[str, str]]:
    # Definition lists
    for dt in soup.find_all("dt"):
        dd = dt.find_next_sibling("dd")
        if dd is not None:
            yield dt.get_text(" ", strip=True), dd.get_text(" ", strip=True)

    # Table rows (<th>/<td> or <td> label/value)
    for row in soup.find_all("tr"):
        headers = row.find_all("th")
        data_cells = row.find_all("td")
        if len(headers) == 1 and data_cells:
            yield headers[0].get_text(" ", strip=True), " ".join(
                cell.get_text(" ", strip=True) for cell in data_cells
            )
        elif not headers and len(data_cells) >= 2:
            yield data_cells[0].get_text(" ", strip=True), " ".join(
                cell.get_text(" ", strip=True) for cell in data_cells[1:]
            )

    # Inline labels using <strong> or <b>
    for label_tag in soup.find_all(["strong", "b", "span"]):
        text = label_tag.get_text(" ", strip=True)
        if text.endswith(":"):
            value = ""
            sibling = label_tag.next_sibling
            while sibling and not value:
                if hasattr(sibling, "get_text"):
                    value = sibling.get_text(" ", strip=True)
                else:
                    value = str(sibling).strip()
                sibling = sibling.next_sibling
            if value:
                yield text.rstrip(":"), value


def fallback_from_text(record: TaskRecord, text_content: str) -> None:
    for line in text_content.splitlines():
        line = line.strip()
        if not line:
            continue
        for field, patterns in TEXT_FALLBACK_REGEX.items():
            if getattr(record, field):
                continue
            for pattern in patterns:
                match = pattern.search(line)
                if match:
                    setattr(record, field, match.group("value").strip())
                    break


def parse_task_file(html_path: Path, export_root: Path) -> TaskRecord:
    record = TaskRecord(source_path=str(html_path.relative_to(export_root)))
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")

    for label, value in iter_label_value_pairs(soup):
        update_record(record, label, value)

    # If key information is still missing, fall back to raw text parsing.
    fallback_from_text(record, soup.get_text("\n", strip=True))

    if not record.task_id:
        record.task_id = html_path.stem

    return record


def write_json(records: Sequence[TaskRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump([record.as_dict() for record in records], fh, indent=2, sort_keys=True)
        fh.write("\n")


def write_csv(records: Sequence[TaskRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [record.as_dict() for record in records]
    if not rows:
        header = ["source_path"]
    else:
        header = list(rows[0].keys())
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=header)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build_index(export_dir: Path, output_json: Path, output_csv: Optional[Path]) -> List[TaskRecord]:
    html_files = sorted(export_dir.rglob("*.html"))
    records = [parse_task_file(path, export_dir) for path in html_files]

    write_json(records, output_json)
    if output_csv:
        write_csv(records, output_csv)

    return records


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Build a consolidated task index from HTML exports.")
    parser.add_argument(
        "export_dir",
        nargs="?",
        default=".",
        type=Path,
        help="Directory containing the extracted task export (defaults to current directory).",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("data/tasks.json"),
        help="Path to write the consolidated JSON file (default: data/tasks.json).",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        help="Optional path to write a CSV version of the index.",
    )

    args = parser.parse_args(argv)

    export_dir = args.export_dir.resolve()
    if not export_dir.exists():
        raise SystemExit(f"Export directory not found: {export_dir}")

    records = build_index(export_dir, args.output_json.resolve(), args.output_csv and args.output_csv.resolve())
    print(f"Indexed {len(records)} task(s) from {export_dir}")


if __name__ == "__main__":
    main()
