code should be run by:
test_threads -> precess -> batch_training -> model_tag -> analysis_result
the function of different file:
test_threads: get reviews from weibo
precess: tag reviews by snowNLP, analysis data
batch_training: build and training CNN-BiLSTM-Attention model
model_tag: tag reviews by CBA, compair CBA and snowNLP
analysis_result: analysis data from time and province dimension