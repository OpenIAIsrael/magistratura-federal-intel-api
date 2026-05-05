from fastapi import FastAPI, Query, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import os
import re

app = FastAPI(
    title="Magistratura Federal Intel API",
    version="4.0.0",
    description="API para concursos da magistratura federal com todos os TRFs, matérias, prioridades por fase e banca, normativos, jurisprudência, súmulas, doutrina e análise estratégica."
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
    "doutrina",
    "materias",
    "formacao_humanistica",
    "direitos_humanos"
]

TRILHAS = [
    {"id": "enam", "name": "ENAM", "description": "Trilha de habilitação para a magistratura."},
    {"id": "magistratura_federal", "name": "Magistratura Federal", "description": "Trilha para Juiz Federal Substituto."},
    {"id": "formacao_humanistica", "name": "Formação Humanística", "description": "Noções Gerais de Direito e Formação Humanística."}
]

TRIBUNAIS = [
    {"id": "trf1", "name": "TRF1", "official": True, "concursos_url": "https://www.trf1.jus.br/trf1/concursos/concursos-magistrados"},
    {"id": "trf2", "name": "TRF2", "official": True, "concursos_url": "https://www.trf2.jus.br/trf2/consultas-e-servicos/concursos-publicos-para-magistrados"},
    {"id": "trf3", "name": "TRF3", "official": True, "concursos_url": "https://www.trf3.jus.br/concurso-magistrado/"},
    {"id": "trf4", "name": "TRF4", "official": True, "concursos_url": "https://www.trf4.jus.br/trf4/controlador.php?acao=pagina_visualizar&id_pagina=2424"},
    {"id": "trf5", "name": "TRF5", "official": True, "concursos_url": "https://www.trf5.jus.br/index.php/magistrados"},
    {"id": "trf6", "name": "TRF6", "official": True, "concursos_url": "https://portal.trf6.jus.br/concursos-2/concursos-magistrados/"}
]

BANCAS = [
    {
        "id": "fgv",
        "name": "FGV",
        "style": "enunciados mais extensos, interdisciplinaridade moderada, cobrança forte de literalidade combinada com aplicação prática",
        "focus": ["lei seca", "jurisprudencia", "contexto prático", "tempo de prova"]
    },
    {
        "id": "cebraspe",
        "name": "Cebraspe",
        "style": "alta densidade conceitual, pegadinhas técnicas, precisão terminológica e perfil mais analítico",
        "focus": ["conceito", "jurisprudencia", "assertivas", "interpretação fina"]
    },
    {
        "id": "comissao_propria",
        "name": "Comissão Própria",
        "style": "perfil mais autoral, maior variação por examinador e incidência forte de tradição do tribunal",
        "focus": ["programa", "perfil institucional", "doutrina", "dissertacao"]
    }
]

SOURCES = [
    {"id": "cnj", "name": "CNJ", "official": True, "type": "normativo"},
    {"id": "enfam", "name": "ENFAM", "official": True, "type": "institucional"},
    {"id": "fgv", "name": "FGV Conhecimento", "official": True, "type": "banca"},
    {"id": "stf", "name": "STF", "official": True, "type": "jurisprudencia"},
    {"id": "stj", "name": "STJ", "official": True, "type": "jurisprudencia"},
    {"id": "planalto", "name": "Planalto", "official": True, "type": "legislacao"},
    {"id": "interno", "name": "Base interna", "official": False, "type": "doutrina"},
    {"id": "trf1", "name": "TRF1", "official": True, "type": "tribunal"},
    {"id": "trf2", "name": "TRF2", "official": True, "type": "tribunal"},
    {"id": "trf3", "name": "TRF3", "official": True, "type": "tribunal"},
    {"id": "trf4", "name": "TRF4", "official": True, "type": "tribunal"},
    {"id": "trf5", "name": "TRF5", "official": True, "type": "tribunal"},
    {"id": "trf6", "name": "TRF6", "official": True, "type": "tribunal"}
]

