import fasttext

file_path = 'sci.space.txt'
model = fasttext.train_unsupervised(file_path, model='skipgram', dim=3, bucket=1000)
model.save_model('skipgram.model')
