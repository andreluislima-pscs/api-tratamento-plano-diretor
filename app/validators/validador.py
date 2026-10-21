import pandas as pd
import csv
import os
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN, ROUND_CEILING, ROUND_FLOOR

from app.schemas.imovel_schemas import SCHEMA

ENTRADA = ""
SEPARADOR = ";"
LINHAS_POR_ARQUIVO_LIMITE = 50_000
CODIFICACAO = "utf-8"
ERROS_CSV = "validacao_erros.csv"
EXPORTAR_VALIDOS = True
VALIDOS_CSV = "validos.csv"
ARREDONDAMENTO_PADRAO = "HALF_UP"

FORCAR_BOOLEANOS_EM_TINYINT = True
AREA_TERRENO_NAO_NEGATIVA = True
VALIDAR_FORMATO_CPF = True
VALIDAR_FORMATO_CEP = True

VALORES_NULLOS = {"", "None", "NULL", "Null", "null", "Nil", "NaN", "nan"}

FORMATO_DATA_ACEITOS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%Y-%m-%d"
)

def arredondar_decimal_para_inteiro(d:Decimal, modo:str) -> int:
    modo = (modo or "HALF_UP").upper()
    
    if modo == "HALF_UP":
        return int(d.quantize(Decimal("0"), rounding=ROUND_HALF_UP))
    if modo == "HALF_EVEN":
        return int(d.quantize(Decimal("0"), rounding=ROUND_HALF_EVEN))
    if modo == "TRUNCATE":
        return int(d.quantize(Decimal("0"), rounding=ROUND_DOWN))
    if modo == "Flimite_minOR":
        return int(d.quantize(Decimal("0"), rounding=ROUND_FLOOR))
    if modo == "CEIL":
        return int(d.quantize(Decimal("0"), rounding=ROUND_CEILING))    
    
    return int(d.quantize(Decimal("0"), rounding=ROUND_HALF_UP))

def is_null(value:str):
    return value in VALORES_NULLOS

def converter_para_inteiro(value:str):
    try:
        return int(value)
    except Exception:
        return None

def converter_para_decimal(value:str):
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None

def formatos_data_valido(value:str):
    for formato in FORMATO_DATA_ACEITOS:
        try:
            datetime.strptime(value, formato)
            return True
        except ValueError:
            continue
    return False

def limite_tamanho_texto(value:str, max_len:int) -> bool:
    return len(value) <= max_len

def obter_limites_bigint(sem_sinal:bool):
    if sem_sinal:
        return(0, 10**18-1)
    return (-10**18 + 1, 10**18 - 1)

        
def obter_limites_int(bits:int, sem_sinal:bool = False):
    if bits >= 11:
        if sem_sinal:
            return(0, 2**32 -1)
        return (-2**31, 2**31 -1)
    
def obter_limites_tinyint(sem_sinal:bool = False):
    if sem_sinal:
        return(0, 255)
    return (-128, 127)

PADRAO_CPF = re.compile(r"^\d[0-9]{11}$")
PADRAO_CEP = re.compile(r"^\d[0-9]{8}$")

def valida_valor(coluna, regras, value):
    
    erros = []
    
    if is_null(value):
        if not regras.get("nullable", True):
            erros.append("NULL não permitido")
        return erros
    
    tipo = regras["type"]
    
    if tipo == "varchar":
        if not limite_tamanho_texto(value, regras["max_len"]):
            erros.append(f"varchar({regras['max_len']}) excedido em (len={len(value)})")

    elif tipo == "bigint":
        valor_int = converter_para_inteiro(value)

        if valor_int is None:
            erros.append("bigint inválido")
        else:
            limite_min, limite_max = obter_limites_bigint(regras.get("nao_negativo", False))

            if not (limite_min <= valor_int <= limite_max):
                erros.append(f"bigint fora de faixa [{limite_min}, {limite_max}]")

    elif tipo == "decimal":
        valor_dec = converter_para_decimal(value)

        if valor_dec is None:
            erros.append("decimal inválido.")
        else:
            prec = regras["precisao"]
            scale = regras.get("escala", 0)

            digitos = ''.join(
                ch for ch in str(valor_dec).lstrip('-') if ch.isdigit()
            )

            int_digitos = len(digitos) - scale
            frac_digitos = scale
            total_digitos = len(digitos)

            if regras.get("nao_negativo", False) and valor_dec < 0:
                erros.append("Decimal não pode ser negativo")

            if total_digitos > prec or (scale == 0 and '.' in str(valor_dec)):
                erros.append(f"decimal({prec}, {scale}) excedido")

            if scale == 0:
                if '.' in str(value) or ',' in str(value):
                    erros.append("decimal sem casas decimais esperado (scale=0)")     
    elif tipo == "tinyint":
        valor_int = converter_para_inteiro(value)
        if valor_int is None:
            erros.append("tinyint inválido.")
        else:
            limite_min, limite_max = obter_limites_tinyint(regras.get("bits", 4), regras("sem_sinal", False))
            if not (limite_min <= valor_int <= limite_max):
                erros.append(f"tinyint fora de faixa [{limite_min},{limite_max}]")
            if "allowed set" in regras and str(valor_int) not in regras["allowed_set"]:
                erros.append(f"valor deve ser um de {sorted(regras["allowed_set"])}")
            elif FORCAR_BOOLEANOS_EM_TINYINT and regras.get("bits", 4) in (1,4) and str(valor_int) not in {"0","1"}:
                erros.append("esperando booleano {0,1}")
        
    elif tipo == "int":
        valor_int = None
        if regras.get("accept_decimal", False) and (("." in value) or ("," in value)):
            val_norm = value.replace(",", ".")
            valor_dec = converter_para_decimal(val_norm)
            if valor_dec is None:
                erros.append("Valor decimal inválido para conversão em inteiro.")
            else:
                modo = regras.get("rouding", ARREDONDAMENTO_PADRAO)
                valor_int = arredondar_decimal_para_inteiro(valor_dec, modo)
        else:
            valor_int = converter_para_inteiro(value)
        if valor_int is None:
            erros.append("inteiro inválido.")
        else:
            limite_min, limite_max = obter_limites_int(regras.get("bits", 11), regras.get("sem_sinal", False))
            if not (limite_min <= valor_int <= limite_max):
                erros.append(f"inteiro fora de faixa: [{limite_min}, {limite_max}]")
            if AREA_TERRENO_NAO_NEGATIVA and coluna == "T75208_AREA_DO_TERRENO" and valor_int < 0:
                erros.append("Área do terreno não pode ser negativa.")
    elif tipo == "datetime":
        if not formatos_data_valido (value):
            erros.append("datetime inválido (formatos aceitos: YYYY-MM-DD HH:MM:SS, YYYY-MM-DDTHH:MM:SS, DD/MM/YYYY HH:MM[:SS], YYYY-MM-DD) )")  
    else:
        erros.append(f"tipo não suportado:{tipo}")
        
    if "allowed_set" in regras and not is_null(value):
        if value not in regras["allowed_set"]:
            if regras["type"] == "varchar":
                erros.append(f"valor for do conjunto permitido: {sorted(regras['allowed_set'])}")
    
    custom  = regras.get("custom")
    if custom == "cpf" and VALIDAR_FORMATO_CPF and not is_null(value):
        if not PADRAO_CPF.fullmatch(value):
            erros.append("CPF deve conter exatamente 11 digitos(apenas números)")                
    if custom == "cep" and VALIDAR_FORMATO_CEP and not is_null(value):
        if not PADRAO_CEP.fullmatch(value):
            erros.append("CEP deve conter exatamente 8 digitos(apenas números)")
    return erros