MATERIAS = [
    {"slug": "direito-constitucional", "name": "Direito Constitucional", "trilhas": ["enam", "magistratura_federal"], "grupo": "nucleo_essencial", "fase": ["objetiva", "discursiva", "oral"], "peso_base": 10, "summary": "Disciplina central da magistratura.", "tags": ["constitucional", "cf88", "direitos fundamentais"]},
    {"slug": "direito-administrativo", "name": "Direito Administrativo", "trilhas": ["enam", "magistratura_federal"], "grupo": "nucleo_essencial", "fase": ["objetiva", "discursiva", "oral"], "peso_base": 9, "summary": "Disciplina central da magistratura.", "tags": ["administrativo", "atos", "poderes", "licitacoes"]},
    {"slug": "direito-civil", "name": "Direito Civil", "trilhas": ["enam", "magistratura_federal"], "grupo": "nucleo_essencial", "fase": ["objetiva", "discursiva", "sentenca_civel", "oral"], "peso_base": 10, "summary": "Disciplina base para sentença cível.", "tags": ["civil", "obrigacoes", "contratos", "familia"]},
    {"slug": "direito-processual-civil", "name": "Direito Processual Civil", "trilhas": ["enam", "magistratura_federal"], "grupo": "nucleo_essencial", "fase": ["objetiva", "discursiva", "sentenca_civel", "oral"], "peso_base": 10, "summary": "Disciplina central para sentença cível.", "tags": ["processo civil", "cpc", "recursos", "execucao"]},
    {"slug": "direito-penal", "name": "Direito Penal", "trilhas": ["enam", "magistratura_federal"], "grupo": "nucleo_essencial", "fase": ["objetiva", "discursiva", "sentenca_penal", "oral"], "peso_base": 10, "summary": "Disciplina central para sentença penal.", "tags": ["penal", "crimes", "penas"]},
    {"slug": "direito-processual-penal", "name": "Direito Processual Penal", "trilhas": ["magistratura_federal"], "grupo": "nucleo_essencial", "fase": ["objetiva", "discursiva", "sentenca_penal", "oral"], "peso_base": 10, "summary": "Disciplina central para fase penal.", "tags": ["processo penal", "cpp", "provas", "acao penal"]},
    {"slug": "direito-empresarial", "name": "Direito Empresarial", "trilhas": ["enam", "magistratura_federal"], "grupo": "complementar_relevante", "fase": ["objetiva", "discursiva", "oral"], "peso_base": 6, "summary": "Disciplina recorrente.", "tags": ["empresarial", "falencia", "recuperacao", "societario"]},
    {"slug": "direito-tributario", "name": "Direito Tributário", "trilhas": ["magistratura_federal"], "grupo": "federal_estrategico", "fase": ["objetiva", "discursiva", "oral"], "peso_base": 8, "summary": "Disciplina estratégica da magistratura federal.", "tags": ["tributario", "ctn", "tributos", "reforma tributaria"]},
    {"slug": "direito-previdenciario", "name": "Direito Previdenciário", "trilhas": ["magistratura_federal"], "grupo": "federal_estrategico", "fase": ["objetiva", "discursiva", "oral"], "peso_base": 8, "summary": "Disciplina estratégica no recorte federal.", "tags": ["previdenciario", "beneficios", "seguridade"]},
    {"slug": "direito-ambiental", "name": "Direito Ambiental", "trilhas": ["magistratura_federal"], "grupo": "federal_estrategico", "fase": ["objetiva", "discursiva", "oral"], "peso_base": 6, "summary": "Disciplina relevante para a magistratura.", "tags": ["ambiental", "licenciamento", "responsabilidade ambiental"]},
    {"slug": "direito-internacional", "name": "Direito Internacional Público e Privado / Comunitário", "trilhas": ["magistratura_federal"], "grupo": "federal_estrategico", "fase": ["objetiva", "oral"], "peso_base": 5, "summary": "Disciplina típica de prova federal.", "tags": ["internacional", "comunitario", "cooperacao"]},
    {"slug": "direito-financeiro-e-economico", "name": "Direito Financeiro e Econômico", "trilhas": ["magistratura_federal"], "grupo": "federal_estrategico", "fase": ["objetiva", "oral"], "peso_base": 5, "summary": "Disciplina relevante no recorte federal.", "tags": ["financeiro", "economico", "orcamento"]},
    {"slug": "direito-eleitoral", "name": "Direito Eleitoral", "trilhas": ["magistratura_federal"], "grupo": "complementar_relevante", "fase": ["objetiva", "oral"], "peso_base": 4, "summary": "Disciplina cobrada nas listas mínimas.", "tags": ["eleitoral", "inelegibilidade"]},
    {"slug": "direito-do-consumidor", "name": "Direito do Consumidor", "trilhas": ["magistratura_federal"], "grupo": "complementar_relevante", "fase": ["objetiva", "discursiva"], "peso_base": 4, "summary": "Disciplina autônoma na matriz.", "tags": ["consumidor", "cdc"]},
    {"slug": "direito-da-crianca-e-do-adolescente", "name": "Direito da Criança e do Adolescente", "trilhas": ["magistratura_federal"], "grupo": "complementar_relevante", "fase": ["objetiva", "discursiva", "oral"], "peso_base": 4, "summary": "Disciplina autônoma na matriz.", "tags": ["eca", "crianca", "adolescente"]},
    {"slug": "direitos-humanos", "name": "Direitos Humanos", "trilhas": ["enam", "magistratura_federal"], "grupo": "estruturante", "fase": ["objetiva", "discursiva", "oral"], "peso_base": 7, "summary": "Disciplina expressamente reforçada na matriz.", "tags": ["direitos humanos", "sistema interamericano"]},
    {"slug": "direito-do-trabalho", "name": "Direito do Trabalho", "trilhas": ["magistratura_federal"], "grupo": "complementar_relevante", "fase": ["objetiva", "oral"], "peso_base": 3, "summary": "Disciplina relevante de formação geral.", "tags": ["trabalho", "clt"]},
    {"slug": "direito-processual-do-trabalho", "name": "Direito Processual do Trabalho", "trilhas": ["magistratura_federal"], "grupo": "complementar_relevante", "fase": ["objetiva", "oral"], "peso_base": 3, "summary": "Disciplina relevante de formação geral.", "tags": ["processo do trabalho"]},
    {"slug": "formacao-humanistica", "name": "Formação Humanística", "trilhas": ["enam", "magistratura_federal", "formacao_humanistica"], "grupo": "formacao_humanistica", "fase": ["objetiva", "oral"], "peso_base": 7, "summary": "Noções Gerais de Direito e Formação Humanística.", "tags": ["humanistica", "etica", "filosofia", "psicologia", "antidiscriminacao", "direito digital"]}
]

