import sys
import subprocess
from datetime import datetime
from pathlib import Path

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

log_file = log_dir / "drift_history.log"


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")

print("Automated Infrastructure Drift Management")
print("-----------------------------------------")

print("Checking infrastructure state...")

plan = subprocess.run(
    ["terraform", "plan", "-detailed-exitcode", "-no-color"],
    capture_output=True,
    text=True
)

if plan.returncode == 0:
    print("STATUS: Infrastructure is healthy. No drift detected.")
    log("Infrastructure healthy - no drift detected.")

elif plan.returncode == 2:
    print("STATUS: Drift detected.")
    log("Infrastructure drift detected.")
    
    print("Starting automatic correction...")
    

    apply = subprocess.run(
        ["terraform", "apply", "-auto-approve", "-no-color"],
        capture_output=True,
        text=True
    )

    if apply.returncode == 0:
        print("STATUS: Drift correction completed.")
        log("Drift correction completed.")

        verify = subprocess.run(
            ["terraform", "plan", "-detailed-exitcode", "-no-color"],
            capture_output=True,
            text=True
        )

        if verify.returncode == 0:
            print("VERIFICATION: Infrastructure restored successfully.")
            log("Verification successful - infrastructure restored.")
        else:
            print("VERIFICATION: Infrastructure still has differences.")
            log("Verification failed - infrastructure still has differences.")
            sys.exit(1)

    else:
        print("STATUS: Automatic correction failed.")
        print(apply.stderr)
        log("Automatic correction failed.")
        sys.exit(1)

else:
    print("STATUS: Error while checking infrastructure.")
    print(plan.stderr)
    log("Error while checking infrastructure.")
    sys.exit(1)