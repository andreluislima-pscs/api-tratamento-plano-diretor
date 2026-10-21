
from __future__ import annotations
import io
import re
from collections import Counter
from decimal import Decimal, InvalidOperation
import pandas as pd

ABAS = {
    'Plano Diretor': ['Nome','Descrição','Link','Data de início','Data de término','Cnpj Instituição','Ação'],
    'Lei': ['Nome','Descrição','Link'],
    'Zoneamento': ['Nome','Descrição','Tipo','Capitulação','Descrição da Capitulação'],
    'Atividades Permitidas': ['Nome do Plano Diretor','Código CNAE','Zoneamento','Operação','Condição'],
    'Imóvel': ['Nome do Plano Diretor','Zoneamento','Inscrição Imobiliária','Cadastro Imobiliário','Bairro','Tipo de logradouro','Logradouro','Número','Complemento','CEP','Operação','Área Terreno M²','Área Construída Total M²'],
    'Atividades Especiais': ['Código CNAE','Descrição','Operação'],
}

LIMITES_REFERENCIA = {'Tipo de logradouro':20, 'Logradouro':150,'Número':10,'Complemento':255,'Bairro':60,'CEP':8,'Inscrição Imobiliária':20,'Cadastro Imobiliário':40}
MAX_EXIBIR = 150

def ajustar(campo:str, valor:str) -> str:
    novo = valor.strip()
    if campo == "CEP":
        novo = re.sub(r'[.\-\s]', '', novo)
    if campo == "Número" and re.fullmatch(r'\d+\.0', novo):
        novo = novo[:-2]
    return novo

def decimal_br(valor:str) -> bool:
    if not re.fullmatch(r'(?:\d+|\d{1,3}(?:\.\d{3})+)(?:,\d{1,2})?', valor):
        return False
    try:
        return Decimal (valor.replace(".", "").replace(",", "."))>= 0
    except InvalidOperation:
        return False

def ler_xls(conteudo:bytes)-> dict[str, pd.DataFrame]:
    try:
        return pd.read_excel(io.BytesIO(conteudo), sheet_name=None, dtype=str,keep_default_na=False, engine="openpyxl")
    except Exception as e:
        raise ValueError(f"Não foi possível ler a planilha XLSX: {str(e)}") from e
    