TRF_COMPETITIONS = [
    {"tribunal": "trf1", "title": "XVIII Concurso para Juiz Federal Substituto da 1ª Região", "status": "em_andamento", "source": "trf1", "summary": "Concurso público para magistrados do TRF1.", "url": "https://www.trf1.jus.br/trf1/concursos/concursos-magistrados", "tags": ["trf1", "juiz federal", "edital"]},
    {"tribunal": "trf2", "title": "XIX Concurso para Juiz Federal Substituto da 2ª Região", "status": "em_andamento", "source": "trf2", "summary": "Concurso público para magistrados do TRF2.", "url": "https://www.trf2.jus.br/trf2/consultas-e-servicos/concursos-publicos-para-magistrados", "tags": ["trf2", "juiz federal", "edital"]},
    {"tribunal": "trf3", "title": "XXI Concurso para Juiz Federal Substituto da 3ª Região", "status": "encerrado", "source": "trf3", "summary": "Concurso público para magistrados do TRF3.", "url": "https://www.trf3.jus.br/concurso-magistrado/", "tags": ["trf3", "juiz federal", "edital"]},
    {"tribunal": "trf4", "title": "XVIII Concurso para Juiz Federal Substituto da 4ª Região", "status": "encerrado", "source": "trf4", "summary": "Concurso público para magistrados do TRF4.", "url": "https://www.trf4.jus.br/trf4/controlador.php?acao=pagina_visualizar&id_pagina=2424", "tags": ["trf4", "juiz federal", "edital"]},
    {"tribunal": "trf5", "title": "XV Concurso para Juiz Federal Substituto da 5ª Região", "status": "em_andamento", "source": "trf5", "summary": "Concurso público para magistrados do TRF5.", "url": "https://www.trf5.jus.br/index.php/magistrados", "tags": ["trf5", "juiz federal", "edital"]},
    {"tribunal": "trf6", "title": "I Concurso para Juiz Federal Substituto da 6ª Região", "status": "em_andamento", "source": "trf6", "summary": "Concurso público para magistrados do TRF6.", "url": "https://portal.trf6.jus.br/concursos-2/concursos-magistrados/", "tags": ["trf6", "juiz federal", "edital"]}
]

