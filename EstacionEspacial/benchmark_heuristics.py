#!/usr/bin/env python3
"""
benchmark_heuristics.py

Ejecuta A* con las cuatro heurísticas del Punto 5 sobre layouts/systems y
genera archivos CSV/Markdown con costo, movimientos, nodos expandidos y tiempo.

Coloca este archivo dentro de la carpeta EstacionEspacial (al mismo nivel que main.py).

Uso rápido:
    python benchmark_heuristics.py

Todos los layouts:
    python benchmark_heuristics.py --suite all

Layouts específicos:
    python benchmark_heuristics.py --layouts tinyRepair dualArray triadCorridor

Cambiar timeout:
    python benchmark_heuristics.py --suite all --timeout 120

Cambiar repeticiones:
    python benchmark_heuristics.py --repeats 5
"""

from __future__ import annotations

import argparse
import csv
import multiprocessing as mp
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent
LAYOUTS_DIR = PROJECT_ROOT / "layouts" / "systems"

CORE_LAYOUTS = [
    "tinyRepair",
    "dualArray",
    "triadCorridor",
    "fourCornerArray",
    "sixBayDeck",
    "sevenNodeRing",
    "nineBlockGrid",
]

HEURISTICS = [
    "nullHeuristic",
    "manhattanHeuristic",
    "euclideanHeuristic",
    "systemRepairHeuristic",
]


def count_systems(layout_name: str) -> Optional[int]:
    path = LAYOUTS_DIR / f"{layout_name}.lay"
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="latin-1")
    return text.count("T")


def discover_layouts() -> List[str]:
    if not LAYOUTS_DIR.exists():
        return []
    return sorted(p.stem for p in LAYOUTS_DIR.glob("*.lay"))


def _worker(layout_name: str, heuristic_name: str, output_queue) -> None:
    try:
        os.chdir(PROJECT_ROOT)
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))

        from world import station_layout
        from world.station_state import StationState
        from algorithms.problems import SystemRepairProblem
        from algorithms.search import aStarSearch
        import algorithms.heuristics as heuristics

        heuristic = getattr(heuristics, heuristic_name)
        layout = station_layout.getLayout(layout_name)
        if layout is None:
            raise RuntimeError(f"No se encontró el layout '{layout_name}'")

        mission_state = StationState()
        mission_state.initialize(layout)
        problem = SystemRepairProblem(mission_state)

        start = time.perf_counter()
        actions = aStarSearch(problem, heuristic=heuristic)
        elapsed = time.perf_counter() - start

        if actions is None:
            actions = []

        cost = problem.getCostOfActions(actions)
        moves = len(actions)
        expanded = getattr(problem, "_expanded", None)
        status = "OK" if cost != 999999 else "NO_SOLUTION"

        output_queue.put({
            "status": status,
            "layout": layout_name,
            "heuristic": heuristic_name,
            "cost": cost,
            "moves": moves,
            "nodes_expanded": expanded,
            "time_s": elapsed,
            "error": "",
        })
    except Exception as exc:
        output_queue.put({
            "status": "ERROR",
            "layout": layout_name,
            "heuristic": heuristic_name,
            "cost": "",
            "moves": "",
            "nodes_expanded": "",
            "time_s": "",
            "error": f"{type(exc).__name__}: {exc}",
        })


def run_once(layout_name: str, heuristic_name: str, timeout_s: float) -> Dict:
    ctx = mp.get_context("spawn")
    queue = ctx.Queue()
    process = ctx.Process(target=_worker, args=(layout_name, heuristic_name, queue))
    process.start()
    process.join(timeout_s)

    if process.is_alive():
        process.terminate()
        process.join()
        return {
            "status": "TIMEOUT",
            "layout": layout_name,
            "heuristic": heuristic_name,
            "cost": "",
            "moves": "",
            "nodes_expanded": "",
            "time_s": timeout_s,
            "error": f"Superó {timeout_s:.1f} s",
        }

    if not queue.empty():
        return queue.get()

    return {
        "status": "ERROR",
        "layout": layout_name,
        "heuristic": heuristic_name,
        "cost": "",
        "moves": "",
        "nodes_expanded": "",
        "time_s": "",
        "error": f"Proceso terminó con código {process.exitcode} sin devolver resultado",
    }


