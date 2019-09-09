# Игра в шляпу

Игра проходит следующим образом:
- Ведущий вытягивает из шляпы слово WORD для команды i.
- Команда i составляет для ведущего список из N_EXLAINING_WORDS слов, которые ведущий будет сообщать другим участникам по одному.
- Игра проходит N_EXPLAINING_WORDS итераций:
    - каждую итерацию j команда добавляет новую подсказку - новое слово,
    - другие игроки (все остальные команды) пытаются отгадать загаданное слово WORD, сообщая N_GUESSING_WORDS слов.
    - Как только слово окажется в этом топ-5, команда получает очки (чем раньше угадала - тем больше, например (N_EXPLAINING_WORDS - j)).
    - Загадывающая команда получает очки за каждую отгадавшую команду (например, столько же очков).

# Полезные ссылки
- an explanation of what is docker, container, dockerhub and etc https://www.freecodecamp.org/news/docker-simplified-96639a35ff36/
- a comprehensive guide about docker https://docker-curriculum.com
- how to run dockerized apps on heroku (short post) https://medium.com/travis-on-docker/how-to-run-dockerized-apps-on-heroku-and-its-pretty-great-76e07e610e22
- how to run docker on heroku (official docs) https://devcenter.heroku.com/articles/container-registry-and-runtime
- to install latest fasttext, follow the instructions here (pip install won't do it) https://github.com/facebookresearch/fastText
- what is Flask https://palletsprojects.com/p/flask/
