# Resultados A* y heurísticas

| Layout | T | Heurística | Costo | Movimientos | Nodos expandidos | Tiempo mediano (s) | Estado |
|---|---:|---|---:|---:|---:|---:|---|
| tinyRepair | 1 | nullHeuristic | 24 | 24 | 148 | 0.000438 | OK |
| tinyRepair | 1 | manhattanHeuristic | 24 | 24 | 127 | 0.000413 | OK |
| tinyRepair | 1 | euclideanHeuristic | 24 | 24 | 129 | 0.000463 | OK |
| tinyRepair | 1 | systemRepairHeuristic | 24 | 24 | 66 | 0.000343 | OK |
| dualArray | 2 | nullHeuristic | 50 | 50 | 284 | 0.000797 | OK |
| dualArray | 2 | manhattanHeuristic | 50 | 50 | 263 | 0.000862 | OK |
| dualArray | 2 | euclideanHeuristic | 50 | 50 | 263 | 0.000958 | OK |
| dualArray | 2 | systemRepairHeuristic | 50 | 50 | 242 | 0.001213 | OK |
| triadCorridor | 3 | nullHeuristic | 68 | 68 | 817 | 0.002377 | OK |
| triadCorridor | 3 | manhattanHeuristic | 68 | 68 | 705 | 0.002374 | OK |
| triadCorridor | 3 | euclideanHeuristic | 68 | 68 | 734 | 0.002854 | OK |
| triadCorridor | 3 | systemRepairHeuristic | 68 | 68 | 528 | 0.003121 | OK |
| fourCornerArray | 4 | nullHeuristic | 78 | 78 | 2305 | 0.006758 | OK |
| fourCornerArray | 4 | manhattanHeuristic | 78 | 78 | 1972 | 0.006995 | OK |
| fourCornerArray | 4 | euclideanHeuristic | 78 | 78 | 2053 | 0.008537 | OK |
| fourCornerArray | 4 | systemRepairHeuristic | 78 | 78 | 1008 | 0.007184 | OK |
| sixBayDeck | 6 | nullHeuristic | 114 | 114 | 14473 | 0.047735 | OK |
| sixBayDeck | 6 | manhattanHeuristic | 114 | 114 | 13220 | 0.053079 | OK |
| sixBayDeck | 6 | euclideanHeuristic | 114 | 114 | 13472 | 0.066672 | OK |
| sixBayDeck | 6 | systemRepairHeuristic | 114 | 114 | 4872 | 0.051509 | OK |
| sevenNodeRing | 7 | nullHeuristic | 127 | 127 | 37249 | 0.131442 | OK |
| sevenNodeRing | 7 | manhattanHeuristic | 127 | 127 | 35252 | 0.151028 | OK |
| sevenNodeRing | 7 | euclideanHeuristic | 127 | 127 | 35638 | 0.192987 | OK |
| sevenNodeRing | 7 | systemRepairHeuristic | 127 | 127 | 13343 | 0.163626 | OK |
| nineBlockGrid | 9 | nullHeuristic | 162 | 162 | 190992 | 0.781897 | OK |
| nineBlockGrid | 9 | manhattanHeuristic | 162 | 162 | 185546 | 0.972472 | OK |
| nineBlockGrid | 9 | euclideanHeuristic | 162 | 162 | 186937 | 1.208130 | OK |
| nineBlockGrid | 9 | systemRepairHeuristic | 162 | 162 | 62488 | 1.117351 | OK |

## Validación de costos

Si A* está bien implementado y las heurísticas son admisibles, las ejecuciones exitosas de un mismo layout deberían producir el mismo costo óptimo.

- **tinyRepair:** costos consistentes (24).
- **dualArray:** costos consistentes (50).
- **triadCorridor:** costos consistentes (68).
- **fourCornerArray:** costos consistentes (78).
- **sixBayDeck:** costos consistentes (114).
- **sevenNodeRing:** costos consistentes (127).
- **nineBlockGrid:** costos consistentes (162).