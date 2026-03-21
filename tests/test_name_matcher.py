from app.resolution.name_matcher import normalise_name, is_name_match


class TestNormaliseName:
    def test_basic_lowercase(self):
        assert normalise_name('Irina Dunaeva') == {'irina', 'dunaeva'}

    def test_cyrillic_transliteration(self):
        tokens = normalise_name('Ирина Дунаева')
        assert 'irina' in tokens
        assert 'dunaeva' in tokens

    def test_removes_diacritics(self):
        tokens = normalise_name('José García')
        assert 'jose' in tokens
        assert 'garcia' in tokens

    def test_removes_punctuation(self):
        tokens = normalise_name('Dunaeva, Irina')
        assert tokens == {'dunaeva', 'irina'}

    def test_removes_titles(self):
        assert normalise_name('Mr. Viktor Vekselberg') == {'viktor', 'vekselberg'}
        assert normalise_name('Mrs. Oxana Dunaeva') == {'oxana', 'dunaeva'}
        assert normalise_name('Dr. Jean Dupont') == {'jean', 'dupont'}

    def test_hyphenated_names(self):
        tokens = normalise_name('Jean-Pierre Dupont')
        assert tokens == {'jean', 'pierre', 'dupont'}

    def test_strips_single_char_tokens(self):
        tokens = normalise_name('J. P. Dupont')
        assert tokens == {'dupont'}

    def test_empty_string(self):
        assert normalise_name('') == set()

    def test_bin_prefix_removed(self):
        tokens = normalise_name('Mohammed bin Salman')
        assert tokens == {'mohammed', 'salman'}


class TestIsNameMatch:
    def test_exact_match(self):
        assert is_name_match('Irina Dunaeva', 'Irina Dunaeva')

    def test_reversed_order(self):
        assert is_name_match('Irina Dunaeva', 'Dunaeva Irina')

    def test_with_comma(self):
        assert is_name_match('Irina Dunaeva', 'Dunaeva, Irina')

    def test_with_middle_name(self):
        assert is_name_match('Irina Dunaeva', 'Irina Vladimirovna Dunaeva')

    def test_with_title(self):
        assert is_name_match('Viktor Vekselberg', 'Mr. Viktor Vekselberg')

    def test_hyphenated_match(self):
        assert is_name_match('Jean-Pierre Dupont', 'Dupont Jean Pierre')

    def test_cyrillic_latin_match(self):
        assert is_name_match('Irina Dunaeva', 'Ирина Дунаева')

    def test_vladimir_putin_cyrillic(self):
        assert is_name_match('Vladimir Putin', 'Владимир Путин')

    def test_wrong_first_name(self):
        assert not is_name_match('Irina Dunaeva', 'Oxana Dunaeva')

    def test_wrong_last_name(self):
        assert not is_name_match('Irina Dunaeva', 'Irina Liner')

    def test_first_name_only_no_match(self):
        assert not is_name_match('Irina Dunaeva', 'Irina Sericova')

    def test_completely_different(self):
        assert not is_name_match('Irina Dunaeva', 'John Smith')

    def test_empty_query(self):
        assert not is_name_match('', 'Irina Dunaeva')

    def test_empty_result(self):
        assert not is_name_match('Irina Dunaeva', '')

    def test_single_word_query(self):
        assert is_name_match('Dunaeva', 'Irina Dunaeva')

    def test_single_word_no_match(self):
        assert not is_name_match('Dunaeva', 'Irina Liner')
