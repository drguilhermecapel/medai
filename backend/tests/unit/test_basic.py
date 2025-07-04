"""
Testes básicos para verificar cobertura
"""
import pytest

def test_basic_math():
    """Test basic math operations"""
    assert 1 + 1 == 2
    assert 2 * 3 == 6
    assert 10 / 2 == 5

def test_string_operations():
    """Test string operations"""
    assert "hello" + " world" == "hello world"
    assert "test".upper() == "TEST"
    assert len("python") == 6

def test_list_operations():
    """Test list operations"""
    test_list = [1, 2, 3]
    assert len(test_list) == 3
    test_list.append(4)
    assert len(test_list) == 4
    assert test_list[-1] == 4

def test_dict_operations():
    """Test dictionary operations"""
    test_dict = {"key": "value"}
    assert test_dict["key"] == "value"
    test_dict["new_key"] = "new_value"
    assert len(test_dict) == 2
