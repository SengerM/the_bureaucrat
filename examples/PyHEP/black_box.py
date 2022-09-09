import numpy

def measure_black_box(A:float, B:float)->float:
    return (A**2*B**3)*(1 + .1*numpy.random.randn()) + numpy.random.randn()
