from pathlib import Path
from shutil import rmtree
import warnings
import time
import datetime
import tempfile
import traceback
import shutil

warnings.warn(
	f'`the_bureaucrat` is deprecated, please consider using `datanodes` https://github.com/SengerM/datanodes',
	DeprecationWarning, 
	stacklevel = 2,
)

def find_ugly_characters_better_to_avoid_in_paths(path:Path):
	"""Returns a set of characters that are considered as not nice options
	within a Path (e.g. a white space, better to avoid), if any of such
	characters are found. This function is based on [this](https://stackoverflow.com/a/1976172/8849755)."""
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
	"""Returns `True` or `False` depending on whether the `run_name` is
	present in `path_where_to_find_the_run`."""
	path_to_run = path_where_to_find_the_run/run_name
	return (path_to_run/'bureaucrat_run_info.txt').is_file()

def delete_directory_and_or_file_and_subtree(p:Path):
	"""Delete whatever is in `p` and all its contents."""
	if p.is_file() or p.is_symlink():
		p.unlink()
	elif p.is_dir():
		rmtree(p)

class RunBureaucrat:
	def __init__(self, path_to_the_run:Path):
		"""Create a `RunBureaucrat`.
		
		Arguments
		---------
		path_to_the_run: Path
			A path to the run. The last element of the path will be the
			run name.
		"""
		self._path_to_the_run = Path(path_to_the_run)
	
	@property
	def path_to_run_directory(self)->Path:
		"""Return a `Path` object pointing to the run's directory."""
		return self._path_to_the_run
	
	@property
	def run_name(self)->str:
		"""Returns a string with the name of the run."""
		return self._path_to_the_run.parts[-1]
	
	@property
	def path_to_temporary_directory(self)->Path:
		"""Returns a `Path` pointing to a temporary directory to store stuff. 
		It will	be lost after Python ends."""
		if not hasattr(self, '_temporary_directory'):
			self._temporary_directory = tempfile.TemporaryDirectory()
		return Path(self._temporary_directory.name)
	
	@property
	def parent(self):
		"""Returns a `RunBureaucrat` pointing to the parent of this instance,
		if it does not exist, returns `None`."""
		p = self.path_to_run_directory.parent.parent.parent
		if exists_run(p.parent, p.name) == False:
			return None
		return RunBureaucrat(p)
	
	@property
	def pseudopath(self)->Path:
		"""Returns the 'pseudopath' to this bureaucrat, this means the
		path counting only the `RunBureaucrat` instances, not the directories.
		If the run does not exist in the file system, `None` is returned."""
		if self.exists() == False:
			self._pseudopath = None
		else:
			pseudopath = [self]
			while pseudopath[0].parent is not None:
				pseudopath.insert(0, pseudopath[0].parent)
			self._pseudopath = '/'.join([b.run_name for b in pseudopath])
			self._pseudopath = Path(self._pseudopath)
		return self._pseudopath
	
	def exists(self):
		"""Returns `True` or `False` depending on whether the run already
		exists in the file system or not."""
		return exists_run(path_where_to_find_the_run = self.path_to_run_directory.parent, run_name = self.run_name)
	
	def _path_to_directory_of_subruns_of_task(self, task_name:str)->Path:
		"""Returns a `Path` pointing to where the subruns should be found."""
		return self.path_to_directory_of_task(task_name=task_name)/'subruns'
		
	def path_to_directory_of_task(self, task_name:str)->Path:
		"""Returns a `Path` pointing to the directory of a task named 
		`task_name` within the run being handled by this `RunBureaucrat`.
		Note that such directory needs not to exist. 
		
		Arguments
		---------
		task_name: str
			The name of the task for which you want the path to its directory.
		"""
		return self.path_to_run_directory/task_name
	
	def list_subruns_of_task(self, task_name:str)->list:
		"""Returns a list of `RunBureaucrat`s pointing to the subruns.
		If the task does not exist or was not completed successfully, 
		a `RuntimeError` is raised.
		
		Arguments
		---------
		task_name: str
			The name of the task.
		"""
		if self._path_to_directory_of_subruns_of_task(task_name).exists():
			return [RunBureaucrat(p) for p in (self._path_to_directory_of_subruns_of_task(task_name)).iterdir() if p.is_dir()]
		else:
			return []
	
	def was_task_run_successfully(self, task_name:str)->bool:
		"""If `task_name` was successfully run beforehand returns `True`,
		otherwise (task does not exist or it does but was not completed)
		returns `False`.
		
		Arguments
		---------
		task_name: str
			The name of the task.
		
		Returns
		-------
		was_run: bool
			`True` or `False` telling if the tasks was run successfully
			or not.
		"""
		was_run = False
		try:
			with open(self.path_to_directory_of_task(task_name)/'bureaucrat_task_report.txt', 'r') as ifile:
				if 'exit_status: task completed successfully with no errors :)' in ifile.readline():
					was_run = True
		except Exception:
			pass
		return was_run
	
	def check_these_tasks_were_run_successfully(self, tasks_names:list, raise_error:bool=True)->bool:
		"""Check that certain tasks were run successfully beforehand.
		
		Arguments
		---------
		tasks_names: list of str, or str
			A list with the names of the tasks to check for, or a string
			with the name of a single task to check for.
		raise_error: bool, default True
			If `True` then a `RuntimeError` will be raised if any of the
			tasks in `tasks_names` was not run successfully beforehand.
			If `False` then no error is raised.
		
		Returns
		-------
		all_tasls_were_run: bool
			`True` if all the tasks were run, else `False`.
		"""
		if isinstance(tasks_names, str):
			tasks_names = [tasks_names]
		if not isinstance(tasks_names, list) or not all([isinstance(task_name, str) for task_name in tasks_names]):
			raise ValueError(f'`tasks_names` must be a list of strings.')
		tasks_not_run = [task_name for task_name in tasks_names if not self.was_task_run_successfully(task_name)]
		all_tasks_were_run = len(tasks_not_run) == 0
		if raise_error == True and not all_tasks_were_run:
			raise RuntimeError(f"Task(s) {tasks_not_run} was(were)n't successfully run beforehand on run {self.pseudopath} located in {self.path_to_run_directory}.")
		return all_tasks_were_run
	
	def create_run(self, if_exists:str='raise error'):
		"""Creates a run where this `RunBureaucrat` is pointing to.
		
		Arguments
		---------
		if_exists: str, default 'raise error'
			Determines the behavior to follow if this method is called
			and the run already exists according to the following options:
			- `'raise error'`: A `RuntimeError` is raised if the run
			already exists.
			- `'override'`: If the run already exists, it will be deleted
			(together with all its contents) and a new run will be 
			created instead.
			- `'skip'`: If the run already exists, nothing is done.
		"""
		OPTIONS_FOR_IF_EXISTS_ARGUMENT = {'raise error','override','skip'}
		if if_exists not in OPTIONS_FOR_IF_EXISTS_ARGUMENT:
			raise ValueError(f'`if_exists` must be one of {OPTIONS_FOR_IF_EXISTS_ARGUMENT}, received {repr(if_exists)}. ')
		
		if exists_run(self.path_to_run_directory.parent, self.run_name):
			if if_exists == 'raise error':
				raise RuntimeError(f'Cannot create run {repr(self.run_name)} in {self.path_to_run_directory} because it already exists.')
			elif if_exists == 'override':
				delete_directory_and_or_file_and_subtree(self.path_to_run_directory)
			elif if_exists == 'skip':
				return
			else:
				raise ValueError(f'Unexpected value received for argument `if_exists`. ')
		
		create_run(
			path_where_to_create_the_run = self.path_to_run_directory.parent,
			run_name = self.run_name,
		)
	
	def handle_task(self, task_name:str, drop_old_data:bool=True, backup_this_python_file:bool=True, allowed_exceptions:set=None):
		"""This method is used to create a new "subordinate bureaucrat" 
		of type `TaskBureaucrat` that will manage a task (instead of a
		run) within the run being managed by the current `RunBureaucrat`.
		
		This method was designed for being used together with a `with` 
		statement, e.g.
		```
		with a_run_bureaucrat.handle_task('some_task') as subordinated_task_bureaucrat:
			blah blah blah
		```
		
		Arguments
		---------
		task_name: str
			The name of the task to handle by the new bureaucrat.
		drop_old_data: bool, dafault True
			If `True` then any data that may exist in the given task e.g.
			from a previous execution will be deleted. This ensures that
			in the end all the contents belong to the latest execution
			and it is not mixed with old stuff.
		backup_this_python_file: bool, default True
			If `True`, the file where `handle_task` is being called will
			be backed up in the respective task directory, i.e. a copy
			will be created there. Thus, in the future you will be able
			to know how you did things in case you forget.
		allowed_exceptions: set of exceptions, default None
			A set of exceptions that if happen they are not considered errors,
			for example you may want that if you manualy stop the execution
			that is not an error so you then `allowed_exceptions={KeyboardInterrupt}`
			would handle that.
		
		Returns
		-------
		new_bureaucrat: TaskBureaucrat
			A bureaucrat to handle the task.
		"""
		if len(find_ugly_characters_better_to_avoid_in_paths(task_name)) != 0:
			warnings.warn(f'Your `task_name` is {repr(task_name)} and contains the character/s {find_ugly_characters_better_to_avoid_in_paths(task_name)} which is better to avoid, as this is going to be a path in the file system.')
		return TaskBureaucrat(
			path_to_the_run = self.path_to_run_directory,
			task_name = task_name,
			drop_old_data = drop_old_data,
			path_to_script_to_backup = Path(traceback.extract_stack()[-2].filename),
			allowed_exceptions = allowed_exceptions,
		)
	
