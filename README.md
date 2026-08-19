# Multi-Stage Attack Orchestrator

This is my implementation of a small attack orchestration framework. The Python
side chooses and runs an attack, while a C program simulates the device and
exposes a simple TCP interface.

## How I approached it

An attack is an ordered list of stages. Each stage has an estimated chance of
success, so I rank compatible attacks by multiplying their stage probabilities.
For example, an attack with probabilities `0.9` and `0.8` gets a score of
`0.72`. This assumes the stages are independent. It is intentionally a simple
policy; in a real system I would probably include execution time, risk and the
cost of a failed attempt as well.

Before ranking, attacks are filtered by model, iOS range and minimum battery.
The connected flow reads those values from the device rather than relying on
caller-provided state.

Stages run in order and fail fast. A normal stage failure stops the current
chain, after which the orchestrator tries the next compatible attack. A dropped
connection is treated differently: it raises `ConnectionError` and stops the
run because the device may now be in an unknown state.

I kept device I/O behind the `DeviceClient` interface. The attack and extraction
code therefore do not depend on sockets, and the TCP client can later be
replaced by a real device implementation.

## Unlocking and extraction

The simulator starts each connection in a locked state. Before running a chain,
the client sends its stage count. The simulator tracks successful stages and
only enables file access when the whole chain has completed. A failed stage
clears the progress.

`Extractor.extract_file(path)` reads one file. `Extractor.extract_all()` asks
the device for its file list and reads every returned path. The orchestrator's
`run_and_extract()` method ties the full flow together: read device state,
choose an attack, run it, and extract the files if it succeeds.

## TCP protocol

The protocol is newline-delimited JSON: one JSON object per line in each
direction. TCP is a byte stream, so the simulator buffers input until it sees a
newline rather than assuming that one `recv()` call contains one request.

The supported commands are:

- `get_info` returns the model, iOS version and battery level.
- `begin_attack` starts a chain and includes `stage_count`.
- `run_stage` runs the named stage and returns `success` or `failure`.
- `list_files` returns the available paths after the device is unlocked.
- `read_file` returns the contents of one path.
- `disconnect` closes the session cleanly.

For example, a request to run a stage looks like this:

```json
{"command": "run_stage", "stage": "stage_1"}
```

and a successful response is:

```json
{"status": "ok", "result": "success"}
```

The simulator also recognizes two stage names used by the integration tests:
`fail_stage` returns a normal failure, while `drop_connection` closes the socket
without replying. File operations before unlock return `Access denied`.

The C code deliberately avoids an external JSON dependency and only parses the
small, known command format used here. File contents are UTF-8 strings rather
than arbitrary binary data. Both are reasonable shortcuts for this simulator,
but not choices I would carry into a production protocol.

## Running it

Python 3.10 or newer and `gcc` are required.

```bash
python -m pip install -r requirements.txt
python -m pytest
```

The integration tests compile the C simulator and start it on an available
local port. To run the simulator manually on port 9000:

```bash
gcc -Wall -Wextra simulator/device_simulator.c -o simulator/device_simulator
./simulator/device_simulator
```

The compiled binary is ignored by Git.

## Tests and scope

The tests cover compatibility checks, probability-based ranking, fail-fast
chains, fallback to another attack, locked file access, extraction, missing
files and connection drops. The integration suite uses the compiled C process,
not a mock.

The simulator is intentionally single-threaded and holds a small fixed set of
files in memory. Authentication, encryption, persistence and concurrent clients
are outside the scope of this assignment.
