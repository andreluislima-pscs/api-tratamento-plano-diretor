
UF_VALIDAS = {
    "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT",
    "MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO",
    "RR","SC","SP","SE","TO"
}

#SCHEMAS
SCHEMA = {
    # ===== IDENTIFICAÇÃO DO IMÓVEL =====

    "T75208_IPTU": {
        "type": "varchar",
        "max_len": 40,
        "nullable": False
    },

    "T75208_T75202_ID": {
        "type": "bigint",
        "precision": 18,
        "unsigned": True,
        "nullable": False
    },

    "T75208_CADASTRO_IMOBLILIARIO": {
        "type": "varchar",
        "max_len": 40,
        "nullable": False
    },

    # ===== ENDEREÇO =====

    "T75208_TIPO_LOGRADOURO": {
        "type": "varchar",
        "max_len": 20,
        "nullable": False
    },

    "T75208_LOGRADOURO": {
        "type": "varchar",
        "max_len": 150,
        "nullable": True
    },

    "T75208_NUMERO_LOGRADOURO": {
        "type": "varchar",
        "max_len": 10,
        "nullable": True
    },

    "T75208_COMPLEMENTO": {
        "type": "varchar",
        "max_len": 255,
        "nullable": True
    },

    "T75208_BAIRRO": {
        "type": "varchar",
        "max_len": 60,
        "nullable": True
    },

    "T75208_CEP": {
        "type": "varchar",
        "max_len": 8,
        "nullable": True,
        "custom": "cep"
    },

    "T75208_UF": {
        "type": "varchar",
        "max_len": 2,
        "nullable": True,
        "allowed_set": UF_VALIDAS
    },

    "T75208_COD_MUNIC": {
        "type": "decimal",
        "precision": 6,
        "scale": 0,
        "nullable": True,
        "unsigned": True
    },

    "T75208_NOME_MUNIC": {
        "type": "varchar",
        "max_len": 60,
        "nullable": True
    },

    # ===== STATUS E AUDITORIA =====

    "T75208_STATUS": {
        "type": "tinyint",
        "bits": 1,
        "unsigned": True,
        "nullable": False,
        "allowed_set": {"0", "1"}
    },

    "T75208_CPF_CRIOU": {
        "type": "varchar",
        "max_len": 11,
        "nullable": False,
        "custom": "cpf"
    },

    "T75208_DATA_CRIOU": {
        "type": "datetime",
        "nullable": False
    },

    "T75208_CPF_ALTEROU": {
        "type": "varchar",
        "max_len": 11,
        "nullable": True,
        "custom": "cpf"
    },

    "T75208_DATA_ALTEROU": {
        "type": "datetime",
        "nullable": True
    },

    # ===== ÁREAS DO IMÓVEL =====

    "T75208_AREA_DO_TERRENO": {
        "type": "varchar",
        "max_len": 20,
        "nullable": True
    },

    "T75208_AREA_CONSTRUIDA": {
        "type": "varchar",
        "max_len": 20,
        "nullable": True
    },

    # ===== CORREDORES =====

    "T75208_E_CORREDOR_TRAFEGO": {
        "type": "tinyint",
        "bits": 4,
        "nullable": True
    },

    "T75208_E_CORREDOR_COMERCIO_SERVICO": {
        "type": "tinyint",
        "bits": 4,
        "nullable": True
    },

    "T75208_E_CORREDOR_DEMAIS_LOGRADOURO": {
        "type": "tinyint",
        "bits": 4,
        "nullable": True
    },

    # ===== ORIGEM E INTEGRAÇÃO =====

    "T75208_ORIGEM_DADO": {
        "type": "varchar",
        "max_len": 50,
        "nullable": True
    },

    "T75208_INTEGRA_API_EXTERNA_ID": {
        "type": "bigint",
        "nullable": True
    },

    # ===== CARACTERÍSTICAS DO IMÓVEL =====

    "T75208_TIPO_IMOVEL": {
        "type": "varchar",
        "max_len": 20,
        "nullable": True
    },

    "T75208_DATA_SINCRONIZACAO": {
        "type": "datetime",
        "nullable": True
    },

    "T75208_NOME_IMOVEL_RURAL": {
        "type": "varchar",
        "max_len": 255,
        "nullable": True
    },

    "T75208_SITUACAO_IMOVEL": {
        "type": "varchar",
        "max_len": 100,
        "nullable": True
    },

    "T75208_QTD_AREA_MODULOS_FISCAIS": {
        "type": "varchar",
        "max_len": 50,
        "nullable": True
    },

    # ===== INIBIÇÃO =====

    "T75208_INIBICAO": {
        "type": "varchar",
        "max_len": 100,
        "nullable": True
    },

    "T75208_DATA_INIBICAO": {
        "type": "varchar",
        "max_len": 20,
        "nullable": True
    },

    # ===== DADOS GEOGRÁFICOS =====

    "T75208_EPSG": {
        "type": "varchar",
        "max_len": 20,
        "nullable": True
    },

    "T75208_LATITUDE": {
        "type": "varchar",
        "max_len": 50,
        "nullable": True
    },

    "T75208_LONGITUDE": {
        "type": "varchar",
        "max_len": 50,
        "nullable": True
    },

    # ===== ENDEREÇO E CANCELAMENTO =====

    "T75208_REQUER_TROCA_ENDERECO": {
        "type": "tinyint",
        "bits": 1,
        "nullable": True
    },

    "T75208_MOTIVO_CANCELAMENTO": {
        "type": "varchar",
        "max_len": 255,
        "nullable": True
    },

    "T75208_DATA_CANCELAMENTO": {
        "type": "varchar",
        "max_len": 20,
        "nullable": True
    },

    "T75208_CODIGO_LOGRADOURO": {
        "type": "varchar",
        "max_len": 50,
        "nullable": True
    },

    "T75208_NOME_CANONICO_TIPO_LOGRADOURO": {
        "type": "varchar",
        "max_len": 100,
        "nullable": True
    },

    "T75208_NOME_CANONICO_LOGRADOURO": {
        "type": "varchar",
        "max_len": 255,
        "nullable": True
    },

    "T75208_CLASSIFICACAO_VIARIA_SIGLA": {
        "type": "varchar",
        "max_len": 20,
        "nullable": True
    },

    # ===== COORDENADAS =====

    "T75208_X": {
        "type": "varchar",
        "max_len": 50,
        "nullable": True
    },

    "T75208_Y": {
        "type": "varchar",
        "max_len": 50,
        "nullable": True
    },

    "T75208_COD_IBGE": {
        "type": "bigint",
        "nullable": True
    },

    # ===== CONTROLE DE DADOS SECUNDÁRIOS =====

    "T75208_STATUS_DADOS_SEC": {
        "type": "varchar",
        "max_len": 20,
        "nullable": True
    },

    "T75208_DATA_CARGA_DADOS_SEC": {
        "type": "datetime",
        "nullable": True
    },

    "T75208_MSG_ERRO_DADOS_SEC": {
        "type": "varchar",
        "max_len": 500,
        "nullable": True
    },

    "T75208_TENTATIVAS_CARGA_DADOS_SEC": {
        "type": "int",
        "bits": 11,
        "nullable": True
    }

}