class TaskBureaucrat(RunBureaucrat):
	def __init__(self, path_to_the_run:Path, task_name:str, drop_old_data:bool=True, path_to_script_to_backup:Path=None, allowed_exceptions:set=None):
		"""Create a `TaskBureaucrat`.
		
		Arguments
		---------
		path_to_the_run: Path
			A `Path` object pointing to the run wherein to handle the task.
		task_name: str
			The name of this task.
		drop_old_data: bool, default True
			If `True`, the directory for this task will be cleaned when
			this bureaucrat begins operating. Otherwise, any previous data
			will be untouched.
		allowed_exceptions: set of exceptions, default None
			A set of exceptions that if happen they are not considered errors,
			for example you may want that if you manualy stop the execution
			that is not an error so you then `allowed_exceptions={KeyboardInterrupt}`
			would handle that.
		"""
		if not exists_run(path_to_the_run.parent, path_to_the_run.parts[-1]):
			raise ValueError(f'`path_to_the_run` is {path_to_the_run} which does not look like the directory of a run...')
		super().__init__(path_to_the_run=path_to_the_run)
		self._task_name = task_name
		self._drop_old_data = drop_old_data
		self._path_to_script_to_backup = path_to_script_to_backup
		self._allowed_exceptions = allowed_exceptions if allowed_exceptions is not None else {}
	
	@property
	def task_name(self)->str:
		"""Returns a string with the name of the task."""
		return self._task_name
	
	@property
	def path_to_directory_of_my_task(self)->Path:
		"""Returns a `Path` object pointing to the directory of the current
		task."""
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
			if all([exc is None for exc in [exc_type, exc_value, exc_traceback]]) or exc_type in self._allowed_exceptions: # This means there was no error, see https://docs.python.org/3/reference/datamodel.html#object.__exit__
				print('exit_status: task completed successfully with no errors :)', file=ofile)
				print(f'The sole purpose of this file is to indicate that this task was completed with no errors on {datetime.datetime.now()}.', file=ofile)
			else: # If there was any kind of error...
				print('exit_status: task could not be completed becasue there were errors :(', file=ofile)
				print(f'If you are reading this it means that this script ended with errors on {datetime.datetime.now()}', file=ofile)
				print('---', file=ofile)
				traceback.print_tb(exc_traceback, file=ofile)
				print(f'{exc_type.__name__}: {exc_value}', file=ofile)
		
		if self._path_to_script_to_backup is not None:
			try:
				shutil.copyfile(self._path_to_script_to_backup, self.path_to_directory_of_my_task/f'backup.{self._path_to_script_to_backup.parts[-1]}')
			except FileNotFoundError as e:
				warnings.warn(f'Cannot create backup of script, reason: {e}.')
	
	def create_subrun(self, subrun_name:str, if_exists:str='raise error')->RunBureaucrat:
		"""Create a subrun within the current task.
		
		Arguments
		---------
		subrun_name: str
			The name for the subrun.
		if_exists: str, default 'raise error'
			Determines the behavior to follow if this method is called
			and the run already exists. For available options see documentation
			of `RunBureaucrat.create_run`.
		
		Returns
		-------
		new_run_bureaucrat: RunBureaucrat
			A newly created `RunBureaucrat` ready to handle the new subrun.
		"""
		some_bureaucrat = RunBureaucrat(path_to_the_run=self._path_to_directory_of_subruns_of_task(self.task_name)/subrun_name)
		some_bureaucrat.create_run(if_exists=if_exists)
		return some_bureaucrat
	
	def clean_directory_of_my_task(self):
		"""Deletes all content in the default output directory."""
		for p in self.path_to_directory_of_my_task.iterdir():
			delete_directory_and_or_file_and_subtree(p)
