# Tofino implementation of TurboNet

## 1. Describe your network
Write and run a Python file (cases/emulator.py as an example) to describe the network you want to emulate.

The APIs are described in cases/src/mapper.py and cases/src/topo.py.

The Python file should output a configuration file (YOUR_NAME.log) to the cases/examples folder. 

## 2. Compile and run the P4 code
Compile the P4 program (dataplane/p4src/main.p4) on your P4 switch.

## 3. Install table entries
You can use runtime/turbonet_pd.py to install table entries (by reading YOUR_NAME.log generated in Step 1).