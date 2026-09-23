# **EE542 Laboratory #4 - Hadoop**

## **Overview**

This portion of the lab sets up a two-node Hadoop cluster on AWS EC2 and runs MapReduce workloads on a PRoject Gutenberg dataset.

### **Environment**

* **OS:** Ubuntu 22.04
* **Hadoop:** 3.3.6
* **Java:** OpenJDK 11
* **Language:** Python 3
* **Execution:** Hadoop Streaming
* **Cluster:** 1 master \+ 1 worker
* **Dataset:** 150 Project Gutenberg English books (\~110MB)
* **HDFS input:** /gutenberg

The same workloads were also executed with only the master NodeManager active to compare one-node and two-node performance.

---

## **1\. Hadoop Source Code**

The Hadoop MapReduce implementations are:
* wordcount\_mapper.py
* wordcout\_reducer.py
* minmax\_reducer.py
* char\_mapper.py
* char\_reducer.py

All python programs use standard input/output so they can be executed using Hadoop Streaming.

### **WordCount**

wordcount\_mapper.py reads each input line, splits it into whitespace-separated tokens, and emits:
* word    1

wordcount\_reducer.py aggregates the values for each word and emits:
* wrod    count

The mapper preserves punctuation & capitalization because tokens are generated directly using Python's split().

### **Min/Max**

minmax\_reducer.py reads the WordCount output and determines. the least- and most-frequent keys.

Output format:
* MIN   \<word\>    \<count\>
* MAX   \<word\>    \<count\>

For this dataset & tokenizer:
* MIN   \!  1
* MAX   the 945229

---

## **2\. Character Count**

### **Mapper**
char\_mapper.py performs mapper-local aggregation. 
Instead of emitting one record for every character, it counts characters locally and emits one record per character/code point encountered by that mapper. 
* count\[ord(char)\] \+= 1

The emitted format is:
* \<Unicode code point\>    \<local count\>

For instance, the character a has Unicode code point 97.

### **Reducer**
char\_reducer.py receives sorted code-point keys and combines the counts for each key. It converts the numeric code point back into a character using:
* chr(current\_char)

The final output contains one record for each distinct character/code point

### **Character Count Optimization**
The original character mapper emitted one record per character. On the full dataset this produced:
* 109,279,541 map output records
& the job failed because of the resulting shuffle workload.
The mapped was optimized to aggregate character counts locally before emitting them. The optimized implementation produced:
* 14,572 map output records
This reduced the intermediate record count by approximately 7,5000x and allowed the character count job to complete successfully.

---

## **3\. Running Hadoop Streaming Jobs**
The Hadoop Streaming JAR is located at:
* /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar
Alternatively:
* /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-\*.jar

### **WordCount**
* hdfs \-rm \-r /output\_wordcount
*
* time hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-\*.jar \\
*   \-files /home/ubuntu/ee542-lab4/wordcount\_mapper.py,/home/ubuntu/ee542-lab4/wordcount\_reducer.py \\
*   \-input /gutenberg \\
*   \-output /output\_wordcount \\
*   \-mapper wordcount\_mapper.py \\
*   \-reducer wordcount\_reducer.py

The \-files option fistributes the Python mapper and reducer to the containers running the tasks. 

### **Min/Max**
Min/Max uses the WordCount output as its input:
* hdfs dfs \-rm \-r /output\_minmax
* 
* time hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-\*.jar \\
*   \-files /home/ubuntu/ee542-lab4/minmax\_reducer.py \\
*   \-input /output\_wordcount \\  
*   \-output /output\_minmax \\  
*   \-mapper /bin/cat \\  
*   \-reducer minmax\_reducer.py

### **Character Count**
* hdfs dfs \-rm \-r /output\_charcount  
*   
* time hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-\*.jar \\  
*   \-files /home/ubuntu/ee542-lab4/char\_mapper.py,/home/ubuntu/ee542-lab4/char\_reducer.py \\  
*   \-input /gutenberg \\  
*   \-output /output\_charcount \\  
*   \-mapper char\_mapper.py \\  
*   \-reducer char\_reducer.py 

---

## **4\. Viewing Results**
List an output directory:
* hdfs dfs \-ls /output\_wordcount

View the complete output:
* hdfs dfs \-cat /output\_wordcount/part-00000

View the first 100 lines:
* hdfs dfs \-cat /output\_wordcount/part-00000 | head \-100

Copy an HDFS output to a local file:
* hdfs dfs \-cat /output\_wordcount/part-00000 \> wordcount\_output.txt  

---

## **5\. One-Node vs. Two-Node Experiment**
To compare Hadoop performance, the same dataset and source code were run with one and two active YARN compute nodes.

### **One Node**

Only the master's YARN NodeManager was active.

### **Two Nodes**

Both the master and worker NodeManagers were active.

The HDFS dataset remained available during both experiments.

### **Results**

| Job | 1 Node | 2 Nodes |
| ----- | ----- | ----- |
| WordCount | 14m 42.655s | 5m 37.392s |
| Min/Max | 34.841s | 20.509s |
| Character Count | 13m 4.867s | 6m 44.677s |

All three workloads completed faster with two active compute nodes.

---

## **6\. Hadoop Cluster Configuration**
Both nodes use:
* Ubuntu 22.04  
* Hadoop 3.3.6  
* Java 11