NORMATIVOS = [
    {"title": "Resolução CNJ nº 75/2009", "category": "normativo", "area": "normativos", "source": "cnj", "summary": "Dispõe sobre os concursos públicos para ingresso na carreira da magistratura.", "url": "https://atos.cnj.jus.br/atos/detalhar/100", "tags": ["cnj", "resolucao 75", "magistratura", "concurso"]},
    {"title": "Normativos do ENAM", "category": "normativo", "area": "enam", "source": "enfam", "summary": "Página oficial com editais, resoluções, portarias e comunicados do ENAM.", "url": "https://www.enfam.jus.br/enam/normativos/", "tags": ["enam", "enfam", "normativos"]}
]

RESOLUCOES = [
    {"title": "Resolução CNJ nº 75/2009", "category": "resolucao", "area": "normativos", "source": "cnj", "summary": "Resolução-base dos concursos para ingresso na magistratura.", "url": "https://atos.cnj.jus.br/atos/detalhar/100", "tags": ["resolucao", "cnj"]},
    {"title": "Resolução Enfam nº 13/2025", "category": "resolucao", "area": "enam", "source": "enfam", "summary": "Normas para realização do ENAM.", "url": "https://www.enfam.jus.br/institucional/legislacao/resolucoes-da-enfam/", "tags": ["enfam", "enam", "resolucao"]}
]

LEIS = [
    {"title": "Constituição Federal de 1988", "category": "lei", "area": "magistratura_federal", "source": "planalto", "summary": "Base constitucional relevante.", "url": "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm", "tags": ["cf88", "constitucional"]},
    {"title": "Código Civil", "category": "lei", "area": "magistratura_federal", "source": "planalto", "summary": "Lei-base para Direito Civil.", "url": "https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm", "tags": ["civil"]},
    {"title": "Código de Processo Civil", "category": "lei", "area": "magistratura_federal", "source": "planalto", "summary": "Lei-base para Processo Civil.", "url": "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm", "tags": ["cpc"]},
    {"title": "Código Penal", "category": "lei", "area": "magistratura_federal", "source": "planalto", "summary": "Lei-base para Direito Penal.", "url": "https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm", "tags": ["penal"]},
    {"title": "Código de Processo Penal", "category": "lei", "area": "magistratura_federal", "source": "planalto", "summary": "Lei-base para Processo Penal.", "url": "https://www.planalto.gov.br/ccivil_03/decreto-lei/del3689.htm", "tags": ["cpp"]}
]

CRONOGRAMAS = [
    {"tribunal": "enam", "title": "Cronograma ENAM", "category": "cronograma", "area": "enam", "source": "fgv", "summary": "Página oficial com cronograma do ENAM.", "url": "https://conhecimento.fgv.br/exames/enam/5exame", "tags": ["enam", "cronograma", "fgv"]},
    {"tribunal": "trf1", "title": "Cronograma/andamento TRF1", "category": "cronograma", "area": "magistratura_federal", "source": "trf1", "summary": "Página oficial do concurso de magistrados do TRF1.", "url": "https://www.trf1.jus.br/trf1/concursos/concursos-magistrados", "tags": ["trf1", "cronograma"]},
    {"tribunal": "trf2", "title": "Cronograma/andamento TRF2", "category": "cronograma", "area": "magistratura_federal", "source": "trf2", "summary": "Página oficial do concurso de magistrados do TRF2.", "url": "https://www.trf2.jus.br/trf2/consultas-e-servicos/concursos-publicos-para-magistrados", "tags": ["trf2", "cronograma"]},
    {"tribunal": "trf3", "title": "Cronograma/andamento TRF3", "category": "cronograma", "area": "magistratura_federal", "source": "trf3", "summary": "Página oficial do concurso de magistrados do TRF3.", "url": "https://www.trf3.jus.br/concurso-magistrado/editais", "tags": ["trf3", "cronograma"]},
    {"tribunal": "trf4", "title": "Cronograma/andamento TRF4", "category": "cronograma", "area": "magistratura_federal", "source": "trf4", "summary": "Página oficial do concurso de magistrados do TRF4.", "url": "https://www.trf4.jus.br/trf4/controlador.php?acao=pagina_visualizar&id_pagina=2424", "tags": ["trf4", "cronograma"]},
    {"tribunal": "trf5", "title": "Cronograma/andamento TRF5", "category": "cronograma", "area": "magistratura_federal", "source": "trf5", "summary": "Página oficial do concurso de magistrados do TRF5.", "url": "https://www.trf5.jus.br/index.php/magistrados", "tags": ["trf5", "cronograma"]},
    {"tribunal": "trf6", "title": "Cronograma/andamento TRF6", "category": "cronograma", "area": "magistratura_federal", "source": "trf6", "summary": "Página oficial do concurso de magistrados do TRF6.", "url": "https://portal.trf6.jus.br/concursos-2/concursos-magistrados/", "tags": ["trf6", "cronograma"]}
]

