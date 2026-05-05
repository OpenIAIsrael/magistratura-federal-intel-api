from fastapi import FastAPI, Query, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import os
import re

app = FastAPI(
    title="Magistratura Federal Intel API",
    version="2.0.0",
    description="API para consultas de normativos, resoluções, leis, editais, cronogramas, jurisprudência, súmulas, doutrina e estratégia para concursos da magistratura federal."
)

API_KEY = os.getenv("API_KEY", "troque-esta-chave-em-producao")

AREAS = [
    "enam",
    "magistratura_federal",
    "objetiva",
    "discursiva",
    "sentenca_civel",
    "sentenca_penal",
    "prova_oral",
    "titulos",
    "bancas",
    "editais",
    "cronogramas",
    "normativos",
    "jurisprudencia",
    "sumulas",
    "doutrina"
]

SOURCES = [
    {"id": "enfam", "name": "ENFAM", "official": True, "type": "institucional"},
    {"id": "fgv", "name": "FGV Conhecimento", "official": True, "type": "banca"},
    {"id": "cnj", "name": "CNJ", "official": True, "type": "normativo"},
    {"id": "stf", "name": "STF", "official": True, "type": "jurisprudencia"},
    {"id": "stj", "name": "STJ", "official": True, "type": "jurisprudencia"},
    {"id": "trf3", "name": "TRF3", "official": True, "type": "tribunal"},
    {"id": "interno", "name": "Base interna", "official": False, "type": "doutrina"}
]

NORMATIVOS = [
    {
        "title": "Resolução CNJ nº 75/2009",
        "category": "normativo",
        "area": "normativos",
        "source": "cnj",
        "summary": "Dispõe sobre os concursos públicos para ingresso na carreira da magistratura.",
        "url": "https://atos.cnj.jus.br/atos/detalhar/100",
        "tags": ["cnj", "resolucao 75", "magistratura", "concurso"]
    },
    {
        "title": "Resolução CNJ nº 531/2023",
        "category": "normativo",
        "area": "enam",
        "source": "cnj",
        "summary": "Altera a Resolução 75/2009 para instituir o Exame Nacional da Magistratura.",
        "url": "https://atos.cnj.jus.br/atos/detalhar/5332",
        "tags": ["cnj", "enam", "resolucao 531"]
    },
    {
        "title": "Normativos do ENAM",
        "category": "normativo",
        "area": "enam",
        "source": "enfam",
        "summary": "Página oficial com editais, resoluções, portarias e comunicados do ENAM.",
        "url": "https://www.enfam.jus.br/enam/normativos/",
        "tags": ["enam", "enfam", "normativos", "editais"]
    }
]

RESOLUCOES = [
    {
        "title": "Resolução CNJ nº 75/2009",
        "category": "resolucao",
        "area": "normativos",
        "source": "cnj",
        "summary": "Resolução-base dos concursos para ingresso na magistratura.",
        "url": "https://atos.cnj.jus.br/atos/detalhar/100",
        "tags": ["resolucao", "cnj", "magistratura"]
    },
    {
        "title": "Resolução CNJ nº 381/2021",
        "category": "resolucao",
        "area": "normativos",
        "source": "cnj",
        "summary": "Veda entrevista pessoal reservada como etapa do certame.",
        "url": "https://atos.cnj.jus.br/atos/detalhar/3796",
        "tags": ["resolucao", "cnj", "381", "concurso"]
    },
    {
        "title": "Resolução CNJ nº 496/2023",
        "category": "resolucao",
        "area": "normativos",
        "source": "cnj",
        "summary": "Altera a Resolução CNJ 75/2009.",
        "url": "https://atos.cnj.jus.br/atos/detalhar/5030",
        "tags": ["resolucao", "cnj", "496", "magistratura"]
    },
    {
        "title": "Resolução ENFAM nº 7/2023",
        "category": "resolucao",
        "area": "enam",
        "source": "enfam",
        "summary": "Estabelece normas para a realização do ENAM.",
        "url": "https://www.enfam.jus.br/institucional/legislacao/resolucoes-da-enfam/",
        "tags": ["enfam", "enam", "resolucao"]
    }
]

LEIS = [
    {
        "title": "Constituição Federal de 1988",
        "category": "lei",
        "area": "magistratura_federal",
        "source": "planalto",
        "summary": "Base constitucional relevante para concursos da magistratura.",
        "url": "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm",
        "tags": ["cf88", "constitucional"]
    }
]

EDITAIS = [
    {
        "title": "5º Exame Nacional da Magistratura – ENAM 2026.1",
        "category": "edital",
        "area": "enam",
        "source": "fgv",
        "status": "em_andamento",
        "summary": "Edital oficial do 5º ENAM 2026.1.",
        "url": "https://conhecimento.fgv.br/sites/default/files/concursos/edital-enam-2026_1.v2.1-1_0.pdf",
        "tags": ["enam", "fgv", "2026.1"]
    },
    {
        "title": "XXI Concurso para Juiz Federal Substituto da 3ª Região",
        "category": "edital",
        "area": "magistratura_federal",
        "source": "trf3",
        "status": "encerrado",
        "summary": "Edital do XXI concurso do TRF3.",
        "url": "https://www.trf3.jus.br/documentos/roco/XX_CONCURSO/SEI_11373553_Edital_de_Abertura.pdf",
        "tags": ["trf3", "juiz federal", "edital"]
    }
]

