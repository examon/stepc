#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# Copyright (C) 2012 exo <exo[at]tty[dot]sk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# -----------------------------------------------------------------------------
# DESCRIPTION:
#
# stepc serves for counting user's steps, processing collected data into html
# web page filled with graph/statistics. stepc can automatically upload all
# processed data to the user's server via ssh/rsync.

# -----------------------------------------------------------------------------
# REQUIREMENTS:
#
#	matplotlib
#	ssh
#	rsync

# -----------------------------------------------------------------------------
# USAGE:
#
# just use:
#
#	python stepc.py -h
# or	
#	python stepc.py --help


# -----------------------------------------------------------------------------
# User specific stuff. Feel free to change this.

# destination server addr
SSH_DEST	= "tty.sk@195.210.29.11:/sub/steps/"

# working dir path
DIR_DEST	= "/home/exo/Stuff/tty/sub/steps/"

# database path
DB_PATH		= "/home/exo/Github/stepc/steps_database"

# backup database path
BACKUP_DB_PATH	= "/home/exo/Github/stepc/steps_database_backup"

# user's step length (in meters)
step_length	= 0.65

# font size used for graph
font_size	= 20

# index webpage name
index_name	= "index.html"

# graph's line settings
line_type	= "-x"

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

import matplotlib.pyplot as plt
import pylab
import os
from sys import argv

EXIT_FAILURE = 1
EXIT_SUCCESS = 0
db_date  = []		# date list
db_distance  = []	# distance list
db_steps = []		# steps list

def main():
	check_argv()

def error_bad_argv():
	print "Usage: %s [-y] [--yesterday] [-u] [--update] steps" % argv[0]
	print "Try '%s -h [--help] for more information." % argv[0]

def show_help():
	print "Usage: %s [-y] [--yesterday] steps" % argv[0]
	print "[-y] or [--yesterday]: all work will be done with yesterday's date "
	print "[-u] or [--update]: perform only graph/index.html update"
	print "steps: number of steps"

def check_argv():
	""" Check cmd line argument abuse & call next core fuctions.
	"""
	if (len(argv) != 2 and len(argv) != 3):
		error_bad_argv()
		return EXIT_FAILURE
	elif (len(argv) == 2):
		if (argv[1] == "-h" or argv[1] == "--help"):
			show_help()
			return EXIT_FAILURE
		elif (argv[1] == "-u" or argv[1] == "--update"):
			perform_update()
		elif (argv[1].isdigit()):
			stream = os.popen("date +\"%Y-%m-%d\"")
			date = stream.next()[:-1]
			steps = argv[1]
			backup_database(date, steps)
			perform_update()
		else:
			print "error: cmd line argument representing number",
			print "of steps have to be an integer!"
			return EXIT_FAILURE
	elif (len(argv) == 3 and (argv[1] == "-y" or argv[1] == "--yesterday")):
		stream = os.popen("date --date=\'1 days ago\' +\"%Y-%m-%d\"")	
		date = stream.next()[:-1]
		steps = argv[2]	
		if not (steps.isdigit()):
			print "error: cmd line argument representing number",
			print "of steps have to be an integer!"
			return EXIT_FAILURE
		backup_database(date, steps)
		perform_update()
	else:
		error_bad_argv()
		return EXIT_FAILURE

def perform_update():
	""" Update graph/index to the most recent version.
	"""
	print "Updating..."
	make_graph()
	make_index_html()
	mirror_local_server()	
	print "Done!"
	return EXIT_SUCCESS

def mirror_local_server():
	""" Mirror DIR_DEST with SSH_DEST using ssh and rsync.
	"""
	print "Connecting to server..."
	os.system("rsync -avz -e ssh %s %s" % (DIR_DEST, SSH_DEST))
	print "Disconnected from server!"	

def backup_database(date, steps):
	""" Copy file at DB_PATH to BACKUP_DB_PATH. Then update DB_PATH
	    with the most recent date and steps.
	"""
	print "Backuping database..."
	os.system(("cp %s %s" % (DB_PATH, BACKUP_DB_PATH)))
	date_steps = "%s %s" % (date, steps)
	os.system("echo \"%s\" >> %s" % (date_steps, DB_PATH))
	print "Done!"

def make_graph():
	km = 1000.0
	db_mixed = []
	fo = open(DB_PATH, "r")
	for i in fo: db_mixed.append(i)
	for i in db_mixed:
		db_date.append(i.split(' ')[0])
		db_distance.append(round(int(i.split(' ')[1][0:-1]) * step_length / km, 1))
		db_steps.append(int(i.split(' ')[1][0:-1]))
	plt.plot(db_distance, line_type)
	graph_title = "%s - %s" % (db_date[0], db_date[-1])
	plt.title(graph_title, fontsize = font_size)
	plt.ylabel("Distance/Day [km]", fontsize = font_size)
	ax = pylab.gca()
	ax.xaxis.set_visible(False)
	plt.savefig(DIR_DEST + "plot_distance.png")
	print "Image generated: %s" % (DIR_DEST + "plot_distance.png")

def total():
	km = 1000.0
	total_steps = 0;
	for i in db_steps: total_steps += int(i)
	total_distance = round(total_steps * step_length / km, 2)
	total_days = len(db_date)
	return (total_steps, total_distance, total_days)

def avg_day():
	days = len(db_date)
	avg_day_steps = total()[0] / days
	avg_day_distance = round(total()[1] / days, 2)
	return (avg_day_steps, avg_day_distance)

def steps_min_max():
	return (min(db_steps), max(db_steps))

def distance_min_max():
	return (min(db_distance), max(db_distance))

def make_index_html():
	index = open(DIR_DEST + index_name, "w")
	avg_day_steps = str(avg_day()[0])
	avg_day_distance = str(avg_day()[1])
	total_steps = str(total()[0])
	total_distance = str(total()[1])
	total_days = str(total()[2])
	min_steps_day = str(steps_min_max()[0])
	max_steps_day = str(steps_min_max()[1])
	min_distance_day = str(distance_min_max()[0])
	max_distance_day = str(distance_min_max()[1])

	index.write(
		    "<html>\n"
		    "	<img src=\"plot_distance.png\">\n"
		    "	<pre>\n"
		    "	Statistics\n"
		    "	==========\n"
		    "	total days: " + total_days + "\n"
		    "	total steps: " + total_steps + "\n"
		    "	total distance: " + total_distance + "km\n"
		    "	----------------\n"
		    "	avg. steps/day: " + avg_day_steps + "\n"
		    "	avg. distance/day: " + avg_day_distance + "km\n"
		    "	----------------\n"
		    "	min. steps/day: " + min_steps_day + "\n"
		    "	max. steps/day: " + max_steps_day + "\n"
	            "	----------------\n"
		    "	min. distance/day: " + min_distance_day + "km\n"
		    "	max. distance/day: " + max_distance_day + "km\n"
		    "	</pre>\n"
		    "</html>"
		   )

	index.close()
	print "Index generated: %s" % (DIR_DEST + index_name)

if __name__ == "__main__":
	main()
