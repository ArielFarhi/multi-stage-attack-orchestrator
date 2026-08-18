# Multi-Stage Attack Orchestrator

A Python framework that selects and runs a compatible multi-stage attack, then
extracts files from a simulated device over TCP. The simulator is written in C.

## Design

- `Device` describes the model, iOS version, and battery level.
- `Stage` has a name and an estimated probability of success.
- `Attack` contains an ordered, configurable list of stages and compatibility
  constraints.
- `AttackSelector` filters incompatible attacks and ranks the rest by total
  estimated success probability. The total is the product of the individual
  stage probabilities, assuming independent stages.
- `AttackOrchestrator` tries ranked attacks in order. A failed stage stops that
  attack immediately; the next compatible attack is then attempted.
- `DeviceClient` is the boundary between the framework and a device.
  `TCPDeviceClient` implements it using the simulator's protocol.
- `Extractor` reads one file or all files exposed by the device.

Stages can run without a device client for unit testing of the probabilistic
model. In an integrated run, stage names are sent to the device and the device's
result is authoritative; probabilities rank attacks rather than causing a
second random decision.

`AttackOrchestrator.run_and_extract()` connects the complete workflow: select an
attack, run its stages, and extract all files after success. A normal stage
failure allows fallback to another attack. A transport failure raises
`ConnectionError` because device state is unknown and retrying may be unsafe.

## TCP protocol

The client connects to `127.0.0.1:9000` by default. The simulator also accepts a
port as its first argument. Each request and response is one newline-delimited
JSON object.

| Operation | Request | Successful response |
| --- | --- | --- |
| Device info | `{"command":"get_info"}` | `{"status":"ok","model":"iPhone14","ios":"17.2","battery":80}` |
| Run stage | `{"command":"run_stage","stage":"stage_1"}` | `{"status":"ok","result":"success"}` |
| List files | `{"command":"list_files"}` | `{"status":"ok","files":[...]}` |
| Read file | `{"command":"read_file","path":"/data/contacts.txt"}` | `{"status":"ok","data":"Alice,123456"}` |
| Disconnect | `{"command":"disconnect"}` | `{"status":"ok"}`, followed by socket close |

Simulator-only stage names used to exercise failures:

- `fail_stage` returns a normal `failure` result.
- `drop_connection` closes the connection without a response.

Unknown commands and missing files return `"status":"error"`. File payloads
are UTF-8 strings in this small protocol; production code would use binary
framing or base64 for arbitrary files. The simulator intentionally uses minimal
string matching instead of a third-party JSON parser.

## Running the project

Requirements are Python 3.10 or newer and a `gcc` compiler. Install and test:

```bash
python -m pip install -r requirements.txt
python -m pytest
```

Integration tests compile and start the simulator automatically on an available
local port. To run it manually on the default port:

```bash
gcc -Wall -Wextra simulator/device_simulator.c -o simulator/device_simulator
./simulator/device_simulator
```

The compiled binary is intentionally excluded from Git.

## Test coverage

The suite covers compatibility, probability calculation, ranking, chain
short-circuiting, fallback, and extraction. Integration tests use the real C
simulator for device information, stage execution, file operations, missing
files, connection drops, and the complete select-run-extract workflow.

## Deliberate limitations

This assignment implementation is single-client and single-threaded. It has no
authentication or encryption, and its in-memory files are fixed fixtures. These
choices keep it focused on orchestration, failure semantics, and the Python/C
process boundary.
