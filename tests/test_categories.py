import pytest

from olx import categories
from olx.errors import ConfigError


def test_tree_is_loaded():
    assert len(categories._tree()) > 2000


def test_missing_reference_file_raises_config_error_not_file_not_found_error(monkeypatch):
    # /list и /export зовут label() на каждый вызов -- при отсутствующем справочнике
    # (например, после git clone без data/reference/) владелец должен увидеть понятную
    # причину из нашей таксономии, а не голый FileNotFoundError из pathlib.
    categories._tree.cache_clear()
    monkeypatch.setattr(categories, "TREE_PATH", categories.TREE_PATH.with_name("missing.json"))
    try:
        with pytest.raises(ConfigError, match="Справочник категорий не найден"):
            categories._tree()
    finally:
        categories._tree.cache_clear()


def test_known_leaves_resolve_to_real_names():
    assert categories.name(2982) == "Продажа квартир"
    assert categories.name(2979) == "Аренда квартир долгосрочно"
    assert categories.name(85) == "Мобильные телефоны / смартфоны"


def test_path_goes_from_root_to_leaf():
    assert categories.path(2979) == [
        "Недвижимость",
        "Аренда квартир долгосрочно",
    ]


def test_label_keeps_the_distinguishing_tail():
    # Продажа и аренда различаются только последним звеном -- если label его срежет,
    # кнопки в боте станут неотличимы друг от друга.
    assert categories.label(2982) != categories.label(2979)
    assert "Продажа квартир" in categories.label(2982)
    assert "Аренда квартир долгосрочно" in categories.label(2979)


def test_unknown_id_degrades_gracefully():
    assert categories.name(99_999_999) is None
    assert categories.path(99_999_999) == []
    assert "99999999" in categories.label(99_999_999)


def test_roots_and_children():
    roots = categories.children(None)
    assert any(r["name"] == "Недвижимость" for r in roots)

    kids = {c["name"] for c in categories.children(1)}
    assert {"Продажа квартир", "Аренда квартир долгосрочно"} <= kids


@pytest.mark.parametrize("category_id", [1, 2982, 2979, 85, 3276])
def test_every_path_is_bounded(category_id):
    assert 0 < len(categories.path(category_id)) <= 6
