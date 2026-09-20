#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-деревьев множителей. Числа сверяются с ответами ДЗ-17."""
from pathlib import Path

OUT = Path(__file__).resolve().parent

TASKS = {
    1260: [2, 2, 3, 3, 5, 7],
    924:  [2, 2, 3, 7, 11],
    2310: [2, 3, 5, 7, 11],
    6300: [2, 2, 3, 3, 5, 5, 7],
    756:  [2, 2, 3, 3, 3, 7],
    3850: [2, 5, 5, 7, 11],
    882:  [2, 3, 3, 7, 7],
    1575: [3, 3, 5, 5, 7],
}


def factorize(n):
    factors = []
    d = 2
    while n > 1:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
        if d * d > n and n > 1:
            factors.append(n)
            break
    return factors


def fmt(factors):
    return " · ".join(map(str, factors))


def tree_svg(n, factors):
    steps = []
    rest = n
    for p in factors[:-1]:
        rest //= p
        steps.append((p, rest))

    W = 820
    top, vstep = 30, 78
    H = top + (len(steps) + 1) * vstep + 90
    x0 = max(300, 410 - 55 * len(steps))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f"font-family=\"'Segoe UI', Arial, sans-serif\">",
        '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs>',
        f'<rect x="0" y="0" width="{W}" height="{H}" rx="18" fill="#f8faff"/>',
    ]

    boxes = []
    bx, by = x0, top
    boxes.append((bx, by, n))
    circles = []
    lines = []
    for p, q in steps:
        cx, cy = bx - 110, by + vstep
        nx, ny = bx + 70, by + vstep
        lines.append((bx + 60, by + 36, cx, cy - 20))
        lines.append((bx + 80, by + 36, nx + 60, ny - 4))
        circles.append((cx, cy, p))
        boxes.append((nx, ny, q))
        bx, by = nx, ny

    last_x, last_y, last_val = boxes.pop()
    circles.append((last_x + 60, last_y + 20, last_val))

    parts.append('<g stroke="#94a3b8" stroke-width="2.5" fill="none" marker-end="url(#arr)">')
    for x1, y1, x2, y2 in lines:
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    parts.append("</g>")

    parts.append('<g font-size="26" font-weight="700" text-anchor="middle">')
    for x, y, val in boxes:
        parts.append(
            f'<rect x="{x}" y="{y}" width="120" height="40" rx="12" '
            f'fill="#eef2ff" stroke="#4f46e5" stroke-width="2"/>'
            f'<text x="{x + 60}" y="{y + 29}" fill="#3730a3">{val}</text>'
        )
    parts.append("</g>")

    parts.append('<g font-size="26" font-weight="700" text-anchor="middle">')
    for x, y, val in circles:
        parts.append(
            f'<circle cx="{x}" cy="{y}" r="24" fill="#f0fdf4" '
            f'stroke="#16a34a" stroke-width="2.5"/>'
            f'<text x="{x}" y="{y + 9}" fill="#15803d">{val}</text>'
        )
    parts.append("</g>")

    res = f"{n} = {fmt(factors)}"
    rw = max(300, 34 * len(res) // 2 + 80)
    ry = H - 55
    parts.append(
        f'<rect x="{(W - rw) // 2}" y="{ry}" width="{rw}" height="40" rx="12" '
        f'fill="#fffbeb" stroke="#d97706" stroke-width="2"/>'
        f'<text x="{W // 2}" y="{ry + 28}" font-size="24" font-weight="700" '
        f'text-anchor="middle" fill="#92400e">{res}</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    for n, expected in TASKS.items():
        got = factorize(n)
        assert got == expected, f"{n}: расчёт {got} != ответы {expected}"
        prod = 1
        for p in got:
            prod *= p
        assert prod == n
        svg = tree_svg(n, got)
        path = OUT / f"factor-tree-{n}.svg"
        path.write_text(svg, encoding="utf-8")
        print(f"OK {n} = {fmt(got)} -> {path.name}")


if __name__ == "__main__":
    main()
