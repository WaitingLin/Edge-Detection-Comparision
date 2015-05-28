#!/usr/bin/python

from scipy import misc
from scipy import ndimage
from array import array

import numpy as np
import math
import matplotlib.pyplot as plt
import multiprocessing
import Queue
import time
import ctypes

def convolution(inputArr, x, y):
	x_mask = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
	y_mask = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
	ret_x = 0
	ret_y = 0
	lx, ly = inputArr.shape

	for i in range(-1, 2):
		for j in range(-1, 2):
			x_index = (x + i if x + i < lx else (x + i) % lx)
			y_index = (y + j if y + j < ly else (y + j) % ly)
			ret_x += inputArr[x_index, y_index] * x_mask[i + 1, j + 1]
			ret_y += inputArr[x_index, y_index] * y_mask[i + 1, j + 1]
	
	return math.sqrt(ret_x**2 + ret_y**2)



def convolution_wrap(start):
	global inputArr, outputArr, mp_arr, part
	n = len(inputArr[0])	

	arr = np.frombuffer(mp_arr.get_obj(), dtype=ctypes.c_int)
	outputArr = arr.reshape((n,n))	

	for i in range(start, start+part):
		for j in range(n):
			outputArr[i, j] = convolution(inputArr, i, j)

def computation(inputArr, process_count):
	n = len(inputArr)	
	pool = multiprocessing.Pool(process_count)
	pool.map(convolution_wrap, range(0,n, part))
	
	arr = np.frombuffer(mp_arr.get_obj(), dtype=ctypes.c_int)
	outputArr = arr.reshape((n,n))

	return outputArr


if __name__ == '__main__':
	import argparse, sys
	from os.path import isfile
	from argparse import ArgumentParser
	# Program arguments
#	parser = ArgumentParser(description="Image Edge detection")
#	parser.add_argument("-i", "--input",
#		dest="filename", required=True, type=extant_file,
#		help="input image file", metavar="FILE")
#	parser.add_argument("-o", "--output",
#		type=argparse.FileType(mode='w'),
#		default=sys.stdout, dest="output",
#		help="file to write output to (default=stdout)")
#	args = parser.parse_args()	

	# Creating a numpy array from an image file
	inputArr = misc.imread('lena.png')

	# Do edge detection
	start_time = time.time()
	lx, ly = inputArr.shape
	outputArr = np.zeros((lx, ly))

	# Create & start new threads
	process_count = multiprocessing.cpu_count()*2
	
	# Create shared data among processes 
	mp_arr = multiprocessing.Array(ctypes.c_int, lx*ly)
	part = len(inputArr) / process_count
	if part < 1:
		part = 1

	outputArr = computation(inputArr, process_count)
	elapsed_time = time.time() - start_time
	print "elapsed_time: " + str(elapsed_time)
	# Display picture
	plt.imshow(outputArr)
	plt.show()
	#plt.imshow(inputArr, cmap=plt.cm.gray)

	plt.imshow(inputArr, cmap=plt.cm.gray, vmin=30, vmax=200)
	plt.show()

	# Store the result in another picture file
	misc.imsave('output.png', outputArr)