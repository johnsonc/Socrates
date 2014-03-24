#!/usr/bin/python

SPECS = {
	'description' : 'Provides functions for statistical analysis',
	'functions' : {
		'basic' : {
			'param': {
				'field': {
					'type' : 'field_reference numeric',
					'comment': 'Field to analyze',
				}
			},
			'aggregate_result': {
				'total': 'numeric',
				'max' : 'numeric',
				'min' : 'numeric',
				'average' : 'numeric',
				'variance' : 'numeric',
				'standard_deviation' : 'numeric'
			},
			'entry_result': {}
		}
	}
}

def basic(working_set, param=False):
	fieldVals = param['field'] #remember, this has been converted to an array of the referenced field values
	average = 0
	total = 0
	variance = 0
	maxVal = fieldVals[0]
	minVal = fieldVals[0]

	for r in fieldVals:
		total += r
		if r > maxVal:
			maxVal = r
		elif r < minVal:
			minVal = r
	
	average = total/len(fieldVals)

	for r in fieldVals:
		variance += (r - average) ** 2
	variance /= len(fieldVals) - 1

	standard_deviation = variance ** (.5)

	return {
		#'meta' : res_meta,
		'aggregate_analysis': {
				'total': total,
				'max' : maxVal,
				'min' : minVal,
				'average' : average,
				'variance' : variance,
				'standard_deviation' : standard_deviation
		},
		'entry_analysis': {}
	}

def covariance(working_set, param):
	pass