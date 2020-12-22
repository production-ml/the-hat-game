import fasttext

file_path = 'misc.forsale.txt'
model = fasttext.train_unsupervised(file_path, model='skipgram', dim=3)
model.save_model('skipgram.model')
