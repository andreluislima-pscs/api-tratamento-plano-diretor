
import base64
import io
import re
import csv
from collections import Counter

import pandas as pd

from app.validators.validador import valida_valor
from app.schemas import imovel_schemas

MAX_LINHAS = 50_000
MAX_ERROS_EXIBIDOS = 100

def limpar_campo(coluna:str, valor:str) -> str:
    valor = valor.strip()
    if coluna == "T75208_UF":
        return valor.upper()
    
    if coluna in ("T75208_CEP", "T75208_CPF_CRIOU", "T75208_CPF_ALTEROU"):
        return re.sub(r"[.\-/\s]", "", valor)
    
    if coluna == "T75208_NUMERO_LOGRADOURO" and re.fullmatch(r'\d+\.0', valor):
        return valor[:-2]
    
    return valor

def ler_tabela(conteudo:bytes, nome:str)-> pd.DataFrame:
    if nome.lower().endswith('.csv'):
        texto = conteudo.decode("utf-8-sig")
        return pd.read_csv (io.StringIO(texto),sep=";", dtype=str, keep_default_na=False,
                            on_bad_lines="error", engine="python")
    if nome.lower().endswith(".xlsx"):
        return pd.read_excel(io.BytesIO(conteudo), dtype=str, keep_default_na=False, engine='openpyxl')
    raise ValueError('Formato não suportado. Envie .csv (UTF-8, separado por ;) ou .xlsx.')
     
def processar_dados(conteudo:str, nome:str) -> dict:
    df = ler_tabela(conteudo, nome)
    if len(df) > MAX_LINHAS:
        raise ValueError(f'Limite didático: {MAX_LINHAS} linhas por arquivo.')
    faltantes = [c for c in SCHEMA if c not in df.columns]
    if faltantes:
        raise ValueError('Colunas obrigatórias ausentes: ' + ', '.join(faltantes))
    # Não permitir descartar silenciosamente colunas extras.
    extras = [c for c in df.columns if c not in SCHEMA]
    if extras:
        raise ValueError('Colunas não previstas no schema: ' + ', '.join(extras))

    dados = df.copy()
    auditoria = []
    erros = []
    contagem = Counter()
    for i, (_, linha) in enumerate(dados.iterrows(), start=2):
        for col in imovel_schemas.SCHEMA:
            antigo = '' if pd.isna(linha[col]) else str(linha[col])
            novo = limpar_campo(col, antigo)
            if novo != antigo:
                dados.at[dados.index[i - 2], col] = novo
                regra = 'NORMALIZACAO_' + col.replace('T75208_', '')
                contagem[regra] += 1
                if len(auditoria) < 100:
                    auditoria.append({'linha': i, 'coluna': col, 'antes': antigo,
                                      'depois': novo, 'regra': regra})

    # Duplicados completos são apontados, jamais removidos automaticamente.
    duplicados = dados.duplicated(keep=False)
    for idx in dados.index[duplicados]:
        erros.append({'linha': int(dados.index.get_loc(idx)) + 2, 'coluna': '(linha inteira)',
                      'valor': '', 'erro': 'Linha duplicada: análise obrigatória'})

    # IPTU repetido também exige decisão da regra de negócio.
    repetidos_iptu = dados['T75208_IPTU'].astype(str).str.strip()
    mascara = repetidos_iptu.ne('') & repetidos_iptu.duplicated(keep=False)
    for idx in dados.index[mascara]:
        erros.append({'linha': int(dados.index.get_loc(idx)) + 2, 'coluna': 'T75208_IPTU',
                      'valor': str(dados.at[idx, 'T75208_IPTU']),
                      'erro': 'IPTU repetido: verificar regra de negócio'})

    for i, (_, linha) in enumerate(dados.iterrows(), start=2):
        for col, spec in imovel_schemas.SCHEMA.items():
            valor = str(linha[col])
            for msg in valida_valor(col, spec, valor):
                erros.append({'linha': i, 'coluna': col, 'valor': valor, 'erro': msg})

    resultado = {
        'sucesso': not erros, 'modo': 'SIMULACAO_SEM_BANCO',
        'linhasRecebidas': len(dados), 'totalErros': len(erros),
        'totalCorrecoes': sum(contagem.values()), 'correcoesPorRegra': dict(contagem),
        'auditoria': auditoria, 'erros': erros[:MAX_ERROS_EXIBIDOS],
        'errosTruncados': len(erros) > MAX_ERROS_EXIBIDOS
    }
    if not erros:
        output = io.StringIO()
        dados.to_csv(output, index=False, sep=';', quoting=csv.QUOTE_MINIMAL)
        resultado['arquivoCorrigidoBase64'] = base64.b64encode(output.getvalue().encode('utf-8-sig')).decode('ascii')
        resultado['nomeArquivo'] = 'plano_diretor_saneado.csv'
    return resultado


