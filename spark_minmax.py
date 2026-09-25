from pyspark import SparkContext
sc = SparkContext("spark://172.31.2.84:7077", "MinMax")
text = sc.textFile("/gutenberg/*.txt")
counts = text.flatMap(lambda line: line.split()) \
.map(lambda word: (word, 1)) \
.reduceByKey(lambda a, b: a + b)
min_word = counts.min(key=lambda x: x[1])
max_word = counts.max(key=lambda x: x[1])
print("MIN:", min_word)
print("MAX:", max_word)