def analisar (conteudo:bytes, exportar:bool=False):
    abas = ler_xls(conteudo)
    
    faltando = [nome for nome in ABAS if nome not in abas]
    if faltando:
        raise ValueError("Abas obrigatorias ausentes: "+", ".join(faltando))
    
    extras_abas = [a for a in abas if a not in ABAS]
    if extras_abas:
        raise ValueError("Abas não previstas "+" ".join(extras_abas))
    for nome, colunas in ABAS.items():
        recebidas = list(abas[nome].columns)
        if recebidas != colunas:
            raise ValueError (f"Cabeçalho incompatível na aba{nome}. Aguardando:{colunas}; recebido: {recebidas}")
          
    erros, avisos, auditoria = [], [], []
    contagem = Counter()
    estatisticas = {}
    
    def adicionar(destino, aba, linha, col, valor, desc):
        destino.append({'aba':aba, 'linha':linha, 'coluna':col, 'valor':str(valor), 'mensagem':desc})
    for nome, df in abas.items():
        if len(df) > 25000:
            raise ValueError(f'Aba{nome} tem mais de 25.000 registros; limite do prototipo.')
        estatisticas[nome] = len(df)
        for coluna in df.columns:
            antes = df[coluna].fillna('').astype(str)
            depois = antes.map(lambda v: ajustar(coluna, v))
            alterados = antes.ne(depois)
            contagem[coluna] += int(alterados.sum())
            if len(auditoria)<MAX_EXIBIR:
                for indice in df. index[alterados][:MAX_EXIBIR-len(auditoria)]:
                    auditoria.append({'aba':nome, 'linha':int(indice)+2, 
                                    'coluna':coluna,'antes':antes.at[indice],
                                    'depois':depois.at[indice]})
            df[coluna] = depois
        if nome == 'Imóvel':
            for indice, linha in df.iterrows():
                n = int(indice)+2
                for coluna, max_len in LIMITES_REFERENCIA.items():
                    valor = linha[coluna]
                    if len(valor)>max_len:
                        adicionar(erros,nome,n,coluna,valor,f'Tamanho {len(valor)} excede limite de referência {max_len}; confirmar DDL/API')
                if not linha['Inscrição Imobiliária']:
                    adicionar(erros,nome,n,'Inscrição Imobiliária','', 'Identificador obrigatório vazio')
                if not re.fullmatch(r'\d{8}',linha['CEP']):
                    adicionar(erros,nome,n,'CEP',linha['CEP'],'CEP deve conter 8 dígitos')
                for coluna in ('Área Terreno M²','Área Construída Total M²'):
                    if not decimal_br(linha[coluna]):
                        adicionar(erros,nome,n,coluna,linha[coluna],'Área numérica não negativa, com vírgula e até 2 casas decimais')
            repetidos = df['Inscrição Imobiliária'].duplicated(keep=False) & df['Inscrição Imobiliária'].ne('')
            for indice in df.index[repetidos]:
                adicionar(erros,nome,int(indice)+2,'Inscrição Imobiliária',df.at[indice,'Inscrição Imobiliária'],'Inscrição imobiliária repetida; revisar')
        if nome == 'Atividades Permitidas':
            for indice, valor in df['Código CNAE'].items():
                if not re.fullmatch(r'\d{7}',valor):
                    adicionar(avisos,nome,int(indice)+2,'Código CNAE',valor,'Conferir CNAE: esperado código de 7 dígitos no arquivo de referência')
            mask = df.duplicated(subset=['Nome do Plano Diretor','Código CNAE','Zoneamento'],keep=False)
            for indice in df.index[mask]:
                adicionar(erros,nome,int(indice)+2,'Código CNAE',df.at[indice,'Código CNAE'],'Combinação plano/CNAE/zoneamento repetida')
        if nome == 'Plano Diretor':
            for indice, valor in df['Cnpj Instituição'].items():
                if not re.fullmatch(r'\d{14}',valor):
                    adicionar(erros,nome,int(indice)+2,'Cnpj Instituição',valor,'CNPJ exige 14 dígitos (sem validar dígitos verificadores)')
    sucesso = not erros
    resposta = {'sucesso':sucesso,'modo':'SIMULACAO_SEM_BANCO',
                'abas':estatisticas,'linhasRecebidas':sum(estatisticas.values()),
                'totalCorrecoes':sum(contagem.values()),
                'correcoesPorCampo':dict((c,v) for c,v in contagem.items() if v),
                'totalErros':len(erros),'totalAvisos':len(avisos),
                'erros':erros[:MAX_EXIBIR], 'avisos':avisos[:MAX_EXIBIR],
                'auditoria':auditoria,
                'resultadosParciais':len(erros)>MAX_EXIBIR or len(avisos)>MAX_EXIBIR}
    if exportar and sucesso:
        destino=io.BytesIO()
        with pd.ExcelWriter(destino,engine='openpyxl') as writer:
            for nome, df in abas.items():
                df.to_excel(writer,sheet_name=nome,index=False)
                sheet=writer.sheets[nome]
                # Código CNAE e identificadores continuam texto; evita conversão para número.
                for coluna in ('Código CNAE','Inscrição Imobiliária','Cadastro Imobiliário','CEP','Cnpj Instituição'):
                    if coluna in df:
                        idx=df.columns.get_loc(coluna)+1
                        for celulas in sheet.iter_cols(min_col=idx,max_col=idx,min_row=2):
                            for cel in celulas:cel.number_format='@'
        return resposta,destino.getvalue()
    return resposta,None
