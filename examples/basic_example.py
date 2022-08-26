from pathlib import Path
from the_bureaucrat.bureaucrats import RunBureaucrat

Michael = RunBureaucrat(Path.home()/Path(f'deleteme/todays_run'))

Michael.create_run()

try:
	with Michael.handle_task('measure_thing') as task_handler:
		print(f'Results will be saved in {task_handler.path_to_directory_of_my_task}')
		with open(task_handler.path_to_directory_of_my_task/'thing.txt', 'w') as ofile:
			print(f'The measured thing is equal to 1', file=ofile)
		# Uncomment the line below to see how it changes.
		# ~ raise RuntimeError('Some problem while doing the task `measure_thing`.')
except:
	pass

if Michael.was_task_run_successfully('measure_thing'):
	print('`measure_thing` was successfull :)')
else:
	print('`measure_thing` was not successfull :(')
