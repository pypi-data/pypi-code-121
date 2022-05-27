"""Main script to run others as subcommands."""
import fire

from .generate_schema import gen_schema
from .run_modeller import run as modeller_run
from .run_pod import run as pod_run
from .run_testing import evaluate_model


def main() -> None:
    """Main script entry point."""
    fire.Fire(
        {
            "generate_schema": gen_schema,
            "run_modeller": modeller_run,
            "run_pod": pod_run,
            "run_testing": evaluate_model,
        }
    )


if __name__ == "__main__":
    main()
