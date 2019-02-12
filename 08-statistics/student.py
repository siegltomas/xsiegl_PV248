#!/usr/bin/env python3

import sys
import json
import csv
import numpy
from datetime import datetime, date

STR_MEAN = "mean"
STR_MEDIAN = "median"
STR_PASSED = "passed"
STR_TOTAL = "total"
STR_REGRESSION_SLOPE = "regression slope"

STR_STUDENT = "student"
STR_AVG = "average"
STR_START_DATE = "2018-09-17"


def get_avg(id, csv_data):
    data = {}
    points_list = {}
    count = {}

    for row in csv_data:
        for key, val in row.items():
            if key != STR_STUDENT:
                if key not in points_list:
                    points_list[key] = float(val)
                    count[key] = 1
                else:
                    points_list[key] = points_list[key] + float(val)
                    count[key] = count[key] + 1

    data[STR_STUDENT] = id

    for key, val in points_list.items():
        data[key] = val / count[key]

    return data


def print_per_date(date, exercise):
    points = []
    dates = []
    for val in exercise.values():
        points.append(val)
    dates = [(key, val) for key, val in date.items()]
    return (dates, points, datetime.strptime(STR_START_DATE,'%Y-%m-%d').date().toordinal())


def fill_stats(regression, points, start_date):
    stats = {}
    stats[STR_REGRESSION_SLOPE] = regression
    stats[STR_PASSED] = numpy.where(numpy.array(points) > 0)[0].size
    stats[STR_MEDIAN] = numpy.median(numpy.array(points))
    stats[STR_MEAN] = numpy.mean(numpy.array(points))
    stats[STR_TOTAL] = numpy.sum(numpy.array(points))
    if regression != 0:
        stats["date 16"] = str(datetime.fromordinal((start_date + int(16 / regression))).date())
        stats["date 20"] = str(datetime.fromordinal((start_date + int(20 / regression))).date())

    return(stats)


def get_stats(id, csv_data):
    data = {}
    if id == "average":
        data = get_avg(id, csv_data)
    else:
        for row in csv_data:
            if row[STR_STUDENT] == id:
                data = row
    date = {}
    exercise = {}
    for key, val in data.items():
        if key != STR_STUDENT:
            (d, ex) = tuple(key.split('/'))
            if d in date:
                date[d] = date[d] + float(val)
            else:
                date[d] = float(val)
            if ex in exercise:
                exercise[ex] = exercise[ex] + float(val)
            else:
                exercise[ex] = float(val)

    (dates, points, start_date) = print_per_date(date, exercise)

    d_list = []
    p_list = []
    for key, val in sorted(dates, key = lambda key: key[0]):
        p_list.append(val)
        d_list.append(datetime.strptime(key, '%Y-%m-%d').date().toordinal() - start_date)

    for i in range(1, len(p_list)):
        p_list[i] += p_list[i - 1]
    d_list = numpy.array(d_list)
    regression = numpy.linalg.lstsq([[d1] for d1 in d_list], p_list, rcond=None)[0].item()
    return fill_stats(regression, points, start_date)


def main():
    if len(sys.argv) < 3:
        print("argv error: not enough program arguments")
        print("invocation: ./student.py file id/average")
        sys.exit()

    file_name = sys.argv[1]
    id = sys.argv[2]

    file = open(file_name, 'r')
    csv_data = csv.DictReader(file, delimiter=',')

    stats = get_stats(id, csv_data)
    print(json.dumps(stats, ensure_ascii=False, indent=4))
    file.close()


if __name__ == '__main__':  
    main() 
