#!/usr/bin/env python3
"""SVG geometry QA for hand-authored Hermes diagrams.

Checks the failure modes repeatedly found in Scott's SOP flowcharts:
- card/gate bounding boxes overlap
- adjacent card/gate gaps are too small
- text likely overflows the owning card/gate
- connector segments cross card/gate interiors
- connector segments cross layer title bands

The script is intentionally dependency-free and conservative. It is not a full
SVG renderer; it catches geometry mistakes before browser/vision review.

Usage:
    python scripts/svg_geometry_qa.py diagram.svg
    python scripts/svg_geometry_qa.py diagram.svg --json

Author: Hermes Agent
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Optional

SVG_NS_RE = re.compile(r"^\{.*\}")
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")
PATH_CMD_RE = re.compile(r"([ML])\s*(-?\d+(?:\.\d+)?)\s*,?\s*(-?\d+(?:\.\d+)?)", re.I)


def strip_ns(tag: str) -> str:
    return SVG_NS_RE.sub("", tag)


def fnum(value: Optional[str], default: float = 0.0) -> float:
    if value is None:
        return default
    m = NUM_RE.search(str(value))
    return float(m.group(0)) if m else default


def classes(el: ET.Element) -> set[str]:
    return set((el.attrib.get("class") or "").split())


@dataclass
class Box:
    id: str
    kind: str
    x: float
    y: float
    w: float
    h: float

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h

    def contains_point(self, px: float, py: float, pad: float = 0.0) -> bool:
        return self.x - pad <= px <= self.right + pad and self.y - pad <= py <= self.bottom + pad

    def inset(self, amount: float) -> "Box":
        amount = min(amount, max(0.0, self.w / 3), max(0.0, self.h / 3))
        return Box(self.id, self.kind, self.x + amount, self.y + amount, max(0, self.w - 2 * amount), max(0, self.h - 2 * amount))


@dataclass
class Issue:
    severity: str  # FAIL | WARN
    check: str
    message: str
    data: dict


def overlap_area(a: Box, b: Box) -> float:
    dx = min(a.right, b.right) - max(a.x, b.x)
    dy = min(a.bottom, b.bottom) - max(a.y, b.y)
    return max(0.0, dx) * max(0.0, dy)


def rect_intersection(a: Box, b: Box) -> tuple[float, float]:
    return (min(a.right, b.right) - max(a.x, b.x), min(a.bottom, b.bottom) - max(a.y, b.y))


def axis_gap(a: Box, b: Box) -> tuple[float, str]:
    """Return gap and axis if boxes overlap in the other axis."""
    x_overlap = min(a.right, b.right) - max(a.x, b.x)
    y_overlap = min(a.bottom, b.bottom) - max(a.y, b.y)
    if y_overlap > 0:
        if a.right <= b.x:
            return b.x - a.right, "x"
        if b.right <= a.x:
            return a.x - b.right, "x"
    if x_overlap > 0:
        if a.bottom <= b.y:
            return b.y - a.bottom, "y"
        if b.bottom <= a.y:
            return a.y - b.bottom, "y"
    return math.inf, "none"


def text_content(el: ET.Element) -> str:
    parts: list[str] = []
    if el.text:
        parts.append(el.text)
    for child in el:
        parts.append(text_content(child))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts).strip()


def estimate_text_width(s: str, font_size: float) -> float:
    total = 0.0
    for ch in s:
        code = ord(ch)
        if ch.isspace():
            total += font_size * 0.33
        elif (
            0x2E80 <= code <= 0x9FFF
            or 0xF900 <= code <= 0xFAFF
            or 0xFF00 <= code <= 0xFFEF
            or 0x3040 <= code <= 0x30FF
            or 0xAC00 <= code <= 0xD7AF
        ):
            total += font_size * 1.00
        elif ch in "MW@#%&":
            total += font_size * 0.78
        elif ch in "ilI.,'`|!":
            total += font_size * 0.32
        else:
            total += font_size * 0.56
    return total


def parse_points_from_path(d: str) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for _cmd, x, y in PATH_CMD_RE.findall(d or ""):
        pts.append((float(x), float(y)))
    return pts


def segment_intersects_box(p1: tuple[float, float], p2: tuple[float, float], box: Box) -> bool:
    x1, y1 = p1
    x2, y2 = p2
    # Axis-aligned segments are the intended input for Manhattan diagrams.
    if abs(y1 - y2) < 1e-6:
        y = y1
        if not (box.y < y < box.bottom):
            return False
        lo, hi = sorted((x1, x2))
        return max(lo, box.x) < min(hi, box.right)
    if abs(x1 - x2) < 1e-6:
        x = x1
        if not (box.x < x < box.right):
            return False
        lo, hi = sorted((y1, y2))
        return max(lo, box.y) < min(hi, box.bottom)
    # Fallback for diagonal segments: bounding-box overlap heuristic.
    segbox = Box("segment", "segment", min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
    return overlap_area(segbox, box) > 0


def parse_svg(svg_path: Path) -> tuple[ET.Element, dict[ET.Element, ET.Element], list[Box], list[Box]]:
    root = ET.parse(svg_path).getroot()
    parent = {child: el for el in root.iter() for child in el}
    nodes: list[Box] = []
    title_bands: list[Box] = []
    tb_count = 0
    for el in root.iter():
        tag = strip_ns(el.tag)
        cls = classes(el)
        if tag == "g" and ("card" in cls or "gate" in cls):
            if all(k in el.attrib for k in ("data-x", "data-y", "data-w", "data-h")):
                nodes.append(Box(
                    el.attrib.get("id", f"node_{len(nodes)}"),
                    "card" if "card" in cls else "gate",
                    fnum(el.attrib.get("data-x")),
                    fnum(el.attrib.get("data-y")),
                    fnum(el.attrib.get("data-w")),
                    fnum(el.attrib.get("data-h")),
                ))
        if tag == "rect" and "titleBand" in cls:
            tb_count += 1
            title_bands.append(Box(
                el.attrib.get("id", f"titleBand_{tb_count}"),
                "titleBand",
                fnum(el.attrib.get("x")),
                fnum(el.attrib.get("y")),
                fnum(el.attrib.get("width")),
                fnum(el.attrib.get("height")),
            ))
    return root, parent, nodes, title_bands


def owner_node(el: ET.Element, parent: dict[ET.Element, ET.Element], by_element: dict[ET.Element, Box]) -> Optional[Box]:
    cur = parent.get(el)
    while cur is not None:
        if cur in by_element:
            return by_element[cur]
        cur = parent.get(cur)
    return None


def run_qa(svg_path: Path, min_gap: float, right_pad: float, bottom_pad: float, title_band_check: bool = True) -> dict:
    root, parent, nodes, title_bands = parse_svg(svg_path)
    issues: list[Issue] = []
    # Map actual group elements to boxes for text ownership.
    by_element: dict[ET.Element, Box] = {}
    node_by_id = {n.id: n for n in nodes}
    for el in root.iter():
        if strip_ns(el.tag) == "g" and ("card" in classes(el) or "gate" in classes(el)):
            eid = el.attrib.get("id")
            if eid in node_by_id:
                by_element[el] = node_by_id[eid]

    # 1) Node collisions and tight gaps.
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            area = overlap_area(a, b)
            if area > 0.5:
                issues.append(Issue("FAIL", "box_collision", f"{a.id} overlaps {b.id}", {
                    "a": asdict(a), "b": asdict(b), "overlap_area": round(area, 2)
                }))
            else:
                gap, axis = axis_gap(a, b)
                if axis != "none" and gap < min_gap:
                    issues.append(Issue("WARN", "tight_gap", f"{a.id} and {b.id} gap is only {gap:.1f}px on {axis}-axis", {
                        "a": a.id, "b": b.id, "axis": axis, "gap": round(gap, 2), "min_gap": min_gap
                    }))

    # 2) Text overflow inside owning card/gate.
    for el in root.iter():
        if strip_ns(el.tag) != "text":
            continue
        owner = owner_node(el, parent, by_element)
        if owner is None:
            continue
        content = " ".join(text_content(el).split())
        if not content:
            continue
        fs = fnum(el.attrib.get("font-size"), 14.0)
        x = fnum(el.attrib.get("x"), owner.x)
        y = fnum(el.attrib.get("y"), owner.y)
        width = estimate_text_width(content, fs)
        anchor = el.attrib.get("text-anchor", "start")
        if anchor == "middle":
            left, right = x - width / 2, x + width / 2
        elif anchor == "end":
            left, right = x - width, x
        else:
            left, right = x, x + width
        bottom = y + fs * 0.28
        # Right/bottom are the recurring real failures; use hard gates there.
        if right > owner.right - right_pad:
            issues.append(Issue("FAIL", "text_overflow_right", f"text likely exceeds right padding in {owner.id}: {content!r}", {
                "node": owner.id, "text": content, "estimated_right": round(right, 2),
                "allowed_right": round(owner.right - right_pad, 2), "font_size": fs
            }))
        if bottom > owner.bottom - bottom_pad:
            issues.append(Issue("FAIL", "text_overflow_bottom", f"text likely exceeds bottom padding in {owner.id}: {content!r}", {
                "node": owner.id, "text": content, "estimated_bottom": round(bottom, 2),
                "allowed_bottom": round(owner.bottom - bottom_pad, 2), "font_size": fs
            }))
        if left < owner.x - 2:  # allow labels/badges near the edge, but not outside.
            issues.append(Issue("WARN", "text_left_outside", f"text may extend left of {owner.id}: {content!r}", {
                "node": owner.id, "text": content, "estimated_left": round(left, 2), "node_left": owner.x
            }))

    # 3) Connector crossings.
    path_count = 0
    for el in root.iter():
        if strip_ns(el.tag) != "path":
            continue
        pts = parse_points_from_path(el.attrib.get("d", ""))
        if len(pts) < 2:
            continue
        path_count += 1
        path_id = el.attrib.get("id", f"path_{path_count}")
        for p1, p2 in zip(pts, pts[1:]):
            # Cards/gates: ignore intentional entry/exit where an endpoint is on/inside the node.
            for n in nodes:
                if n.contains_point(*p1, pad=2) or n.contains_point(*p2, pad=2):
                    continue
                if segment_intersects_box(p1, p2, n.inset(3)):
                    issues.append(Issue("FAIL", "connector_crosses_node", f"{path_id} segment crosses {n.id}", {
                        "path": path_id, "segment": [p1, p2], "node": n.id
                    }))
            if title_band_check:
                for tb in title_bands:
                    if segment_intersects_box(p1, p2, tb.inset(0)):
                        issues.append(Issue("FAIL", "connector_crosses_title_band", f"{path_id} segment crosses {tb.id}", {
                            "path": path_id, "segment": [p1, p2], "title_band": asdict(tb)
                        }))

    failures = [i for i in issues if i.severity == "FAIL"]
    warnings = [i for i in issues if i.severity == "WARN"]
    return {
        "svg": str(svg_path),
        "status": "PASS" if not failures else "FAIL",
        "nodes": len(nodes),
        "title_bands": len(title_bands),
        "failures": len(failures),
        "warnings": len(warnings),
        "issues": [asdict(i) for i in issues],
    }


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Run deterministic geometry QA on SVG diagrams.")
    ap.add_argument("svg", type=Path, help="SVG file to inspect")
    ap.add_argument("--json", action="store_true", help="Emit JSON report")
    ap.add_argument("--min-gap", type=float, default=24.0, help="Warn when adjacent nodes are closer than this")
    ap.add_argument("--right-pad", type=float, default=16.0, help="Required right padding for estimated text")
    ap.add_argument("--bottom-pad", type=float, default=14.0, help="Required bottom padding for estimated text")
    ap.add_argument("--allow-title-band-crossing", action="store_true", help="Do not fail connectors crossing title bands")
    args = ap.parse_args(argv)

    if not args.svg.exists():
        print(f"ERROR: SVG not found: {args.svg}", file=sys.stderr)
        return 2
    report = run_qa(args.svg, args.min_gap, args.right_pad, args.bottom_pad, not args.allow_title_band_crossing)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"SVG Geometry QA: {report['status']}  nodes={report['nodes']}  failures={report['failures']}  warnings={report['warnings']}")
        for issue in report["issues"][:80]:
            print(f"[{issue['severity']}] {issue['check']}: {issue['message']}")
        if len(report["issues"]) > 80:
            print(f"... {len(report['issues']) - 80} more issues omitted; rerun with --json")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
