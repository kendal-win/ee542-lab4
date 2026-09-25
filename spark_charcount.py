from pyspark import SparkContext
sc = SparkContext("spark://172.31.2.84:7077", "CharCount")
text = sc.textFile("/gutenberg/*.txt")
chars = text.flatMap(lambda line: list(line)) \
.map(lambda ch: (ch, 1)) \
.reduceByKey(lambda a, b: a + b)
chars.saveAsTextFile("/output_spark_charcount")
