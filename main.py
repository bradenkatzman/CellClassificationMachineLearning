import sys
import time
import numpy as np
from RNASeqData import RNASeqData
import preprocess
import guassianNB_RNASeq
import analysis


# Resource: http://machinelearningmastery.com/get-your-hands-dirty-with-scikit-learn-now/
# Python for Java Programmers: http://python4java.necaiseweb.org/Fundamentals/TheBasics

# run with downsampling: python main.py GSE60361C13005Expression.txt expressionmRNAAnnotations.txt 1
# run without downsampling: python main.py GSE60361C13005Expression.txt expressionmRNAAnnotations.txt 0

if __name__ == '__main__':
	t0 = time.clock()
	print "start"
	
	# check for correct number of args
	if len(sys.argv) != 4:
		print "Usage: python main.py <raw_data_file> <annotations_file> <down sample? --> 0,1>"
		sys.exit(0)

	raw_data_file = sys.argv[1]
	annotations_file = sys.argv[2]
	downSampleFlag = False
	if sys.argv[3] == "1":
		downSampleFlag = True

	print "Using:"
	print " - raw data: {raw}".format(raw=raw_data_file)
	print " - annotations: {ann}".format(ann=annotations_file)
	if downSampleFlag:
		print "** Down sampling enabled **"
	else:
		print "** Down sampling disabled **"


	# initialize the data set class
	data = RNASeqData(raw_data_file, annotations_file)
	
	# read raw RNA seq data into memory
	data.setRawData(preprocess.loadRawData(data.getRawDataFileName()))

	# read cell identifier annotations into memory
	data.setCellIdentifierAnnotations(preprocess.loadCellIdentifierAnnotations(data.getAnnotationsFileName(), 
		data.getNumCellsRaw()))

	# read molecule count annotations into memory
	data.setMoleculeCountAnnotations(preprocess.loadMoleculeCountAnnotations(data.getAnnotationsFileName(),
		data.getNumCellsRaw()))

	if downSampleFlag:
		# down sample the data by cluster size --> MAKE DOWN SAMPLING A CLA OPTION
		#	 i.e. scale all cluster size to the smallest cluster (by number of cells)
		# save down sampled data and random indices for accessing corresponding annotations
		downSampleClusterData, randIndices = preprocess.downSampleByClusterSize(data.getRawData(), 
			data.getCellIdentifierAnnotations())

		# add the data and random indices reference to the data class
		data.setDSClusterData(downSampleClusterData)
		data.setRandIndicesFromDS(randIndices)

		# down sample the data by the cell with the least number of molecules
		data.setDSCluster_MoleculeData(preprocess.downSampleByMoleculeCount(data.getDSClusterData(),
			data.getMoleculeCountAnnotations(), data.getRandIndices()))

		# partition the down sampled data set into 70% training and 30% testing
		data.makeDSTrainingAndTestingData()

		# fit down sampled training data to gaussian nb
		guassianNB_RNASeq.fitTrainingData(data.getDSTrainingData(), data.getDSTargetValues())

		# predict values using gaussian nb with down sampled data
		guassianNB_predictionResults = guassianNB_RNASeq.predictTestData(data.getDSTestingData())
	
		# analyze results of guassian nb on down sampled data
		analysis.analyzeResults("Guassian Naive Bayes", guassianNB_predictionResults, data.getDSTestingDataTargetValues())
	else:
		# partition the data set into 70% training and 30% testing
		data.makeTrainingAndTestingData()

		# fit training data to gaussian nb
		guassianNB_RNASeq.fitTrainingData(data.getTrainingData(), data.getTrainingDataTargetValues())

		# predict values using gaussian nb with down sampled data
		guassianNB_predictionResults = guassianNB_RNASeq.predictTestData(data.getTestingData())
	
		# analyze results of guassian nb on down sampled data
		analysis.analyzeResults("Guassian Naive Bayes", guassianNB_predictionResults, data.getTestingDataTargetValues())
	

	print "\nprogram execution: {t} seconds".format(t=time.clock()-t0)
	print "exiting"
