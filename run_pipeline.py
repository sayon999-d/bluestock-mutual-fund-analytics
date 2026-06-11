from __future__ import annotations

import logging
import shutil
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SCRIPTS = [
    BASE_DIR / "scripts" / "data_cleaning.py",
    BASE_DIR / "scripts" / "db_migration.py",
    BASE_DIR / "scripts" / "recommender.py",
]
DB_PATH = BASE_DIR / "data" / "db" / "bluestock_mf.db"
BACKUP_PATH = BASE_DIR / "data" / "db" / "bluestock_mf.backup.sqlite"


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def backup_database_if_exists() -> bool:
    """Create a safety backup of the existing SQLite database before migration.

    Returns:
        True if a backup was created, otherwise False.
    """
    if DB_PATH.exists():
        BACKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(DB_PATH, BACKUP_PATH)
        logging.info("Backed up existing database to %s", BACKUP_PATH)
        return True
    return False


def restore_database_backup(has_backup: bool) -> None:
    if has_backup and BACKUP_PATH.exists():
        shutil.copy2(BACKUP_PATH, DB_PATH)
        logging.warning("Restored database from backup: %s", BACKUP_PATH)
    elif DB_PATH.exists() and not has_backup:
        try:
            DB_PATH.unlink()
            logging.warning("Removed partially created database: %s", DB_PATH)
        except OSError as exc:
            logging.error("Unable to remove partial database %s: %s", DB_PATH, exc)


def run_script(script_path: Path) -> None:
    logging.info("Starting step: %s", script_path.relative_to(BASE_DIR))
    result = subprocess.run(
        [sys.executable, script_path.as_posix()],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.stdout:
        logging.info("STDOUT from %s:\n%s", script_path.name, result.stdout.strip())
    if result.stderr:
        logging.error("STDERR from %s:\n%s", script_path.name, result.stderr.strip())

    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            returncode=result.returncode,
            cmd=[sys.executable, script_path.as_posix()],
            output=result.stdout,
            stderr=result.stderr,
        )

    logging.info("Completed step successfully: %s", script_path.relative_to(BASE_DIR))


def main() -> int:
    configure_logging()
    logging.info("Bluestock master pipeline starting from %s", BASE_DIR)

    if not all(script.exists() for script in SCRIPTS):
        missing = [str(script) for script in SCRIPTS if not script.exists()]
        logging.error("Missing required pipeline scripts: %s", missing)
        return 1

    backup_created = False

    try:
        run_script(SCRIPTS[0])
        backup_created = backup_database_if_exists()
        run_script(SCRIPTS[1])
        run_script(SCRIPTS[2])
    except subprocess.CalledProcessError as exc:
        logging.exception("Pipeline failed at command: %s", exc.cmd)
        restore_database_backup(backup_created)
        logging.error("Pipeline aborted. Review the logs above for the failing step.")
        return exc.returncode or 1
    except Exception as exc:  # pragma: no cover - defensive guard
        logging.exception("Unexpected pipeline error: %s", exc)
        restore_database_backup(backup_created)
        return 1
    finally:
        if BACKUP_PATH.exists():
            try:
                BACKUP_PATH.unlink()
                logging.info("Removed temporary backup: %s", BACKUP_PATH)
            except OSError as exc:
                logging.warning("Could not delete backup file %s: %s", BACKUP_PATH, exc)

    logging.info("Bluestock pipeline completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
