from app.services.processamento import limpar_campo

def test_espacos():
    assert limpar_campo('T75208_LOGRADOURO', 'Rua A ') == 'Rua A'

def test_cep():
    assert limpar_campo('T75208_CEP', '22.770-001') == '22770001'

def test_nao_remove_letras_cep():
    assert limpar_campo('T75208_CEP', 'abc') == 'abc'
    
def test_numero_nao_inventa():
    assert limpar_campo('T75208_NUMERO_LOGRADOURO', '100.0') == '100'
    assert limpar_campo('T75208_NUMERO_LOGRADOURO', 'S/N') == 'S/N'