def validar_csv():
    os.makedirs(os.path.dirname(ERROS_CSV) or ".", exist_ok=True)
    if EXPORTAR_VALIDOS:
        if os.path.exists(VALIDOS_CSV):
            os.remove(VALIDOS_CSV)
            
        with open(ERROS_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                "arquivo_parte",
                "linha_global",
                "linha_no_chunk",
                "T75208_IPTU",       
                "coluna",
                "valor",
                "erro"
            ])
            reader = pd.read_csv(
            ENTRADA,
            sep=SEPARADOR,
            engine="python",
            dtype=str,             # mantém tudo como string para validação fiel ao DDL
            chunksize=LINHAS_POR_ARQUIVO_LIMITE,
            on_bad_lines="error",
            encoding=CODIFICACAO,
            quotechar='"'
    )
            
    linha_global = 0
    for i, chunk in enumerate(reader, start=1):
        # garante colunas esperadas
        faltantes = [c for c in SCHEMA.keys() if c not in chunk.columns]
        extras = [c for c in chunk.columns if c not in SCHEMA]
        if faltantes:
            raise ValueError(f"Colunas faltando no CSV: {faltantes}")
        if extras:
            # não dá erro fatal, mas avisa
            print(f"Aviso: colunas extras não presentes no DDL: {extras}")

        # normaliza nulos como strings padrão
        chunk = chunk.fillna("")

        erros_lote = []
        validos_lote = []

        for r_idx, row in chunk.iterrows():
            iptu_chave = (row.get("T75208_IPTU") or "").strip()
            linha_global += 1
            linha_no_chunk = r_idx + 1  # 1-based dentro do chunk

            linha_ok = True
            for col, spec in SCHEMA.items():
                val = row[col]
                # padroniza "NULL"
                if val is None:
                    val = ""
                val_str = str(val).strip()

                msgs = valida_valor(col, spec, val_str)
                if msgs:
                    linha_ok = False
                    for m in msgs:
                        erros_lote.append([
                            f"parte_{i:03d}",
                            linha_global,
                            linha_no_chunk,
                            iptu_chave,   # << NOVO
                            col,
                            val_str,
                            m
                        ])

            if linha_ok and EXPORTAR_VALIDOS:
                # mantém ordem das colunas do SCHEMA
                validos_lote.append([row[c] for c in SCHEMA.keys()])

        # grava erros do chunk
        if erros_lote:
            with open(ERROS_CSV, "a", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerows(erros_lote)

        # grava válidos do chunk (opcional)
        if EXPORTAR_VALIDOS and validos_lote:
            # se for a primeira escrita, escreve cabeçalho
            header = list(SCHEMA.keys())
            write_header = (i == 1 and not os.path.exists(VALIDOS_CSV))
            with open(VALIDOS_CSV, "a", newline="", encoding="utf-8") as f:
                w = csv.writer(f, quoting=csv.QUOTE_ALL)
                if write_header:
                    w.writerow(header)
                w.writerows(validos_lote)

        print(f"Chunk {i:03d} validado. Erros: {len(erros_lote)}")

    print(f"Validação concluída. Relatório: {ERROS_CSV}")
    if EXPORTAR_VALIDOS:
        print(f"Linhas válidas exportadas em: {VALIDOS_CSV}")

if __name__ == "__main__":
    validar_csv()
         