### **Environment Variables**
* export HADOOP\_HOME=/usr/local/hadoop  
* export HADOOP\_CONF\_DIR=$HADOOP\_HOME/etc/hadoop  
* export HADOOP\_HDFS\_HOME=$HADOOP\_HOME  
* export HADOOP\_MAPRED\_HOME=$HADOOP\_HOME  
* export YARN\_HOME=$HADOOP\_HOME  
* export PATH=$PATH:$HADOOP\_HOME/bin:$HADOOP\_HOME/sbin

Java is configured as:
* export JAVA\_HOME=/usr/lib/jvm/java-11-openjdk-amd64

### **Hostname Resolution**
Both nodes contain entries in /etc/hosts:
* 172.31.33.16 ip-172-31-33-16  
* 172.31.2.84 ip-172-31-2-84

The master acts as the NameNode and ResourceManager.
Both machines run DataNode and NodeManager services.
HDFS replication is configured as:
* dfs.replication \= 1  

---

## **7\. Important Configuration Changes**
Several configuration changes were required to allow Hadoop services to communicate reliably within the AWS environment.

### **7.1 Fixed NodeManager RPC Port**
By default, the NodeManager RPC service may use a dynamic port.
We configured a fixed NodeManager address in yarn-site.xml on both nodes:
* \<property\>  
*     \<name\>yarn.nodemanager.address\</name\>  
*     \<value\>0.0.0.0:8041\</value\>  
* \</property\>

This makes the NodeManager RPC service consistently available on port 8041.
The change was necessary because the master initially attempted to contact the worker's NodeManager on a dynamically assigned port, which caused connection timeouts.

### **7.2 MapReduce Application Master Environment**
The MapReduce Application Master initially failed to locate the Hadoop MapReduce classes.

The following properties were added to mapred-site.xml on both nodes:
* \<property\>  
*     \<name\>yarn.app.mapreduce.am.env\</name\>  
*     \<value\>HADOOP\_MAPRED\_HOME=/usr/local/hadoop\</value\>  
* \</property\>  
*   
* \<property\>  
*     \<name\>mapreduce.map.env\</name\>  
*     \<value\>HADOOP\_MAPRED\_HOME=/usr/local/hadoop\</value\>  
* \</property\>  
*   
* \<property\>  
*     \<name\>mapreduce.reduce.env\</name\>  
*     \<value\>HADOOP\_MAPRED\_HOME=/usr/local/hadoop\</value\>  
* \</property\>

These settings ensure that MapReduce containers know where the Hadoop MapReduce installation is located.

### **7.3 Fixed Shuffle and JobHistory Ports**
The MapReduce shuffle service was configured to use port 9998:
* \<property\>  
*     \<name\>mapreduce.shuffle.port\</name\>  
*     \<value\>9998\</value\>  
* \</property\>

The JobHistory Server was configured on the master:
* \<property\>  
*     \<name\>mapreduce.jobhistory.address\</name\>  
*     \<value\>ip-172-31-33-16:9997\</value\>  
* \</property\>  
*   
* \<property\>  
*     \<name\>mapreduce.jobhistory.webapp.address\</name\>  
*     \<value\>ip-172-31-33-16:19888\</value\>  
* \</property\>

The JobHistory Server was started on the master with:
* mapred \--daemon start historyserver

### **7.4 Application Master Client Port Range**
The AWS security group was configured to allow a limited TCP port range for Hadoop communication.

The MapReduce Application Master was therefore restricted to the same available range:
* \<property\>  
*     \<name\>yarn.app.mapreduce.am.job.client.port-range\</name\>  
*     \<value\>8000-10000\</value\>  
* \</property\>

This prevents the Application Master from selecting an arbitrary dynamic RPC port outside the permitted AWS security-group range.

### **7.5 YARN Resource Limits**
The EC2 instances have limited CPU and memory resources, so explicit NodeManager resource limits were configured on both nodes:
* \<property\>  
*     \<name\>yarn.nodemanager.resource.memory-mb\</name\>  
*     \<value\>3072\</value\>  
* \</property\>  
*   
* \<property\>  
*     \<name\>yarn.nodemanager.resource.cpu-vcores\</name\>  
*     \<value\>2\</value\>  
* \</property\>

This prevents YARN from advertising significantly more resources than the EC2 instances can actually provide.

---

## **8\. Starting the Hadoop Cluster**
On the master:
* start-dfs.sh  
* start-yarn.sh  
* mapred \--daemon start historyserver

Verify Java processes:
* jps
Verify YARN nodes:
* yarn node \-list
A healthy two-node cluster should show:
* Total Nodes:2
Both nodes should have state:
* RUNNING  

---

## **9\. Stopping the Hadoop Cluster**
When the cluster is no longer needed:
* stop-yarn.sh  
* stop-dfs.sh

Stop the JobHistory Server with:
* mapred \--daemon stop historyserver  

---

## **10\. Important Notes**
* Hadoop Streaming uses \-files to make Python mapper/reducer scripts available to worker containers.  
* MapReduce performance can be strongly affected by shuffle volume.  
* Local aggregation can dramatically reduce shuffle traffic.  
* The one-node/two-node measurements were performed using the same dataset and source code.  
* The Hadoop cluster should be restored to two active YARN nodes before performing Spark experiments if Spark is intended to use the same cluster.  