JURISPRUDENCIA = [
    {"title": "Pesquisa oficial de Jurisprudência do STF", "category": "jurisprudencia", "area": "jurisprudencia", "source": "stf", "summary": "Portal oficial de jurisprudência do STF.", "url": "https://portal.stf.jus.br/jurisprudencia/", "tags": ["stf", "jurisprudencia"]},
    {"title": "Pesquisa oficial de Jurisprudência do STJ", "category": "jurisprudencia", "area": "jurisprudencia", "source": "stj", "summary": "Portal oficial do STJ para jurisprudência.", "url": "https://www.stj.jus.br/sites/portalp/Paginas/Comunicacao/Noticias/2024/24092024-STJ-lanca-pagina-renovada-de-pesquisa-de-jurisprudencia-com-mais-precisao-e-rapidez.aspx", "tags": ["stj", "jurisprudencia", "sumulas", "informativos"]}
]

SUMULAS = [
    {"title": "Súmulas Vinculantes do STF", "category": "sumula", "area": "sumulas", "source": "stf", "summary": "Página oficial das súmulas vinculantes do STF.", "url": "https://portal.stf.jus.br/jurisprudencia/sumariosumulas.asp?base=26", "tags": ["stf", "sumulas"]},
    {"title": "Súmulas do STJ", "category": "sumula", "area": "sumulas", "source": "stj", "summary": "Portal oficial do STJ com súmulas e jurisprudência.", "url": "https://www.stj.jus.br/sites/portalp/Paginas/Comunicacao/Noticias/2024/24092024-STJ-lanca-pagina-renovada-de-pesquisa-de-jurisprudencia-com-mais-precisao-e-rapidez.aspx", "tags": ["stj", "sumulas"]}
]

DOUTRINA = [
    {"title": "Guia interno de estratégia para fase objetiva", "category": "doutrina", "area": "objetiva", "source": "interno", "summary": "Material interno para fase objetiva.", "url": "https://exemplo.com/doutrina/objetiva", "tags": ["objetiva", "estrategia"]},
    {"title": "Guia interno de sentença cível", "category": "doutrina", "area": "sentenca_civel", "source": "interno", "summary": "Material interno para sentença cível.", "url": "https://exemplo.com/doutrina/sentenca-civel", "tags": ["sentenca", "civel"]}
]

class StudyPlanRequest(BaseModel):
    objetivo: str
    fase: str
    horas_semanais: int
    nivel: str
    trilha: Optional[str] = None
    banca: Optional[str] = None
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
        normalize(item.get("name", "")),
        normalize(item.get("summary", "")),
        normalize(item.get("area", "")),
        normalize(" ".join(item.get("tags", []))),
        normalize(" ".join(item.get("trilhas", []))) if isinstance(item.get("trilhas"), list) else "",
        normalize(" ".join(item.get("fase", []))) if isinstance(item.get("fase"), list) else ""
    ])
    q = normalize(query)
    score = 0
    for token in q.split():
        if token in hay:
            score += 2
    if q in hay:
        score += 5
    return score

def search_collection(query: str, collection: List[Dict], limit: int = 10):
    results = []
    for item in collection:
        s = score_item(query, item)
        if s > 0:
            enriched = dict(item)
            enriched["_score"] = s
            results.append(enriched)
    results.sort(key=lambda x: (-x["_score"], x.get("title", x.get("name", ""))))
    return results[:limit]

