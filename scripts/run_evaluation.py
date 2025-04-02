from pathlib import Path
import subprocess
import time
from typing import Dict

# Example Command:
# command = 'timeout 60 cargo run --release -- --cores 1-10 on-chain -a "0x983EFCA0Fd5F9B03f75BbBD41F4BeD3eC20c96d8" -b "latest"'


def get_contracts(directory: Path):
    contracts = []

    for file in directory.glob("**/*.txt"):
        with file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("https://etherscan.io/"):
                    contracts.append(
                        {
                            "address": line.split("/")[4].split("?")[0],
                            "blocknum": "latest",
                        }
                    )
    for file in directory.glob("**/defihacklabs_list.txt"):
        with file.open("r", encoding="utf-8") as f:
            for line in f:
                temp = [s.strip() for s in line.split(",")]
                contracts.append(
                    {
                        "address": temp[0],
                        "blocknum": temp[1],
                    }
                )

    return contracts


def run_contract_analysis(contract: Dict):
    address = contract["address"]
    blocknum = contract["blocknum"]
    contract_path = Path(address)

    if contract_path.is_dir():
        print(f"Skipping existing directory: {address}")
        return

    contract_path.mkdir(parents=True, exist_ok=True)
    output_file = contract_path / "output.txt"

    command = f'timeout 60 cargo run --release -- --cores 1-16 -o "{contract_path}/" on-chain -a "{address}" -b "{blocknum}"'
    with open(contract_path / "command.txt", "w") as f:
        f.write(command)

    print(f"Running command: {command}")

    start_time = time.time()

    try:
        with output_file.open("wb") as out:
            subprocess.run(
                command, shell=True, stdout=out, stderr=subprocess.STDOUT, check=True
            )
    except subprocess.CalledProcessError as e:
        print(f"Error processing {contract}: {e}")
    finally:
        elapsed_time = time.time() - start_time
        print(f"Completed {contract} in {elapsed_time:.2f} seconds")


def main():
    contract_dir = Path("eval_targets/contracts")
    contracts = get_contracts(contract_dir)

    for contract in contracts:
        run_contract_analysis(contract)


if __name__ == "__main__":
    main()
