__author__ = 'kartik'

import sys,os,time

# Usage:
# python feature_extraction_launcher.py <dataset_location> <train_set_size> <test_set_size>
# python glossextractionengine/launcher_interface.py final_dataset/ 5000 2000

class FeatureExtractionLauncher:

    def __init__(self, data_location):
        self.data_location = data_location
        self.training_set_size = None
        self.test_set_size = None

    def check_params(self):
        if self.data_location is None or self.training_set_size is None or self.test_set_size is None:
            print "You need to specify data_location, training_set_size and test_set_size before invoking any operation."
            exit()

    def invoke_sampling(self):
        self.check_params()
        # do sampling
        _cmd = "python glossextractionengine/sampler_interface.py "+self.data_location+"/positive_instances "+self.data_location+"/negative_instances "+ str(self.training_set_size)+" "+str(self.test_set_size)
        os.system(_cmd)
        time.sleep(5)

    def remove_training_dir_on_hdfs(self):
        self.check_params()
        # remove training directory on HDFS
        _cmd = "hadoop fs -rmr /user/hadoop/train"
        os.system(_cmd)
        time.sleep(5)

    def remove_output_dir_on_hdfs(self):
        self.check_params()
        # remove output directory on HDFS
        _cmd = "hadoop fs -rmr /user/hadoop/output"
        os.system(_cmd)
        time.sleep(5)

    def load_training_data_on_hdfs(self):
        self.check_params()
        # load new training data on HDFS
        _cmd = "hadoop fs -put Train/train_set_w_tags /user/hadoop/train/"
        os.system(_cmd)
        time.sleep(10)

    def start_feature_extraction_job(self):
        self.check_params()
        # start feature extraction
        _cmd = "hadoop jar /home/hadoop/contrib/streaming/hadoop-streaming-1.0.3.jar -input /user/hadoop/train -mapper glossextractionengine/lib/mapreduce/feature_extraction_flow_mapper.py -file glossextractionengine/lib/mapreduce/feature_extraction_flow_mapper.py -reducer glossextractionengine/lib/mapreduce/feature_extraction_flow_reducer.py -file glossextractionengine/lib/mapreduce/feature_extraction_flow_reducer.py -file glossextractionengine.mod -output /user/hadoop/output"
        os.system(_cmd)
        time.sleep(5)
        print "completed hadoop job..."


    def export_output_from_hdfs(self):
        self.check_params()
        if not os.path.exists("FeatureCollection"):
            os.system("mkdir FeatureCollection")

        _cmd = "hadoop fs -getmerge /user/hadoop/output ./FeatureCollection/"+str(self.training_set_size)+"_output.txt"
        os.system(_cmd)
        print "saved output: FeatureCollection/"+str(self.training_set_size)+"_output.txt"

    def launch(self):
        self.check_params()
        self.invoke_sampling()
        self.remove_training_dir_on_hdfs()
        self.remove_output_dir_on_hdfs()
        self.load_training_data_on_hdfs()
        self.start_feature_extraction_job()
        self.export_output_from_hdfs()


if __name__=="__main__":
    if len(sys.argv)<4:
        print ":( not enough params"
        print "usage: python feature_extraction_launcher.py <dataset_location> <train_set_size> <test_set_size>"
        # print sys.argv
    else:
        _data_location = sys.argv[1]
        training_set_size = sys.argv[2]
        test_set_size = sys.argv[3]

        l = FeatureExtractionLauncher(data_location=_data_location)
        l.training_set_size = training_set_size
        l.test_set_size = test_set_size
        l.launch()