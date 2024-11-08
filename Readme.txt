Using a CNN-BiLSTM-Attention model trained on Weibo sentiment data, the study achieves a high accuracy of 94% in classifying sentiment, surpassing the SnowNLP baseline accuracy of 73%. The results reveal that Luckin Coffee has evolved from a Starbucks "follower" facing financial skepticism into a popular local coffee brand in China, especially valued for its affordability and innovative products. Conversely, Starbucks' "third place" concept has not fully resonated with Chinese consumers, as customer complaints often cite noise and less-than-ideal service in Starbucks locations. The report suggests that Starbucks should adapt its strategy, particularly in northern China, and avoid negative publicity to strengthen its brand appeal.

code should be run by:
test_threads -> precess -> batch_training -> model_tag -> analysis_result
the function of different file:
test_threads: get reviews from weibo
precess: tag reviews by snowNLP, analysis data
batch_training: build and training CNN-BiLSTM-Attention model
model_tag: tag reviews by CBA, compair CBA and snowNLP
analysis_result: analysis data from time and province dimension