CRONOGRAMAS = [
    {
        "title": "Cronograma ENAM 2026.1",
        "category": "cronograma",
        "area": "enam",
        "source": "fgv",
        "summary": "Cronograma oficial com datas principais do ENAM 2026.1.",
        "url": "https://conhecimento.fgv.br/sites/default/files/concursos/cronograma_enam-2026.1-1.pdf",
        "tags": ["enam", "cronograma", "fgv"]
    }
]

JURISPRUDENCIA = [
    {
        "title": "Pesquisa oficial de Jurisprudência do STF",
        "category": "jurisprudencia",
        "area": "jurisprudencia",
        "source": "stf",
        "summary": "Portal oficial de pesquisa jurisprudencial do STF.",
        "url": "https://portal.stf.jus.br/jurisprudencia/",
        "tags": ["stf", "jurisprudencia", "pesquisa oficial"]
    },
    {
        "title": "Pesquisa oficial de Jurisprudência do STJ",
        "category": "jurisprudencia",
        "area": "jurisprudencia",
        "source": "stj",
        "summary": "Portal oficial com acórdãos, súmulas, decisões monocráticas e informativos do STJ.",
        "url": "https://www.stj.jus.br/sites/portalp/Paginas/Comunicacao/Noticias/2024/24092024-STJ-lanca-pagina-renovada-de-pesquisa-de-jurisprudencia-com-mais-precisao-e-rapidez.aspx",
        "tags": ["stj", "jurisprudencia", "acordaos", "sumulas", "informativos"]
    }
]

SUMULAS = [
    {
        "title": "Súmulas Vinculantes do STF",
        "category": "sumula",
        "area": "sumulas",
        "source": "stf",
        "summary": "Página oficial das súmulas vinculantes do STF.",
        "url": "https://portal.stf.jus.br/jurisprudencia/sumariosumulas.asp?base=26",
        "tags": ["stf", "sumulas vinculantes", "sumulas"]
    },
    {
        "title": "Súmulas do STJ",
        "category": "sumula",
        "area": "sumulas",
        "source": "stj",
        "summary": "Pesquisa oficial do STJ, incluindo súmulas e jurisprudência.",
        "url": "https://www.stj.jus.br/sites/portalp/Paginas/Comunicacao/Noticias/2024/24092024-STJ-lanca-pagina-renovada-de-pesquisa-de-jurisprudencia-com-mais-precisao-e-rapidez.aspx",
        "tags": ["stj", "sumulas", "jurisprudencia"]
    }
]

DOUTRINA = [
    {
        "title": "Guia interno de estratégia para fase objetiva",
        "category": "doutrina",
        "area": "objetiva",
        "source": "interno",
        "summary": "Material-base interno para organização da fase objetiva.",
        "url": "https://exemplo.com/doutrina/objetiva",
        "tags": ["doutrina", "objetiva", "estrategia"]
    },
    {
        "title": "Guia interno de sentença cível",
        "category": "doutrina",
        "area": "sentenca_civel",
        "source": "interno",
        "summary": "Material-base interno para treino de sentença cível.",
        "url": "https://exemplo.com/doutrina/sentenca-civel",
        "tags": ["doutrina", "sentenca", "civel"]
    }
]

class StudyPlanRequest(BaseModel):
    objetivo: str
    fase: str
    horas_semanais: int
    nivel: str
    pontos_fracos: List[str] = []
    data_provavel_prova: Optional[str] = None

def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

def require_bearer(authorization: Optional[str]) -> None:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.replace("Bearer ", "", 1).strip()
    if token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())

def score_item(query: str, item: Dict) -> int:
    hay = " ".join([
        normalize(item.get("title", "")),
        normalize(item.get("summary", "")),
        normalize(item.get("area", "")),
        normalize(" ".join(item.get("tags", [])))
    ])
    q = normalize(query)
    score = 0
    for token in q.split():
        if token in hay:
            score += 2
    if q in hay:
        score += 5
    return score

def search_collection(query: str, collection: List[Dict], area: Optional[str] = None, limit: int = 5):
    results = []
    for item in collection:
        if area and item.get("area") != area:
            continue
        s = score_item(query, item)
        if s > 0:
            enriched = dict(item)
            enriched["_score"] = s
            results.append(enriched)
    results.sort(key=lambda x: (-x["_score"], x["title"]))
    return results[:limit]

@app.get("/health")
def health(authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"status": "healthy", "api": "Magistratura Federal Intel API", "version": "2.0.0", "timestamp": now_iso()}

@app.get("/v1/sources")
def list_sources(authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"sources": SOURCES}

@app.get("/v1/areas")
def list_areas(authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"areas": AREAS}

@app.get("/v1/normativos")
def get_normativos(q: str = Query(..., min_length=2), area: Optional[str] = Query(None), limit: int = Query(5, ge=1, le=20), authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"query": q, "results": search_collection(q, NORMATIVOS, area, limit), "warnings": []}

