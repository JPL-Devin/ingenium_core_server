# Stress Tests

This is a script that can run many executions to stress Core/Archive/Execution.

To run the script.

```
$ cd core_server/tests
$ virtualenv -p python3 ve3 
$ source ve3/bin/activate
(ve3) $ pip install -r requirements.txt
(ve3) $ cd stress_tests
(ve3) $ python run_procedures.py

```

If you are connecting to an instance that uses a non-public SSL cert.

```
(ve3) $ export CURL_CA_BUNDLE=""
```

If you do not provide any command line argument, the script will print it usage.

```
(ve3) $ python run_procedures.py
USAGE: python run_procedures.py server create_venues num_venues
USAGE: python run_procedures.py server create_procedure num_sections num_steps_per_section
USAGE: python run_procedures.py server run_procedure venue_id procedure_id version timeout
USAGE: python run_procedures.py server run_procedures procedure_id version num_runs timeout
USAGE: python run_procedures.py server run_procedures_multi_procs procedure_id version num_runs timeout num_procs
```

The first argument is a command option.

|command|inputs|description|
|-------|-------|----------|
|create_venues|<ul><li>num_venues</li></ul>|Create venues|
|create_procedure|<ul><li>num_sections</li><li>num_steps_per_section</li></ul>|Create a procedure with a number of sections and steps populated in each section. Wait steps will be created with a random description field.|
|run_procedure|<ul><li>venue_id</li><li>procedure_id</li><li>version</li><li>timeout</li></ul>|Execute the specified procedure using the specified venue|
|run_procedures|<ul><li>procedure_id</li><li>version</li><li>num_runs: number of repeats on a process</li><li>timeout</li></ul>|Execute a procedure for a specified number of times. The execution will be executed sequentially and spread over available venues.|
|run_procedures_multi_procs|<ul><li>procedure_id</li><li>version</li><li>num_runs: number of repeats on a process</li><li>timeout</li><li>num_procs: number of simultaneous executions</li></ul>|Execute a procedure simultaneously over available venues.|

