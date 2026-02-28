from dataclasses import dataclass

@dataclass
class GeneratorConfig:

    start_year: int = 2018
    end_year: int = 2025
    mrns_per_year: int = 100
    workers: int = 8
    chunksize: int = 10
    out_root_dir: str = "./out"
    remove_existing_files: int = 1
    seed: int | None = 42

    # Validator related
    validate: int = 0
    validator_path: str = "./validator/validator_cli.jar" # path to validator_cli.jar
    uscore_root: str = "./validator/package_v8.0.1_R4" # path to uscore profiles    