@app.get("/v1/resolucoes")
def get_resolucoes(q: str = Query(..., min_length=2), area: Optional[str] = Query(None), limit: int = Query(5, ge=1, le=20), authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"query": q, "results": search_collection(q, RESOLUCOES, area, limit), "warnings": []}

@app.get("/v1/leis")
def get_leis(q: str = Query(..., min_length=2), area: Optional[str] = Query(None), limit: int = Query(5, ge=1, le=20), authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"query": q, "results": search_collection(q, LEIS, area, limit), "warnings": []}

@app.get("/v1/editais")
def get_editais(q: str = Query(..., min_length=2), area: Optional[str] = Query(None), status: Optional[str] = Query(None), limit: int = Query(5, ge=1, le=20), authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    results = search_collection(q, EDITAIS, area, limit)
    if status:
        results = [r for r in results if r.get("status") == status]
    return {"query": q, "results": results[:limit], "warnings": []}

@app.get("/v1/cronogramas")
def get_cronogramas(q: str = Query(..., min_length=2), area: Optional[str] = Query(None), limit: int = Query(5, ge=1, le=20), authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"query": q, "results": search_collection(q, CRONOGRAMAS, area, limit), "warnings": []}

@app.get("/v1/jurisprudencia")
def get_jurisprudencia(q: str = Query(..., min_length=2), area: Optional[str] = Query(None), limit: int = Query(5, ge=1, le=20), authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"query": q, "results": search_collection(q, JURISPRUDENCIA, area, limit), "warnings": []}

@app.get("/v1/sumulas")
def get_sumulas(q: str = Query(..., min_length=2), area: Optional[str] = Query(None), limit: int = Query(5, ge=1, le=20), authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"query": q, "results": search_collection(q, SUMULAS, area, limit), "warnings": []}

@app.get("/v1/doutrina")
def get_doutrina(q: str = Query(..., min_length=2), area: Optional[str] = Query(None), limit: int = Query(5, ge=1, le=20), authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"query": q, "results": search_collection(q, DOUTRINA, area, limit), "warnings": []}

@app.get("/v1/analyze")
def analyze(q: str = Query(..., min_length=2), area: Optional[str] = Query(None), authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    norm = search_collection(q, NORMATIVOS + RESOLUCOES, area, 3)
    edi = search_collection(q, EDITAIS, area, 3)
    jur = search_collection(q, JURISPRUDENCIA, area, 3)
    sumu = search_collection(q, SUMULAS, area, 3)
    dout = search_collection(q, DOUTRINA, area, 3)

    return {
        "query": q,
        "area": area,
        "analysis": {
            "diagnostico": f"A consulta '{q}' exige leitura integrada de normativos, edital, jurisprudência, súmulas e material doutrinário aplicável.",
            "normativos_prioritarios": norm,
            "editais_prioritarios": edi,
            "jurisprudencia_prioritaria": jur,
            "sumulas_prioritarias": sumu,
            "doutrina_prioritaria": dout,
            "riscos_estrategicos": [
                "Risco de estudar por material sem aderência à fase do concurso.",
                "Risco de confundir ENAM com concurso de juiz federal substituto.",
                "Risco de ignorar súmulas e jurisprudência consolidada."
            ],
            "plano_de_acao": [
                "Identificar se a demanda é ENAM ou TRF específico.",
                "Fixar o normativo e o edital central.",
                "Cruzar legislação, jurisprudência, súmulas e doutrina aplicável."
            ]
        },
        "warnings": []
    }

@app.post("/v1/plano-estudos")
def plano_estudos(payload: StudyPlanRequest, authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)

    prioridades = [
        "Legislação seca e questões",
        "Jurisprudência STF/STJ por matéria",
        "Súmulas relevantes",
        "Treino escrito progressivo",
    ]

    if "sentenca" in payload.fase.lower():
        prioridades.insert(0, "Treino prático de sentença")
    if payload.pontos_fracos:
        prioridades.append(f"Reforço direcionado em: {', '.join(payload.pontos_fracos)}")

    return {
        "objetivo": payload.objetivo,
        "fase": payload.fase,
        "horas_semanais": payload.horas_semanais,
        "nivel": payload.nivel,
        "diagnostico": "Plano inicial gerado com foco em constância, revisão ativa, jurisprudência e aderência à fase.",
        "prioridades": prioridades,
        "execucao_semanal": [
            {
                "semana": 1,
                "foco": "Base + diagnóstico",
                "tarefas": [
                    "Questões da disciplina núcleo",
                    "Leitura de lei seca",
                    "Leitura de súmulas relevantes",
                    "Revisão de caderno de erros"
                ]
            },
            {
                "semana": 2,
                "foco": "Aprofundamento + treino escrito",
                "tarefas": [
                    "Simulado parcial",
                    "Treino de peça/sentença conforme fase",
                    "Revisão de jurisprudência",
                    "Revisão de material doutrinário"
                ]
            }
        ],
        "data_provavel_prova": payload.data_provavel_prova,
        "warnings": []
    }
