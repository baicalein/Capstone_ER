import os
import argparse
from .config import GeneratorConfig
from .generator import run_generation


def parse_args():
    p = argparse.ArgumentParser(description="US Core synthetic FHIR data generator")

    sub = p.add_subparsers(dest="command")

    # -------------------------
    # generate command
    # -------------------------
    gen = sub.add_parser("generate")
    gen.add_argument("--start-year", type=int, default=2018)
    gen.add_argument("--end-year", type=int, default=2025)
    gen.add_argument("--mrns-per-year", type=int, default=100)
    gen.add_argument("--workers", type=int, default=8)
    gen.add_argument("--chunksize", type=int, default=10)
    gen.add_argument("--out-root-dir", type=str, default="./out")
    gen.add_argument("--remove-existing-files", type=int, default=1, choices=[0,1])
    gen.add_argument("--seed", type=int, default=42)
    # Validator related - it takes a long time to validate
    gen.add_argument("--validate", type=int, default=0, choices=[0,1]) # validator uses profiles in uscore-root
    gen.add_argument("--validator-path", type=str, default="./validator/validator_cli.jar") # path to validator_cli.jar
    gen.add_argument("--uscore-root", type=str, default="./validator/package_v8.0.1_R4") # path to profiles

    return p.parse_args()


def main():
    args = parse_args()

    if args.command == "generate":
        cfg = GeneratorConfig(
            start_year=args.start_year,
            end_year=args.end_year,
            mrns_per_year=args.mrns_per_year,
            workers=args.workers,
            chunksize=args.chunksize,
            out_root_dir=args.out_root_dir,
            remove_existing_files=args.remove_existing_files,
            seed=args.seed,
            validate=args.validate,
            validator_path=args.validator_path,
            uscore_root=args.uscore_root,
        )

        run_generation(cfg)

    else: 
        print(f"Use as: \n'$ poetry run uscore-synth generate'")
