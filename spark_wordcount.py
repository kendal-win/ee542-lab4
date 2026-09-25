from pyspark import SparkContext
sc = SparkContext("spark://172.31.2.84:7077", "WordCount")
text = sc.textFile("/gutenberg/*.txt")
counts = text.flatMap(lambda line: line.split()) \
.map(lambda word: (word, 1)) \
.reduceByKey(lambda a, b: a + b)
counts.saveAsTextFile("/output_spark_wordcount")
