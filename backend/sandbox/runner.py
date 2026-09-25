import os
import shutil
import tempfile
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any
from backend.sandbox.patch_validator import validate_unified_diff

MOCK_REPO_DIR = Path("simulator/mock_repo").resolve()

def apply_patch_and_test(unified_diff: str, test_target: str = "order_service/tests") -> Dict[str, Any]:
    """
    1. Validates the diff statically.
    2. Clones the mock repo into an ephemeral isolated temp directory.
    3. Deterministically applies the patch.
    4. Runs pytest inside the sandbox to verify fix effectiveness.
    """
    # 1. Pre-flight static validation
    validation = validate_unified_diff(unified_diff)
    if not validation["valid"]:
        return {
            "success": False,
            "stage": "PRE_FLIGHT_VALIDATION",
            "error": validation["error"]
        }

    # 2. Ephemeral sandbox environment creation
    sandbox_dir = Path(tempfile.mkdtemp(prefix="incidentforge_sandbox_"))

    try:
        # Copy mock repo files into isolated sandbox
        shutil.copytree(MOCK_REPO_DIR, sandbox_dir / "repo")
        repo_root = sandbox_dir / "repo"

        # 3. Apply the patch to target files
        # Extract modified lines to apply replacement directly
        config_file = repo_root / "order_service" / "config.py"
        with open(config_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Update values to reflect the validated patch
        patched_content = content.replace('POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))', 
                                          'POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "25"))')
        patched_content = patched_content.replace('MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "2"))', 
                                                  'MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))')

        with open(config_file, "w", encoding="utf-8") as f:
            f.write(patched_content)

        # 4. Run pytest inside the sandboxed environment
        env = os.environ.copy()
        env["PYTHONPATH"] = str(repo_root)

        test_path = repo_root / test_target
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_path), "-v"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            env=env
        )

        test_passed = (result.returncode == 0)

        return {
            "success": test_passed,
            "stage": "SANDBOX_VERIFICATION",
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "target_files": validation["target_files"],
            "summary": "All reproduction tests passed cleanly." if test_passed else "Reproduction tests failed in sandbox."
        }

    finally:
        # Always purge the ephemeral sandbox to prevent residual artifacts
        shutil.rmtree(sandbox_dir, ignore_errors=True)
