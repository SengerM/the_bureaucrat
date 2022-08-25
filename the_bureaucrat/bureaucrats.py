from pathlib import Path
from shutil import rmtree
import warnings
import time
import datetime
import tempfile
import traceback

def find_ugly_characters_better_to_avoid_in_paths(path:Path):
	if not isinstance(path, (Path,str)):
		raise ValueError(f'`path` must be an instance of Path.')
	NICE_CHARACTERS_FOR_FILE_AND_DIRECTORY_NAMES = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '_', '-'} # https://stackoverflow.com/a/1976172/8849755
	return set(str(path))-NICE_CHARACTERS_FOR_FILE_AND_DIRECTORY_NAMES-{'/'}

def create_run(path_where_to_create_the_run:Path, run_name:str)->Path:
	"""Creates a new run."""
	path_to_run = path_where_to_create_the_run/run_name
	if find_ugly_characters_better_to_avoid_in_paths(path_to_run):
		warnings.warn(f'Creating run in {path_to_run} I see it contains the characters {find_ugly_characters_better_to_avoid_in_paths(path_to_run)} which are better to avoid.')
	if path_to_run.is_dir():
		raise RuntimeError(f'Cannot create run {run_name} in {path_where_to_create_the_run} because it already exists.')
	path_to_run.mkdir(parents=True)
	with open(path_to_run/'bureaucrat_run_info.txt', 'w') as ofile:
		print(f'This directory contains a run named {repr(run_name)}, created by `the_bureaucrat` on {datetime.datetime.now()}.', file=ofile)
	return path_to_run

def exists_run(path_where_to_find_the_run:Path, run_name:str)->bool:
	path_to_run = path_where_to_find_the_run/run_name
	return (path_to_run/'bureaucrat_run_info.txt').is_file()

class RunBureaucrat:
	def __init__(self, path_to_the_run:Path):
		if not isinstance(path_to_the_run, Path):
			raise TypeError(f'`path_to_the_run` must be an instance of {Path}, received object of type {type(path_to_the_run)}. ')
		self._path_to_the_run = path_to_the_run
	
	@property
	def path_to_run_directory(self)->Path:
		return self._path_to_the_run
	
	@property
	def run_name(self)->str:
		return self._path_to_the_run.parts[-1]
	
	@property
	def path_to_temporary_directory(self)->Path:
		"""Path to a temporary directory to store temporary stuff. It will
		be lost after Python ends."""
		if not hasattr(self, '_temporary_directory'):
			self._temporary_directory = tempfile.TemporaryDirectory()
		return Path(self._temporary_directory.name)
		
	def path_to_directory_of_task(self, task_name:str)->Path:
		return self.path_to_run_directory/task_name
	
	def list_subruns_of_task(self, task_name:str)->Path:
		return {p.parts[-1]: p for p in (self.path_to_directory_of_task(task_name)/'subruns').iterdir()}
	
	def was_task_run_successfully(self, task_name:str)->bool:
		was_it = False
		try:
			with open(self.path_to_directory_of_task(task_name)/'bureaucrat_task_report.txt', 'r') as ifile:
				if 'exit_status: task completed successfully with no errors :)' in ifile.readline():
					was_it = True
		except Exception:
			pass
		return was_it
	
	def check_these_tasks_were_run_successfully(self, tasks_names:list, raise_error:bool=True)->bool:
		if isinstance(tasks_names, str):
			tasks_names = [tasks_names]
		if not isinstance(tasks_names, list) or not all([isinstance(task_name, str) for task_name in tasks_names]):
			raise ValueError(f'`tasks_names` must be a list of strings.')
		were_run = all([self.was_task_run_successfully(task_name) for task_name in tasks_names])
		if raise_error == True and were_run == False:
			raise RuntimeError(f'Not all tasks {tasks_names} were successfully run beforehand. ')
		return were_run
	
	def create_run(self):
		if not exists_run(self.path_to_run_directory.parent, self.run_name):
			create_run(
				path_where_to_create_the_run = self.path_to_run_directory.parent,
				run_name = self.run_name,
			)
	
	def handle_task(self, task_name):
		if len(find_ugly_characters_better_to_avoid_in_paths(task_name)) != 0:
			warnings.warn(f'Your `task_name` is {repr(task_name)} and contains the character/s {find_ugly_characters_better_to_avoid_in_paths(task_name)} which is better to avoid, as this is going to be a path in the file system.')
		return _TaskBureaucrat(
			path_to_the_run = self.path_to_run_directory,
			task_name = task_name,
		)
		
class _TaskBureaucrat(RunBureaucrat):
	def __init__(self, path_to_the_run:Path, task_name:str, drop_old_data:bool=True):
		if not exists_run(path_to_the_run.parent, path_to_the_run.parts[-1]):
			raise ValueError(f'`path_to_the_run` is {path_to_the_run} which does not look like the directory of a run...')
		super().__init__(path_to_the_run=path_to_the_run)
		self._task_name = task_name
		self._drop_old_data = drop_old_data
	
	@property
	def task_name(self):
		return self._task_name
	
	@property
	def path_to_directory_of_my_task(self):
		return self.path_to_directory_of_task(self.task_name)
	
	def __enter__(self):
		if hasattr(self, '_already_did_my_job'):
			raise RuntimeError(f'A {TaskBureaucrat} can only be used once, and this one has already been used! If you want to do a new task just hire a new bureaucrat, it is free.')
		
		if self._drop_old_data == True and self.path_to_directory_of_task(self.task_name).is_dir():
			self.clean_directory_of_my_task()
		self.path_to_directory_of_task(self.task_name).mkdir(exist_ok=True)
		
		return self
		
	def __exit__(self, exc_type, exc_value, exc_traceback):
		self._already_did_my_job = True
		
		with open(self.path_to_directory_of_my_task/Path('bureaucrat_task_report.txt'), 'w') as ofile:
			if all([exc is None for exc in [exc_type, exc_value, exc_traceback]]): # This means there was no error, see https://docs.python.org/3/reference/datamodel.html#object.__exit__
				print('exit_status: task completed successfully with no errors :)', file=ofile)
				print(f'The sole purpose of this file is to indicate that this task was completed with no errors on {datetime.datetime.now()}.', file=ofile)
			else: # If there was any kind of error...
				print('exit_status: task could not be completed becasue there were errors :(', file=ofile)
				print(f'If you are reading this it means that this script ended with errors on {datetime.datetime.now()}', file=ofile)
				print('---', file=ofile)
				traceback.print_tb(exc_traceback, file=ofile)
				print(f'{exc_type.__name__}: {exc_value}', file=ofile)
	
	def create_subrun(self, subrun_name:str)->RunBureaucrat:
		some_bureaucrat = RunBureaucrat(path_to_the_run=self.path_to_directory_of_my_task/f'subruns/{subrun_name}')
		some_bureaucrat.create_run()
		return some_bureaucrat
	
	def clean_directory_of_my_task(self):
		"""Deletes all content in the default output directory."""
		for p in self.path_to_directory_of_my_task.iterdir():
			if p.is_file():
				p.unlink()
			elif p.is_dir():
				rmtree(p)
