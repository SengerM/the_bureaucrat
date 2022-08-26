from the_bureaucrat.bureaucrats import RunBureaucrat
from pathlib import Path
import pandas
import plotly.express as px

def plot_measurements_vs_time(bureaucrat:RunBureaucrat):
	Pedro = bureaucrat
	Pedro.check_these_tasks_were_run_successfully('measure_black_box_many_times')
	data_df = pandas.read_csv(Pedro.path_to_directory_of_task('measure_black_box_many_times')/'results.csv')
	fig = px.line(
		data_df.sort_values('When'),
		x = 'When',
		y = 'black_box',
		markers = True,
	)
	with Pedro.handle_task('plot_measurements_vs_time') as employee:
		fig.write_html(
			str(employee.path_to_directory_of_my_task/'measurements_vs_time.html'),
			include_plotlyjs = 'cdn',
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
		data_df.to_csv(Pedros_subordinate.path_to_directory_of_my_task/'data.csv', index=False)
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

def plot_black_box_vs_A_and_B(bureaucrat:RunBureaucrat):
	Pedro = bureaucrat
	Pedro.check_these_tasks_were_run_successfully('measure_black_box_sweeping_A_and_B')
	data = []
	for run_name,path_to_run in Pedro.list_subruns_of_task('measure_black_box_sweeping_A_and_B').items():
		Johana = RunBureaucrat(path_to_run)
		plot_black_box_vs_A(Johana)
		Johana.check_these_tasks_were_run_successfully('plot_black_box_vs_A')
		measured_data_df = pandas.read_csv(Johana.path_to_directory_of_task('plot_black_box_vs_A')/'data.csv')
		data.append(measured_data_df)
	data_df = pandas.concat(data)
	fig = px.line(
		data_df.groupby('run_name').mean().reset_index().sort_values(['A','B']),
		x = 'A',
		y = 'black_box',
		color = 'B',
		markers = True,
	)
	with Pedro.handle_task('plot_black_box_vs_A_and_B') as employee:
		fig.write_html(
			str(employee.path_to_directory_of_my_task/'black_box_vs_A_for_different_Bs.html'),
			include_plotlyjs = 'cdn',
		)
		data_df.to_csv(employee.path_to_directory_of_my_task/'data.csv', index=False)