def compute_priority(materia: Dict, fase: Optional[str], banca: Optional[str], trilha: Optional[str]) -> int:
    score = int(materia.get("peso_base", 1))
    if fase and fase in materia.get("fase", []):
        score += 4
    if trilha and trilha in materia.get("trilhas", []):
        score += 3
    if banca == "fgv":
        if materia["slug"] in ["direito-constitucional", "direito-administrativo", "direito-civil", "direito-processual-civil", "direito-penal", "direito-processual-penal"]:
            score += 2
    if banca == "cebraspe":
        if materia["slug"] in ["direito-constitucional", "direito-administrativo", "direitos-humanos"]:
            score += 2
    return score

@app.get("/health")
def health(authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"status": "healthy", "api": "Magistratura Federal Intel API", "version": "4.0.0", "timestamp": now_iso()}

@app.get("/v1/sources")
def list_sources(authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"sources": SOURCES}

@app.get("/v1/areas")
def list_areas(authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"areas": AREAS}

@app.get("/v1/trilhas")
def list_trilhas(authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"trilhas": TRILHAS}

@app.get("/v1/tribunais")
def list_tribunais(authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"tribunais": TRIBUNAIS}

@app.get("/v1/bancas")
def list_bancas(authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"bancas": BANCAS}

@app.get("/v1/materias")
def get_materias(
    q: str = Query(..., min_length=2),
    trilha: Optional[str] = Query(None),
    fase: Optional[str] = Query(None),
    banca: Optional[str] = Query(None),
    limit: int = Query(15, ge=1, le=50),
    authorization: Optional[str] = Header(default=None)
):
    require_bearer(authorization)
    results = search_collection(q, MATERIAS, 50)
    if trilha:
        results = [r for r in results if trilha in r.get("trilhas", [])]
    if fase:
        results = [r for r in results if fase in r.get("fase", [])]
    for r in results:
        r["priority_score"] = compute_priority(r, fase, banca, trilha)
    results.sort(key=lambda x: (-x["priority_score"], -x.get("_score", 0), x["name"]))
    return {"query": q, "trilha": trilha, "fase": fase, "banca": banca, "results": results[:limit], "warnings": []}

@app.get("/v1/materias/{slug}")
def get_materia_by_slug(slug: str, authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    for item in MATERIAS:
        if item["slug"] == slug:
            return item
    raise HTTPException(status_code=404, detail="Materia not found")

@app.get("/v1/prioridades")
def get_prioridades(
    trilha: str = Query(...),
    fase: str = Query(...),
    banca: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=30),
    authorization: Optional[str] = Header(default=None)
):
    require_bearer(authorization)
    results = []
    for m in MATERIAS:
        if trilha in m.get("trilhas", []) and fase in m.get("fase", []):
            item = dict(m)
            item["priority_score"] = compute_priority(item, fase, banca, trilha)
            results.append(item)
    results.sort(key=lambda x: (-x["priority_score"], x["name"]))
    return {"trilha": trilha, "fase": fase, "banca": banca, "results": results[:limit], "warnings": []}

@app.get("/v1/normativos")
def get_normativos(q: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=20), authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"query": q, "results": search_collection(q, NORMATIVOS, limit), "warnings": []}

@app.get("/v1/resolucoes")
def get_resolucoes(q: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=20), authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"query": q, "results": search_collection(q, RESOLUCOES, limit), "warnings": []}

@app.get("/v1/leis")
def get_leis(q: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=20), authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"query": q, "results": search_collection(q, LEIS, limit), "warnings": []}

@app.get("/v1/editais")
def get_editais(
    q: str = Query(..., min_length=2),
    tribunal: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=30),
    authorization: Optional[str] = Header(default=None)
):
    require_bearer(authorization)
    results = search_collection(q, TRF_COMPETITIONS, 50)
    if tribunal:
        results = [r for r in results if r.get("tribunal") == tribunal]
    if status:
        results = [r for r in results if r.get("status") == status]
    return {"query": q, "tribunal": tribunal, "status": status, "results": results[:limit], "warnings": []}

@app.get("/v1/cronogramas")
def get_cronogramas(
    q: str = Query(..., min_length=2),
    tribunal: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=30),
    authorization: Optional[str] = Header(default=None)
):
    require_bearer(authorization)
    results = search_collection(q, CRONOGRAMAS, 50)
    if tribunal:
        results = [r for r in results if r.get("tribunal") == tribunal]
    return {"query": q, "tribunal": tribunal, "results": results[:limit], "warnings": []}

