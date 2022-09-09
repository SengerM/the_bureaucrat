# the_bureaucrat

A package to help organizing data and results in a directory structure, cross platform and transparent.

# Installation

`pip install git+https://github.com/SengerM/the_bureaucrat`

# Usage

Below there is a simple usage example:

```python
from pathlib import Path
from the_bureaucrat.bureaucrats import RunBureaucrat

Michael = RunBureaucrat(
	Path.home()/Path(f'measurements_data/todays_run'),
)

Michael.create_run()

with Michael.handle_task('measure_thing') as task_handler:
	with open(task_handler.path_to_directory_of_my_task/'thing.txt', 'w') as ofile:
		print(f'The measured thing is equal to 1', file=ofile)
```

The steps are:

1. Create a `RunBureaucrat`.
2. Tell him to create a new run.
3. Tell him to do a task (within that run).

In the end this will create a directory for the run and within that directory as many subdirectories as tasks have been done. Also, each task will have a flag that will tell if it was completed successfully or if an error occurred, that can be checked later on, e.g.:

```python
if Michael.was_task_run_successfully('measure_thing'):
	print('`measure_thing` was successfull :)')
else:
	print('`measure_thing` was not successfull :(')
```

If for some reason some error occurs while `measure_thing` is ongoing, it will not pass unnoticed when you want to use that data in the future.

Furthermore, a backup of the python file in which the task was created will be automatically stored in the respective task directory. Then you can have a hint on how you did things in case you forget in the future.

For more examples, see [here](examples).

# Additional info

This package is thought to handle runs, each run can contain any number of tasks (each with a different name). Within each task anything can be stored, usually the results of such task e.g. the data from some measurement, some plots, etc. Each task can in turn contain subruns, which can contain tasks, and so. So it is a tree-like structure that is automatically created in the background.

![blah](doc/diagram.svg)

An example that creates such tree-like structure is presented in [black_box](examples/black_box) within the [examples](examples) directory. Advantages of this approach: It can tackle a quite complex and tedious problem splitting it in very simple ones.
# the_bureaucrat
