"""
Teste simples para verificar configuração do pytest
"""
import pytest

def test_pytest_is_working():
    """Teste básico para verificar se o pytest está funcionando"""
    assert True
    
def test_basic_math():
    """Teste de matemática básica"""
    assert 2 + 2 == 4
    
class TestBasicFunctionality:
    """Classe de teste básica"""
    
    def test_string_operations(self):
        """Teste de operações com strings"""
        assert "hello".upper() == "HELLO"
    
    def test_list_operations(self):
        """Teste de operações com listas"""
        my_list = [1, 2, 3]
        my_list.append(4)
        assert len(my_list) == 4
        assert my_list[-1] == 4

@pytest.mark.asyncio
async def test_async_function():
    """Teste de função assíncrona"""
    import asyncio
    await asyncio.sleep(0.01)
    assert True

# Teste parametrizado
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16)])
def test_square(input, expected):
    """Teste parametrizado de quadrado"""
    assert input ** 2 == expected