@app.get("/v1/jurisprudencia")
def get_jurisprudencia(q: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=20), authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"query": q, "results": search_collection(q, JURISPRUDENCIA, limit), "warnings": []}

@app.get("/v1/sumulas")
def get_sumulas(q: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=20), authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"query": q, "results": search_collection(q, SUMULAS, limit), "warnings": []}

@app.get("/v1/doutrina")
def get_doutrina(q: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=20), authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"query": q, "results": search_collection(q, DOUTRINA, limit), "warnings": []}

@app.get("/v1/analyze")
def analyze(
    q: str = Query(..., min_length=2),
    trilha: Optional[str] = Query(None),
    fase: Optional[str] = Query(None),
    banca: Optional[str] = Query(None),
    tribunal: Optional[str] = Query(None),
    authorization: Optional[str] = Header(default=None)
):
    require_bearer(authorization)

    materias = search_collection(q, MATERIAS, 20)
    if trilha:
        materias = [m for m in materias if trilha in m.get("trilhas", [])]
    if fase:
        materias = [m for m in materias if fase in m.get("fase", [])]
    for m in materias:
        m["priority_score"] = compute_priority(m, fase, banca, trilha)
    materias.sort(key=lambda x: (-x["priority_score"], x["name"]))

    editais = search_collection(q, TRF_COMPETITIONS, 20)
    if tribunal:
        editais = [e for e in editais if e.get("tribunal") == tribunal]

    return {
        "query": q,
        "trilha": trilha,
        "fase": fase,
        "banca": banca,
        "tribunal": tribunal,
        "analysis": {
            "diagnostico": f"A consulta '{q}' foi analisada com foco em disciplina, fase, banca e tribunal.",
            "materias_prioritarias": materias[:7],
            "normativos_prioritarios": search_collection(q, NORMATIVOS + RESOLUCOES, 4),
            "editais_prioritarios": editais[:4],
            "jurisprudencia_prioritaria": search_collection(q, JURISPRUDENCIA, 3),
            "sumulas_prioritarias": search_collection(q, SUMULAS, 3),
            "riscos_estrategicos": [
                "Risco de estudar com peso igual para matérias com impacto desigual.",
                "Risco de não separar ENAM e concurso do TRF-alvo.",
                "Risco de ignorar diferenças de banca e fase."
            ],
            "plano_de_acao": [
                "Definir trilha principal.",
                "Definir fase-alvo.",
                "Priorizar matérias por peso estratégico.",
                "Cruzar edital do tribunal, jurisprudência e treino ativo."
            ]
        },
        "warnings": []
    }

@app.post("/v1/plano-estudos")
def plano_estudos(payload: StudyPlanRequest, authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)

    fase = payload.fase
    trilha = payload.trilha or "magistratura_federal"
    banca = payload.banca

    priorities = []
    for m in MATERIAS:
        if trilha in m["trilhas"] and fase in m["fase"]:
            item = dict(m)
            item["priority_score"] = compute_priority(item, fase, banca, trilha)
            priorities.append(item)
    priorities.sort(key=lambda x: (-x["priority_score"], x["name"]))
    top = [p["name"] for p in priorities[:6]]

    weekly = [
        {"semana": 1, "foco": "núcleo essencial", "tarefas": [f"Estudar {top[0]}", f"Estudar {top[1]}", "Questões e revisão"]},
        {"semana": 2, "foco": "núcleo essencial + escrita", "tarefas": [f"Estudar {top[2]}", f"Estudar {top[3]}", "Treino escrito"]},
        {"semana": 3, "foco": "matérias estratégicas", "tarefas": [f"Estudar {top[4]}", f"Estudar {top[5]}", "Jurisprudência e súmulas"]},
        {"semana": 4, "foco": "consolidação", "tarefas": ["Simulado parcial", "Auditoria de erros", "Replanejamento"]}
    ]

    return {
        "objetivo": payload.objetivo,
        "fase": payload.fase,
        "horas_semanais": payload.horas_semanais,
        "nivel": payload.nivel,
        "trilha": trilha,
        "banca": banca,
        "diagnostico": "Plano gerado com priorização por trilha, fase e banca.",
        "prioridades": top,
        "execucao_semanal": weekly,
        "data_provavel_prova": payload.data_provavel_prova,
        "warnings": []
    }
