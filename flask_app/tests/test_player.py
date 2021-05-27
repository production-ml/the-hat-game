def test_player_explain():
    from app import player

    words = player.explain(word="test", n_words=5)
    print(words)


def test_player_guess():
    from app import player

    words = player.guess(words=["taste", "cake", "sweet"], n_words=5)
    print(words)