def summarize_runs(layout_name: str, heuristic_name: str, t_count: Optional[int], runs: List[Dict]) -> Dict:
    ok_runs = [r for r in runs if r["status"] == "OK"]

    if ok_runs:
        times = [float(r["time_s"]) for r in ok_runs]
        costs = [int(r["cost"]) for r in ok_runs]
        moves = [int(r["moves"]) for r in ok_runs]
        expanded = [int(r["nodes_expanded"]) for r in ok_runs]

        return {
            "layout": layout_name,
            "systems_T": t_count if t_count is not None else "",
            "heuristic": heuristic_name,
            "cost": costs[0] if len(set(costs)) == 1 else min(costs),
            "moves": moves[0] if len(set(moves)) == 1 else min(moves),
            "nodes_expanded": expanded[0] if len(set(expanded)) == 1 else int(statistics.median(expanded)),
            "time_median_s": statistics.median(times),
            "time_mean_s": statistics.mean(times),
            "time_min_s": min(times),
            "successful_runs": len(ok_runs),
            "attempted_runs": len(runs),
            "status": "OK",
            "notes": "",
        }

    statuses = [r["status"] for r in runs]
    if "TIMEOUT" in statuses:
        status = "TIMEOUT"
    elif "NO_SOLUTION" in statuses:
        status = "NO_SOLUTION"
    else:
        status = "ERROR"

    errors = sorted({str(r.get("error", "")) for r in runs if r.get("error")})
    return {
        "layout": layout_name,
        "systems_T": t_count if t_count is not None else "",
        "heuristic": heuristic_name,
        "cost": "",
        "moves": "",
        "nodes_expanded": "",
        "time_median_s": "",
        "time_mean_s": "",
        "time_min_s": "",
        "successful_runs": 0,
        "attempted_runs": len(runs),
        "status": status,
        "notes": " | ".join(errors),
    }


def write_csv(path: Path, rows: List[Dict], fieldnames: List[str]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value, decimals=6) -> str:
    if value == "" or value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.{decimals}f}"
    return str(value)


