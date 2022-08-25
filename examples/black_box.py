from the_bureaucrat.bureaucrats import RunBureaucrat
from pathlib import Path
import datetime
import pandas
import numpy
import time
import plotly.express as px
import warnings

def measure_black_box(A:float, B:float)->float:
	print('Measuring black box!')
	if numpy.random.rand()<.1:
		raise RuntimeError(f'Error measuring the black box!')
	time.sleep(numpy.random.exponential(scale=max(min(A,.5),.1)))
	return (A**2+B**.5) + numpy.random.randn()

def create_a_timestamp():
	time.sleep(1) # This is to ensure that no two timestamps are the same.
	return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def measure_black_box_many_times(bureaucrat:RunBureaucrat, A:float, B:float, number_of_measurements:int):
	Maria = bureaucrat # Let's give him a proper name.
	Maria.create_run()
	with Maria.handle_task('measure_black_box_many_times') as Raúl: # Now this will handle the task.
		measurements = []
		for n_measurement in range(number_of_measurements):
			# Do whatever you want here...
			measured_stuff = {
				'n_measurement': n_measurement,
				'A': A,
				'B': B,
				'black_box': measure_black_box(A,B),
				'When': datetime.datetime.now(),
			}
			measurements.append(measured_stuff)
		measurements_df = pandas.DataFrame(measurements).set_index('n_measurement')
		measurements_df.to_csv(Raúl.path_to_directory_of_my_task/'results.csv')

def measure_black_box_sweeping_A(bureaucrat:RunBureaucrat, As:list, B:float, number_of_measurements_at_each_point:int):
	Quique = bureaucrat
	Quique.create_run()
	with Quique.handle_task('measure_black_box_sweeping_A') as Ernesto:
		for A in As:
			measure_black_box_many_times(
				Ernesto.create_subrun(f'black_box_with_A_{A}_and_B_{B}'),
				A,
				B,
				number_of_measurements_at_each_point,
			)

def plot_black_box_vs_A(bureaucrat:RunBureaucrat):
	Pedro = bureaucrat
	Pedro.check_these_tasks_were_run_successfully('measure_black_box_sweeping_A')
	data = []
	for run_name,path_to_run in Pedro.list_subruns_of_task('measure_black_box_sweeping_A').items():
		Johana = RunBureaucrat(path_to_run)
		Johana.check_these_tasks_were_run_successfully('measure_black_box_many_times')
		measured_data_df = pandas.read_csv(Johana.path_to_directory_of_task('measure_black_box_many_times')/'results.csv')
		measured_data_df['run_name'] = run_name
		data.append(measured_data_df)
	data_df = pandas.concat(data)
	with Pedro.handle_task('plot_black_box_vs_A') as Pedros_subordinate:
		fig = px.line(
			data_df,
			x = 'When',
			y = 'black_box',
			markers = True,
			color = 'A',
			line_group = 'run_name',
		)
		fig.write_html(
			str(Pedros_subordinate.path_to_directory_of_my_task/'black_box_vs_time.html'),
			include_plotlyjs = 'cdn',
		)
		fig = px.line(
			data_df.groupby('A').mean().reset_index(),
			x = 'A',
			y = 'black_box',
			markers = True,
		)
		fig.write_html(
			str(Pedros_subordinate.path_to_directory_of_my_task/'black_box_vs_A.html'),
			include_plotlyjs = 'cdn',
		)

if __name__ == '__main__':
	John = RunBureaucrat(
		path_to_the_run = Path.home()/Path(f'deleteme/{create_a_timestamp()}_main_run'),
	)
	measure_black_box_sweeping_A(
		bureaucrat = John,
		As = [0,5,10,15],
		B = 3,
		number_of_measurements_at_each_point = 4,
	)
	plot_black_box_vs_A(John)
