"""Main module."""
import logging


def set_up_logging():
    logging.basicConfig(
        level="INFO",
        encoding="UTF-8",
        format="%(asctime)s %(threadName)s %(levelname)s: %(message)s",
        datefmt="%d/%b/%Y %I:%M %p",
    )


def main():
    import sys
    from . import extraviadoscli
    set_up_logging()
    try:
        extraviadoscli.run()
        sys.exit(0)
    except KeyboardInterrupt:
        logging.info("execution stopped")
        sys.exit(0)
    except Exception:
        logging.exception("execution failure")
        sys.exit(1)


if __name__ == "__main__":
    main()
