import os
import subprocess
import re
import argparse


Migration1='''
pragma solidity ^0.4.2;

contract Migrations {
  address public owner;
  uint public last_completed_migration;

  modifier restricted() {
    if (msg.sender == owner) _;
  }

  constructor() public {
    owner = msg.sender;
  }

  function setCompleted(uint completed) public restricted {
    last_completed_migration = completed;
  }

  function upgrade(address new_address) public restricted {
    Migrations upgraded = Migrations(new_address);
    upgraded.setCompleted(last_completed_migration);
  }
}

'''

truffe_config='''
module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "*",
      gas: 1000000000
    }
  },
  compilers: {
     solc: {
       version: "0.4.25",
       optimizer: {
         enabled: true,
         runs: 200
       }
     }
  }
};
'''

initial = '''
var Migrations = artifacts.require("./Migrations.sol");

module.exports = function(deployer) {
  deployer.deploy(Migrations);
};

'''

deploym ='''
var contract = artifacts.require("Crowdsale"); 
module.exports = function(deployer) {
   deployer.deploy(contract);
};

'''

# Regular expression to match the Solidity pragma version
pragma_pattern = re.compile(r"pragma solidity \^?(\d+\.\d+\.\d+);")

def is_pragma_valid(sourcecode):
    # Search for the pragma version in the source code
    match = pragma_pattern.search(sourcecode)
    if match:
        # Extract the version number from the match
        version = match.group(1)
        # Split the version into major, minor, patch for comparison
        major, minor, patch = map(int, version.split('.'))
        # Check if the version is >= 0.4.16
        if (major > 0) or (major == 0 and minor > 4) or (major == 0 and minor == 4 and int(str(patch)[0]) >= 2):
            return True
    return False

def create_sol_files(input_folder, output_folder):
    # Read the CSV file
    index = 0
    for root, _, files in os.walk(input_folder):
        print(files)
        for file in files:
            index += 1
            if file.endswith(".sol"):

                # Read the source code from the file
                sourcecode = open(os.path.join(root, file), 'r', encoding='utf-8').read()

                # Create the folder if it doesn't exist
                folder_path = output_folder

                contract_folder_path = os.path.join(folder_path, str(index))

                cc_path = os.path.join(contract_folder_path, "contracts")
                migrations_path = os.path.join(contract_folder_path, "migrations")

                os.makedirs(folder_path, exist_ok=True)
                os.makedirs(contract_folder_path, exist_ok=True)
                os.makedirs(cc_path, exist_ok=True)
                os.makedirs(migrations_path, exist_ok=True)

                # Create the .sol file
                file_name = file
                #contract
                file_path = os.path.join(cc_path, file_name)
                
                migrations= os.path.join(cc_path, "Migrations.sol")
                truffle=os.path.join(contract_folder_path, "truffle-config.js")

                initial_migration=os.path.join(migrations_path, "1_initial_migration.js")
                deploy_migration=os.path.join(migrations_path, "2_deploy_contracts.js")

                with open(migrations, 'w', encoding='utf-8') as f:
                    f.write(Migration1)
                
                with open(truffle, 'w', encoding='utf-8') as f:
                    f.write(truffe_config)
                
                with open(initial_migration, 'w', encoding='utf-8') as f:
                    f.write(initial)
                
                with open(deploy_migration, 'w', encoding='utf-8') as f:
                    f.write(deploym)

                # Write the source code to the file with UTF-8 encoding
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(sourcecode)

                print(f"Created: {file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create .sol files from CSV")
    parser.add_argument("-i", "--input", required=True, help=".sol file folder")
    parser.add_argument("-o", "--output", required=True, help="Output folder name")
    args = parser.parse_args()

    create_sol_files(args.input, args.output)
