# -*- coding: utf-8 -*-
"""Interface de linha de comando do cenário ferroviário padrão."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import re

from classes.Agents import TrainFlowModel
from classes.functions import extrair_diagonal_principal, zerar_diagonal_principal
import classes.plot as plot
from Configuration.definitions import (
    ITINERARY_TABLE_DEFAULT,
    STATION_TABLE_DEFAULT,
    TRAIN_TABLE_DEFAULT,
)


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "Outputs"


ADJACENCY_MATRIX = [
    [["S_A", "T_A"], 100, 100, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 100, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 100, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, ["S_B", None], 100, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 100, 100, 100, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 100, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 100, 100],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 80],
    [0, 0, 0, 0, 0, 0, 0, 0, ["S_C", None], 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, ["S_D", "T_B"]],
]


def non_negative_int(value):
    """Converte um argumento em inteiro não negativo."""
    parsed_value = int(value)
    if parsed_value < 0:
        raise argparse.ArgumentTypeError("o valor deve ser maior ou igual a zero")
    return parsed_value


def build_parser():
    """Cria o parser da interface de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Executa o cenário ferroviário padrão do Train Dynamics."
    )
    parser.add_argument(
        "--steps",
        type=non_negative_int,
        default=100,
        help="quantidade de passos da simulação (padrão: 100)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="semente aleatória usada pelo modelo",
    )
    parser.add_argument(
        "--traces",
        action="store_true",
        help="habilita a coleta de métricas e a exportação dos CSVs",
    )
    parser.add_argument(
        "--visualization",
        action="store_true",
        help="salva um gráfico PNG após cada passo, sem abrir janelas",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="raiz das execuções geradas (padrão: Outputs na raiz do projeto)",
    )
    parser.add_argument(
        "--run-name",
        default=Path(__file__).stem,
        help="prefixo da pasta da execução (padrão: run)",
    )
    parser.add_argument(
        "--print-state",
        action="store_true",
        help="imprime o estado completo da rede após cada passo",
    )
    return parser


def create_output_structure(output_root, run_name):
    """Cria uma pasta única de execução e suas categorias de artefatos."""
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", run_name).strip("._") or "run"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = output_root.expanduser().resolve()
    run_dir = output_root / f"{safe_name}_{timestamp}"

    suffix = 1
    while run_dir.exists():
        run_dir = output_root / f"{safe_name}_{timestamp}_{suffix:02d}"
        suffix += 1

    directories = {
        "run": run_dir,
        "csv": run_dir / "csv",
        "images": run_dir / "images",
        "other": run_dir / "other",
    }
    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=False)
    return directories


def write_run_metadata(output_dirs, args, model):
    """Registra os parâmetros e o resultado básico da execução em JSON."""
    metadata = {
        "scenario": Path(__file__).name,
        "run_directory": str(output_dirs["run"]),
        "steps_requested": args.steps,
        "steps_completed": model.step_count,
        "seed": args.seed,
        "traces": args.traces,
        "visualization": args.visualization,
        "finished_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    metadata_path = output_dirs["other"] / "run_metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def create_model(log_metrics=False, seed=None):
    """Cria o modelo correspondente ao cenário padrão de ``run.py``."""
    edges_description = zerar_diagonal_principal(ADJACENCY_MATRIX)
    station_nodes, train_nodes = extrair_diagonal_principal(ADJACENCY_MATRIX)

    return TrainFlowModel(
        edges_description,
        station_nodes,
        train_nodes,
        TRAIN_TABLE_DEFAULT,
        STATION_TABLE_DEFAULT,
        ITINERARY_TABLE_DEFAULT,
        LogMetrics=log_metrics,
        seed=seed,
    )


def run_simulation(args):
    """Executa a simulação conforme os argumentos recebidos."""
    output_dirs = None
    if args.traces or args.visualization:
        output_dirs = create_output_structure(args.output_root, args.run_name)
        print(f"Artefatos da execução: {output_dirs['run']}")

    model = create_model(log_metrics=args.traces, seed=args.seed)

    for step in range(args.steps):
        model.step()

        if args.print_state:
            plot.print_network_state(model.grid.G, step)
        if args.visualization:
            image_path = output_dirs["images"] / f"network_step_{step:04d}.png"
            plot.plot_network_state(
                model.grid.G,
                model.G_runtime,
                step,
                output_file=image_path,
                show=False,
            )
    if args.traces:
        model.export_CSV(output_dirs["csv"])

    if output_dirs is not None:
        write_run_metadata(output_dirs, args, model)

    return model


def main(argv=None):
    """Ponto de entrada da interface de linha de comando."""
    args = build_parser().parse_args(argv)
    run_simulation(args)


if __name__ == "__main__":
    main()
