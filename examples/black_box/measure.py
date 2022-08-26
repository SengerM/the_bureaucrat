from the_bureaucrat.bureaucrats import RunBureaucrat
from pathlib import Path
import datetime
import pandas
import numpy
import time
import plotly.express as px
import warnings
from plots import *

def measure_black_box(A:float, B:float)->float:
	print('Measuring black box!')
	# ~ time.sleep(numpy.random.exponential(scale=max(min(A,.5),.1)))
	return (A**2*B**3)*(1 + .1*numpy.random.randn()) + numpy.random.randn()

def create_a_timestamp():
	time.sleep(1) # This is to ensure that no two timestamps are the same.
	return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def measure_black_box_many_times(bureaucrat:RunBureaucrat, A:float, B:float, number_of_measurements:int):
	Maria = bureaucrat # Let's give her a proper name.
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

def measure_black_box_sweeping_A_and_B(bureaucrat:RunBureaucrat, As:list, Bs:list, number_of_measurements_at_each_point:int):
	Viviana = bureaucrat
	Viviana.create_run()
	with Viviana.handle_task('measure_black_box_sweeping_A_and_B') as Vivianas_employee:
		for B in Bs:
			measure_black_box_sweeping_A(
				Vivianas_employee.create_subrun(f'black_box_with_B_{B}_sweeping_A'),
				As,
				B,
				number_of_measurements_at_each_point,
			)

if __name__ == '__main__':
	John = RunBureaucrat(
		Path.home()/Path(f'deleteme/{create_a_timestamp()}_main_run'),
	)
	measure_black_box_sweeping_A_and_B(
		bureaucrat = John, 
		As = numpy.linspace(0,5), 
		Bs = [-1,0,1],
		number_of_measurements_at_each_point = 9,
	)
	plot_black_box_vs_A_and_B(John)
	print(f'Results can be found in {John.path_to_run_directory}')
