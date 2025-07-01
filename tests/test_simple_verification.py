# -*- coding: utf-8 -*-
"""
Teste simples para verificar se pytest funciona
"""

def test_true():
    """Teste mais básico possível"""
    assert True


def test_math():
    """Teste simples de matemática"""
    assert 2 + 2 == 4


def test_string():
    """Teste simples de string"""
    assert "hello" == "hello"


def test_list():
    """Teste simples de lista"""
    my_list = [1, 2, 3]
    assert len(my_list) == 3


class TestBasic:
    """Classe de teste básica"""
    
    def test_method(self):
        """Método de teste"""
        assert 1 == 1
