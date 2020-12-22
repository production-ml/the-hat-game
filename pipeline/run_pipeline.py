import fasttext

file_path = 'misc.forsale.txt'
model = fasttext.train_unsupervised(file_path, model='skipgram', dim=5)
model.save_model('skipgram.model')
