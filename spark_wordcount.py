from pyspark import SparkContext
sc = SparkContext("local", "WordCount")
text = sc.textFile("/gutenberg/*.txt")
counts = text.flatMap(lambda line: line.split()) \
.map(lambda word: (word, 1)) \
.reduceByKey(lambda a, b: a + b)
counts.saveAsTextFile("/output_spark_wordcount")
