#!/usr/bin/env python
# coding=utf-8

import requests
import commands
import math
from tqdm import tqdm
from batch_link import * 
import time 
import subprocess

if __name__ == "__main__":
    baidu_name = []
    hudong_name = []
    jm = JenaCmd()
    nts = ["/home1/peng/project/d2rq-0.8.1/full_nt/baidu_baike.nt", "/home1/peng/project/d2rq-0.8.1/full_nt/hudong_baike.nt"]
#    nts = ["/home1/peng/project/d2rq-0.8.1/1_nt/baidu_1.nt", "/home1/peng/project/d2rq-0.8.1/1_nt/hudong_1.nt"]
    subprocess.Popen(['sh', '/home1/peng/project/apache-jena-fuseki-3.7.0/fuseki-server'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    time.sleep(5)
#    status, _ = commands.getstatusoutput('sh /home1/peng/project/apache-jena-fuseki-3.7.0/fuseki-server')
    for idx, nt in enumerate(nts):
        print "nt", nt
        out_file_list = seg_nt(nt, max_len=5000000.0)
#        out_file_list = seg_nt(nt, max_len=20.0)
        for file in out_file_list:
            dbName = file.split("/")[-1].strip(".nt")
            if idx == 0:
                baidu_name.append(dbName)
            else:
                hudong_name.append(dbName)
            jm.delete_tdb(dbName=dbName)
            jm.add_tdb(dbName=dbName)
            JenaCmd.load_nt("./tdb_" + dbName, file)
            status, out = commands.getstatusoutput('cp {}/* {}'.format("./tdb_" + dbName, "/home1/peng/project/apache-jena-fuseki-3.7.0/run/databases/" + dbName))
            print out
    # restart fuseki server
    _, out = commands.getstatusoutput("netstat -tunlp|grep 3030")
    uid = out.split()[-1].strip("/java')")
    _, _ = commands.getstatusoutput("kill {}".format(uid))
    subprocess.Popen(['sh', '/home1/peng/project/apache-jena-fuseki-3.7.0/fuseki-server'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    time.sleep(10)
#    status, _ = commands.getstatusoutput('sh /home1/peng/project/apache-jena-fuseki-3.7.0/fuseki-server')

    sm = SilkCmd()
    # delete old project and build new project
    sm.control_project(project_name="baike", action="DELETE")
    sm.control_project(project_name="baike")
    # add prefixes to project
    prefixes = {"baidu": "http://www.kgbaidu.com#",
                "hudong": "http://www.kghudong.com#"}
    sm.add_prefix(prefixes)
    # add Sparql endpoint datasets
    for dname in hudong_name + baidu_name:
        print sm.build_endPoint("baike", dname, "http://10.3.10.194:3030/{}/query".format(dname), "500000")

    # build linking task
    linking_rule = '<LinkageRule linkType="owl:sameAs"><Compare metric="levenshteinDistance" id="levenshteinDistance1" required="false" threshold="0.0" weight="1"><TransformInput function="lowerCase" id="lowerCase1"><Input path="baidu:lemmas_disambi" id="sourcePath1"/></TransformInput><TransformInput function="lowerCase" id="lowerCase2"><Input path="hudong:lemmas_disambi" id="targetPath1"/></TransformInput><Param name="minChar" value="0"/><Param name="maxChar" value="z"/></Compare><Filter/></LinkageRule>'
    for hname in hudong_name:
        for bname in baidu_name:
            # odata_file means output rdf file
            # o_rdf is the name of output dataset name corresponding to odata_file
            odata_file = "o_" + hname + bname + ".nt"
            o_rdf = "d_" + hname + bname
            task_name = "t_" + hname + bname
            sm.build_output("baike", odata_file)
            sm.build_rdf("baike", o_rdf, odata_file)
            sm.build_task(project_name="baike", task_name=task_name, source_data=bname, target_data=hname, output_data=o_rdf)

    for hname in hudong_name:
        for bname in baidu_name:
            odata_file = "o_" + hname + bname + ".nt"
            o_rdf = "d_" + hname + bname
            task_name = "t_" + hname + bname
            print sm.add_rule(linking_rule, project_name="baike", task_name=task_name)
            print "task_name: ", type(task_name), task_name
            sm = SilkCmd()
            print sm.control_linking(project_name="baike", task_name=task_name)