def write_markdown(path: Path, summary: List[Dict]) -> None:
    lines = [
        "# Resultados A* y heurísticas",
        "",
        "| Layout | T | Heurística | Costo | Movimientos | Nodos expandidos | Tiempo mediano (s) | Estado |",
        "|---|---:|---|---:|---:|---:|---:|---|",
    ]

    for row in summary:
        lines.append(
            f"| {row['layout']} | {fmt(row['systems_T'],0)} | {row['heuristic']} | "
            f"{fmt(row['cost'],0)} | {fmt(row['moves'],0)} | {fmt(row['nodes_expanded'],0)} | "
            f"{fmt(row['time_median_s'],6)} | {row['status']} |"
        )

    lines += [
        "",
        "## Validación de costos",
        "",
        "Si A* está bien implementado y las heurísticas son admisibles, las ejecuciones exitosas de un mismo layout deberían producir el mismo costo óptimo.",
        "",
    ]

    by_layout: Dict[str, List[Dict]] = {}
    for row in summary:
        by_layout.setdefault(row["layout"], []).append(row)

    for layout, rows in by_layout.items():
        ok = [r for r in rows if r["status"] == "OK" and r["cost"] != ""]
        costs = sorted({int(r["cost"]) for r in ok})
        if len(costs) == 1 and ok:
            lines.append(f"- **{layout}:** costos consistentes ({costs[0]}).")
        elif len(costs) > 1:
            lines.append(f"- **{layout}: ADVERTENCIA:** costos distintos entre heurísticas: {costs}.")
        else:
            lines.append(f"- **{layout}:** sin suficientes ejecuciones exitosas para validar.")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark de A* con las heurísticas del Punto 5.")
    parser.add_argument("--suite", choices=["core", "all"], default="core")
    parser.add_argument("--layouts", nargs="+", help="Layouts específicos; reemplaza --suite")
    parser.add_argument("--timeout", type=float, default=60.0, help="Máximo de segundos por ejecución")
    parser.add_argument("--repeats", type=int, default=None, help="Repeticiones por combinación")
    parser.add_argument("--output-prefix", default="resultados_heuristicas")
    args = parser.parse_args()

    if not (PROJECT_ROOT / "main.py").exists():
        print("ERROR: coloca benchmark_heuristics.py dentro de EstacionEspacial, al mismo nivel que main.py.", file=sys.stderr)
        sys.exit(1)

    available = discover_layouts()
    if not available:
        print("ERROR: no se encontraron archivos en layouts/systems.", file=sys.stderr)
        sys.exit(1)

    if args.layouts:
        layouts = args.layouts
    elif args.suite == "all":
        layouts = available
    else:
        layouts = [name for name in CORE_LAYOUTS if name in available]

    missing = [name for name in layouts if name not in available]
    if missing:
        print("ERROR: layouts no encontrados: " + ", ".join(missing), file=sys.stderr)
        sys.exit(1)

    repeats = args.repeats
    if repeats is None:
        repeats = 1 if args.suite == "all" and not args.layouts else 5
    if repeats < 1:
        print("ERROR: --repeats debe ser >= 1", file=sys.stderr)
        sys.exit(1)

    detailed_rows: List[Dict] = []
    summary_rows: List[Dict] = []
    total_combinations = len(layouts) * len(HEURISTICS)
    combination_index = 0

    print("=" * 76)
    print("BENCHMARK A* - PUNTO 5")
    print(f"Layouts: {len(layouts)} | Heurísticas: {len(HEURISTICS)} | Repeticiones: {repeats}")
    print(f"Timeout por ejecución: {args.timeout:.1f} s")
    print("=" * 76)

    for layout_name in layouts:
        t_count = count_systems(layout_name)

        for heuristic_name in HEURISTICS:
            combination_index += 1
            print(f"\n[{combination_index}/{total_combinations}] {layout_name} (T={t_count}) / {heuristic_name}")
            runs: List[Dict] = []

            for repeat in range(1, repeats + 1):
                print(f"  repetición {repeat}/{repeats}...", end=" ", flush=True)
                result = run_once(layout_name, heuristic_name, args.timeout)
                result["repeat"] = repeat
                result["systems_T"] = t_count if t_count is not None else ""
                runs.append(result)
                detailed_rows.append(result)

                if result["status"] == "OK":
                    print(
                        f"OK | costo={result['cost']} | nodos={result['nodes_expanded']} | "
                        f"tiempo={float(result['time_s']):.6f}s"
                    )
                else:
                    print(f"{result['status']} | {result.get('error', '')}")

                if repeat == 1 and result["status"] in {"TIMEOUT", "ERROR", "NO_SOLUTION"}:
                    if repeats > 1:
                        print("  Se omiten las repeticiones restantes de esta combinación.")
                    break

            summary_rows.append(summarize_runs(layout_name, heuristic_name, t_count, runs))

    detailed_path = PROJECT_ROOT / f"{args.output_prefix}_detallado.csv"
    summary_path = PROJECT_ROOT / f"{args.output_prefix}_tabla.csv"
    markdown_path = PROJECT_ROOT / f"{args.output_prefix}_tabla.md"

    detailed_fields = [
        "layout", "systems_T", "heuristic", "repeat", "status", "cost", "moves",
        "nodes_expanded", "time_s", "error"
    ]
    summary_fields = [
        "layout", "systems_T", "heuristic", "cost", "moves", "nodes_expanded",
        "time_median_s", "time_mean_s", "time_min_s", "successful_runs",
        "attempted_runs", "status", "notes"
    ]

    write_csv(detailed_path, detailed_rows, detailed_fields)
    write_csv(summary_path, summary_rows, summary_fields)
    write_markdown(markdown_path, summary_rows)

    print("\n" + "=" * 76)
    print("ARCHIVOS GENERADOS")
    print(f"- {detailed_path.name}: cada ejecución individual")
    print(f"- {summary_path.name}: tabla final resumida")
    print(f"- {markdown_path.name}: tabla lista para copiar al informe")
    print("=" * 76)

    print("\nVALIDACIÓN DE COSTOS POR LAYOUT")
    for layout_name in layouts:
        rows = [
            r for r in summary_rows
            if r["layout"] == layout_name and r["status"] == "OK" and r["cost"] != ""
        ]
        costs = sorted({int(r["cost"]) for r in rows})
        if len(costs) == 1:
            print(f"  {layout_name}: OK, costo óptimo común = {costs[0]}")
        elif len(costs) > 1:
            print(f"  {layout_name}: ADVERTENCIA, costos distintos {costs}. Revisar A* o la heurística propia.")
        else:
            print(f"  {layout_name}: sin suficientes resultados exitosos.")


if __name__ == "__main__":
    mp.freeze_support()
    main()
