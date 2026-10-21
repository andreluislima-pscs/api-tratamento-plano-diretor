from app.processador_plano_diretor import ajustar, decimal_br, analisar, ajustar_linha
from pathlib import Path
import pytest

def test_preserva_identificador():
    assert ajustar('Inscrição Imobiliária',' 0010101000000000001 ')=='0010101000000000001'

def test_normaliza_cep():
    assert ajustar('CEP',' 68633-000 ')=='68633000'
    assert ajustar('CEP','ABC')=='ABC'

def test_area_brasileira():
    assert decimal_br('193,86')
    assert not decimal_br('-10,00')
    assert not decimal_br('qualquer')

def test_numero_sn():
    assert ajustar('Número',' SN ')=='SN'

# Teste opcional de integração contra a planilha original (não incluída no ZIP).
def test_integracao_dom_eliseu():
    arquivo = Path(__file__).resolve().parent /'PD_Dom_Eliseu_PA.xlsx'
    
    assert arquivo.exists(), f'Planilha não encontrada: {arquivo}'
    
    dados, arquivo_corrigido = analisar(arquivo.read_bytes())
    
    assert dados['abas']['Imóvel']==17664
    assert dados['abas']['Atividades Permitidas']==1331
    assert dados['totalErros']>=0

    assert arquivo_corrigido is None
    
@pytest.mark.parametrize(
    "tipo, logradouro, esperando_tipo, esperando_logradouro",
    [
        (
            "ANTONIO JESUS DE OLIVEIRA",
            "Rua",
            "Rua",
            "ANTONIO JESUS DE OLIVEIRA"
        ),
        (
            "Avenida",
            "Getúlio Vargas",
            "Avenida",
            "Getúlio Vargas"
        ),
        (
            "Presidente Vargas",
            "Travessa",
            "Travessa",
            "Presidente Vargas"
        ),
    ]
)
def test_ajustar_tipo_logradouro(tipo, logradouro, esperando_tipo, esperando_logradouro):
    linha = {
        "Tipo de logradouro": tipo,
        "Logradouro":logradouro
    }
    
    resultado = ajustar_linha(linha)
    
    assert resultado["Tipo de logradouro"] == esperando_tipo
    assert resultado["Logradouro"] == esperando_logradouro
     