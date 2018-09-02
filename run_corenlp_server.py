import os


print 'Starting corenlp server'

run_corenlp_server = 'java -mx4g -cp ' \
                     '"stanford-corenlp-full-2018-02-27/*" ' \
                     'edu.stanford.nlp.pipeline.' \
                     'StanfordCoreNLPServer' \
                     ' -annotators "tokenize,ssplit,pos,lemma,parse,' \
                     'sentiment" -port 9000 -timeout 30000' \
                     ' --add-modules java.se.ee'  # isort:skip

os.system(run_corenlp_server)
