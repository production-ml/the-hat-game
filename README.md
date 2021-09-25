# Игра в шляпу

Вам предлагается поучаствовать в игре на загадывание и отгадывание слов. Один из игроков пытается объяснить вытянутое из шляпы слово с помощью набора неоднокоренных слов, которые называются по очереди. После каждого нового сказанного слова другие игроки предлагают несколько вариантов отгадок. Чем раньше игрок угадает вытянутое из шляпы слово, тем больше очков он получит. Чем больше игроков угадают вытянутое из шляпы слово и чем раньше они это сделают, тем больше очков получит объясняющий игрок.

Чтобы открыть пошаговый туториал по деплою вашего первого игрока в Шляпу, откройте [HOW_TO_START.md](HOW_TO_START.md)

# Механика игры

В рамках подготовке к игре участники разрабатывают свою модель, которая реализует логику загадывания и отгадывания. Для участия в общем соревновании участники разворачивают на удаленном сервере сервис с моделью, который должен быть доступен ведущим по сети интернет.

Игра проходит следующим образом:
- Ведущий вытягивает из шляпы слово `WORD` для команды `i` и отправляет его сервису команды с помощью REST API.
- Сервис команды `i` составляет для ведущего список из `N_EXPLAINING_WORDS` слов, которые ведущий будет сообщать другим участникам по одному.
- Отгадывание проходит `N_EXPLAINING_WORDS` итераций:
    - каждую итерацию `j` ведущий добавляет новую подсказку - новое слово и отправляет сервисам команд все сказанные на данный момент слова;
    - сервисы других игроков пытаются отгадать загаданное слово `WORD`, сообщая `N_GUESSING_WORDS` слов;
    - Как только загаданное слово оказывается в сообщенных ведущему словах, команда получает очки (чем раньше угадала - тем больше, например `N_EXPLAINING_WORDS - j`);
    - Загадывающая команда получает очки за каждую отгадавшую команду (например, столько же очков).

Для тренировки алгоритмов, участвующих в соревновании, можно использовать *только* предоставленный набор данных. Несколько наборов слов для проведения тестовых игр между несколькими игроками предоставлены в папке vocabulary.

# Правила игры

Можно использовать:
1) списки стоп-слов
2) стемминг, лемматизацию
3) pos-tagging
4) токенизацию (например, в spicy)

Нельзя использовать:
1) прочие корпусы текстов, кроме опубликованных организаторами специально для проведения шляпы
2) предобученные модели
3) синонимы, антонимы, словари похожих слов и тд

Это относится как к самостоятельному использованию (скачиваете словари и используете их сами), так и к использованию библиотек, которые под капотом делают это.

Если pos-tagging/лемматизация/токенизация используют внутри себя какие-то предобученные модели - это ок, но использовать эти же предобученные модели для других целей нельзя. Например, нельзя использовать их, чтобы находить похожие слова на этапе предобработки текстов или при отгадывании/загадывании. Ещё пример - нельзя использовать их, чтобы обогащать тексты синонимами / антонимами.

Если хочется использовать что-то конкретное, но это не попадает в перечисленные пункты, то пишите организаторам (или заводите issue), мы обсудим и при необходимости отредактируем этот список.

# Пример игры

Начнем с примера проведения игры. Для этого откроем ноутбук `GameRun_Demo.ipynb` и выполним его целиком. Для примера можно взять данные датасета 20 news groups -  их можно загрузить с помощью модуля [`sklearn.datasets`](http://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_20newsgroups.html). Они также доступны на [kaggle](https://www.kaggle.com/crawford/20-newsgroups). В качестве примера также подойдет любой достаточно длинный файл с текстом (приблизительно 1 миллиона строк должно быть достаточно).

Данный пример позволяет проводить локальные игры между несколькими игроками в рамках юпитер ноутбука (нужно инициализировать объекты соответствующих классов в ноутбуке), а также тестировать развернутые удаленно сервисы (с помощью класса `RemotePlayer`).

# Как это связано с реальной жизнью

![](https://www.jeremyjordan.me/content/images/2019/09/ml-development-cycle.png)

["Чеклист" стадий ML-проекта](https://www.jeremyjordan.me/ml-projects-guide/#planning)

В индустриальном машинном обучении высоко ценятся широта навыков (насколько ты близко к Fullstack) и умение быстро итерироваться в работе над задачей. Эти вещи взаимосвязаны, поскольку задержки часто возникают там, где закончивается зона ответственности одного человека и начинается зона ответственности другого. Fullstack-специалисты способны выполнять весь цикл работы над задачей - от постановки до внедрения в продакшн. Часто наиболее сложной частью работы является как раз выкатка в прод и дальнейшее развитие созданного решения, поэтому среди прочих Fullstack навыков для DS особенно ценны навыки Software Engineer.

Необязательно быть настоящим разработчиком - улучшение даже базовых навыков разработки способно принести пользу и упростить вам жизнь. Помимо разговора с разработчиками и DevOps на их языке, вы сможете лучше понимать конечные требования к вашим моделям, а также вам будет проще дебажить ваши решения и предотвращать ситуации, когда поведение моделей в продакшне расходится с тем, что у вас происходит на ноутбуке локально.

Также полезным навыком является быстрое прототипирование сервисов вокруг ваших моделей на начальных стадиях выполнения проекта. Это поможет и на работе, когда менеджеру нужно дать протестировать модель "ручками", так и на хакатонах, где также ценится умение не только придумать какую-то идею, но и создать для неё живой прототип.

Ну и помимо того, что это важно и нужно на работе, просто круто уметь создавать ML-решения целиком от начала до конца :)

В рамках нашего соревнования мы предлагаем вам воспользоваться Python, Flask и Docker и множеством других фреймворков и решений, чтобы реализовать игрока в шляпу, научить его отвечать на HTTP запросы и, наконец, задеплоить его на удаленном сервере, откуда он будет доступен другим людям.

А поскольку мы загадываем и отгадываем слова, мы также попрактикуем предобработку текстов, обучение и использование текстовых эмбеддингов для слов. Готовы? [Давайте начнем!](HOW_TO_START.md)
