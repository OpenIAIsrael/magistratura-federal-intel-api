from fastapi import FastAPI, Query, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import os
import re

app = FastAPI(
    title="Magistratura Federal Intel API",
    version="3.0.0",
    description="API para concursos da magistratura federal com matérias, normativos, resoluções, leis, editais, cronogramas, jurisprudência, súmulas, doutrina e estratégia."
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
    {
        "id": "enam",
        "name": "ENAM",
        "description": "Trilha voltada ao Exame Nacional da Magistratura, etapa de habilitação."
    },
    {
        "id": "magistratura_federal",
        "name": "Magistratura Federal",
        "description": "Trilha voltada aos concursos de Juiz Federal Substituto."
    },
    {
        "id": "formacao_humanistica",
        "name": "Formação Humanística",
        "description": "Trilha de Noções Gerais de Direito e Formação Humanística."
    }
]

SOURCES = [
    {"id": "enfam", "name": "ENFAM", "official": True, "type": "institucional"},
    {"id": "fgv", "name": "FGV Conhecimento", "official": True, "type": "banca"},
    {"id": "cnj", "name": "CNJ", "official": True, "type": "normativo"},
    {"id": "stf", "name": "STF", "official": True, "type": "jurisprudencia"},
    {"id": "stj", "name": "STJ", "official": True, "type": "jurisprudencia"},
    {"id": "trf3", "name": "TRF3", "official": True, "type": "tribunal"},
    {"id": "planalto", "name": "Planalto", "official": True, "type": "legislacao"},
    {"id": "interno", "name": "Base interna", "official": False, "type": "doutrina"}
]

MATERIAS = [
    {
        "slug": "direito-constitucional",
        "name": "Direito Constitucional",
        "trilhas": ["enam", "magistratura_federal"],
        "grupo": "nucleo_essencial",
        "fase": ["objetiva", "discursiva", "oral"],
        "summary": "Disciplina central da magistratura e do ENAM.",
        "tags": ["constitucional", "cf88", "controle", "direitos fundamentais"]
    },
    {
        "slug": "direito-administrativo",
        "name": "Direito Administrativo",
        "trilhas": ["enam", "magistratura_federal"],
        "grupo": "nucleo_essencial",
        "fase": ["objetiva", "discursiva", "oral"],
        "summary": "Disciplina central da magistratura e do ENAM.",
        "tags": ["administrativo", "atos", "poderes", "servidores", "licitacoes"]
    },
    {
        "slug": "direito-civil",
        "name": "Direito Civil",
        "trilhas": ["enam", "magistratura_federal"],
        "grupo": "nucleo_essencial",
        "fase": ["objetiva", "discursiva", "sentenca_civel", "oral"],
        "summary": "Disciplina base para fase objetiva, discursiva e sentença cível.",
        "tags": ["civil", "obrigacoes", "contratos", "responsabilidade", "familia", "sucessoes"]
    },
    {
        "slug": "direito-processual-civil",
        "name": "Direito Processual Civil",
        "trilhas": ["enam", "magistratura_federal"],
        "grupo": "nucleo_essencial",
        "fase": ["objetiva", "discursiva", "sentenca_civel", "oral"],
        "summary": "Disciplina central na magistratura, especialmente para sentença cível.",
        "tags": ["processo civil", "cpc", "tutelas", "recursos", "execucao"]
    },
    {
        "slug": "direito-penal",
        "name": "Direito Penal",
        "trilhas": ["enam", "magistratura_federal"],
        "grupo": "nucleo_essencial",
        "fase": ["objetiva", "discursiva", "sentenca_penal", "oral"],
        "summary": "Disciplina central na magistratura e no ENAM.",
        "tags": ["penal", "tipicidade", "culpabilidade", "penas", "crimes"]
    },
    {
        "slug": "direito-processual-penal",
        "name": "Direito Processual Penal",
        "trilhas": ["magistratura_federal"],
        "grupo": "nucleo_essencial",
        "fase": ["objetiva", "discursiva", "sentenca_penal", "oral"],
        "summary": "Disciplina central para a fase penal e sentença penal.",
        "tags": ["processo penal", "cpp", "provas", "prisao", "acao penal"]
    },
    {
        "slug": "direito-empresarial",
        "name": "Direito Empresarial",
        "trilhas": ["enam", "magistratura_federal"],
        "grupo": "complementar_relevante",
        "fase": ["objetiva", "discursiva", "oral"],
        "summary": "Disciplina recorrente em magistratura e ENAM.",
        "tags": ["empresarial", "societario", "titulos", "falencia", "recuperacao"]
    },
    {
        "slug": "direito-tributario",
        "name": "Direito Tributário",
        "trilhas": ["magistratura_federal"],
        "grupo": "federal_estrategico",
        "fase": ["objetiva", "discursiva", "oral"],
        "summary": "Disciplina de alta relevância para magistratura federal.",
        "tags": ["tributario", "ctn", "competencia", "tributos", "reforma tributaria"]
    },
    {
        "slug": "direito-ambiental",
        "name": "Direito Ambiental",
        "trilhas": ["magistratura_federal"],
        "grupo": "federal_estrategico",
        "fase": ["objetiva", "discursiva", "oral"],
        "summary": "Disciplina relevante para concursos da magistratura.",
        "tags": ["ambiental", "licenciamento", "responsabilidade ambiental"]
    },
    {
        "slug": "direito-eleitoral",
        "name": "Direito Eleitoral",
        "trilhas": ["magistratura_federal"],
        "grupo": "complementar_relevante",
        "fase": ["objetiva", "oral"],
        "summary": "Disciplina cobrada em listas mínimas da Resolução CNJ 75.",
        "tags": ["eleitoral", "registro", "inelegibilidade", "partidos"]
    },
    {
        "slug": "direito-do-consumidor",
        "name": "Direito do Consumidor",
        "trilhas": ["magistratura_federal"],
        "grupo": "complementar_relevante",
        "fase": ["objetiva", "discursiva"],
        "summary": "Disciplina cobrada como matéria autônoma.",
        "tags": ["consumidor", "cdc", "fornecedor", "responsabilidade"]
    },
    {
        "slug": "direito-da-crianca-e-do-adolescente",
        "name": "Direito da Criança e do Adolescente",
        "trilhas": ["magistratura_federal"],
        "grupo": "complementar_relevante",
        "fase": ["objetiva", "discursiva", "oral"],
        "summary": "Disciplina autônoma na matriz de magistratura.",
        "tags": ["eca", "crianca", "adolescente", "protecao integral"]
    },
    {
        "slug": "direitos-humanos",
        "name": "Direitos Humanos",
        "trilhas": ["enam", "magistratura_federal"],
        "grupo": "estruturante",
        "fase": ["objetiva", "discursiva", "oral"],
        "summary": "Disciplina incorporada expressamente na matriz do concurso.",
        "tags": ["direitos humanos", "controle de convencionalidade", "sistema interamericano"]
    },
    {
        "slug": "direito-previdenciario",
        "name": "Direito Previdenciário",
        "trilhas": ["magistratura_federal"],
        "grupo": "federal_estrategico",
        "fase": ["objetiva", "discursiva", "oral"],
        "summary": "Disciplina típica e estratégica da magistratura federal.",
        "tags": ["previdenciario", "beneficios", "rgps", "seguridade"]
    },
    {
        "slug": "direito-internacional-publico-e-privado",
        "name": "Direito Internacional Público e Privado / Comunitário",
        "trilhas": ["magistratura_federal"],
        "grupo": "federal_estrategico",
        "fase": ["objetiva", "oral"],
        "summary": "Disciplina recorrente nas listas da magistratura federal.",
        "tags": ["internacional", "privado", "publico", "comunitario", "cooperacao"]
    },
    {
        "slug": "direito-financeiro-e-economico",
        "name": "Direito Financeiro e Econômico",
        "trilhas": ["magistratura_federal"],
        "grupo": "federal_estrategico",
        "fase": ["objetiva", "oral"],
        "summary": "Disciplina estratégica no recorte federal.",
        "tags": ["financeiro", "economico", "orcamento", "responsabilidade fiscal"]
    },
    {
        "slug": "direito-do-trabalho",
        "name": "Direito do Trabalho",
        "trilhas": ["magistratura_federal"],
        "grupo": "complementar_relevante",
        "fase": ["objetiva", "oral"],
        "summary": "Disciplina relevante na formação geral do candidato.",
        "tags": ["trabalho", "clt", "contrato de trabalho"]
    },
    {
        "slug": "direito-processual-do-trabalho",
        "name": "Direito Processual do Trabalho",
        "trilhas": ["magistratura_federal"],
        "grupo": "complementar_relevante",
        "fase": ["objetiva", "oral"],
        "summary": "Disciplina relevante em listas da magistratura.",
        "tags": ["processo do trabalho", "rito", "recursos"]
    },
    {
        "slug": "formacao-humanistica-sociologia-do-direito",
        "name": "Formação Humanística — Sociologia do Direito",
        "trilhas": ["formacao_humanistica", "magistratura_federal", "enam"],
        "grupo": "formacao_humanistica",
        "fase": ["objetiva", "oral"],
        "summary": "Subeixo de Noções Gerais de Direito e Formação Humanística.",
        "tags": ["sociologia", "administracao judiciaria", "controle social"]
    },
    {
        "slug": "formacao-humanistica-psicologia-judiciaria",
        "name": "Formação Humanística — Psicologia Judiciária",
        "trilhas": ["formacao_humanistica", "magistratura_federal", "enam"],
        "grupo": "formacao_humanistica",
        "fase": ["objetiva", "oral"],
        "summary": "Subeixo de Noções Gerais de Direito e Formação Humanística.",
        "tags": ["psicologia judiciaria", "negociacao", "mediacao", "prova testemunhal"]
    },
    {
        "slug": "formacao-humanistica-etica-e-estatuto-da-magistratura",
        "name": "Formação Humanística — Ética e Estatuto Jurídico da Magistratura",
        "trilhas": ["formacao_humanistica", "magistratura_federal", "enam"],
        "grupo": "formacao_humanistica",
        "fase": ["objetiva", "oral"],
        "summary": "Subeixo de formação humanística com forte aderência à carreira.",
        "tags": ["etica", "estatuto da magistratura", "cnj", "responsabilidade funcional"]
    },
    {
        "slug": "formacao-humanistica-filosofia-do-direito",
        "name": "Formação Humanística — Filosofia do Direito",
        "trilhas": ["formacao_humanistica", "magistratura_federal", "enam"],
        "grupo": "formacao_humanistica",
        "fase": ["objetiva", "oral"],
        "summary": "Subeixo de formação humanística.",
        "tags": ["filosofia do direito", "justica", "moral", "interpretacao"]
    },
    {
        "slug": "formacao-humanistica-teoria-geral-do-direito-e-da-politica",
        "name": "Formação Humanística — Teoria Geral do Direito e da Política",
        "trilhas": ["formacao_humanistica", "magistratura_federal", "enam"],
        "grupo": "formacao_humanistica",
        "fase": ["objetiva", "oral"],
        "summary": "Subeixo de formação humanística.",
        "tags": ["teoria geral", "politica", "fontes do direito", "ideologias", "agenda 2030"]
    },
    {
        "slug": "formacao-humanistica-direito-digital",
        "name": "Formação Humanística — Direito Digital",
        "trilhas": ["formacao_humanistica", "magistratura_federal", "enam"],
        "grupo": "formacao_humanistica",
        "fase": ["objetiva", "oral"],
        "summary": "Subeixo incluído por alteração normativa posterior.",
        "tags": ["direito digital", "ia", "lgpd", "provas digitais", "ciberseguranca"]
    },
    {
        "slug": "formacao-humanistica-pragmatismo-aed-e-economia-comportamental",
        "name": "Formação Humanística — Pragmatismo, AED e Economia Comportamental",
        "trilhas": ["formacao_humanistica", "magistratura_federal", "enam"],
        "grupo": "formacao_humanistica",
        "fase": ["objetiva", "oral"],
        "summary": "Subeixo de formação humanística.",
        "tags": ["pragmatismo", "aed", "economia comportamental", "compliance", "whistleblower"]
    },
    {
        "slug": "formacao-humanistica-direito-da-antidiscriminacao",
        "name": "Formação Humanística — Direito da Antidiscriminação",
        "trilhas": ["formacao_humanistica", "magistratura_federal", "enam"],
        "grupo": "formacao_humanistica",
        "fase": ["objetiva", "oral"],
        "summary": "Subeixo de formação humanística incluído por alteração normativa.",
        "tags": ["antidiscriminacao", "racismo", "sexismo", "acoes afirmativas", "povos indigenas"]
    }
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
        "summary": "Aperfeiçoa a Resolução 75 e estrutura o ENAM.",
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
        "area": "direitos_humanos",
        "source": "cnj",
        "summary": "Altera a Resolução 75 e reforça o eixo de Direitos Humanos.",
        "url": "https://atos.cnj.jus.br/atos/detalhar/5030",
        "tags": ["resolucao", "cnj", "496", "direitos humanos"]
    },
    {
        "title": "Resolução Enfam nº 13/2025",
        "category": "resolucao",
        "area": "enam",
        "source": "enfam",
        "summary": "Estabelece normas para a realização do ENAM pela Enfam.",
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
    },
    {
        "title": "Código Civil",
        "category": "lei",
        "area": "magistratura_federal",
        "source": "planalto",
        "summary": "Lei-base para Direito Civil.",
        "url": "https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm",
        "tags": ["codigo civil", "civil"]
    },
    {
        "title": "Código de Processo Civil",
        "category": "lei",
        "area": "magistratura_federal",
        "source": "planalto",
        "summary": "Lei-base para Processo Civil.",
        "url": "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm",
        "tags": ["cpc", "processual civil"]
    },
    {
        "title": "Código Penal",
        "category": "lei",
        "area": "magistratura_federal",
        "source": "planalto",
        "summary": "Lei-base para Direito Penal.",
        "url": "https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm",
        "tags": ["codigo penal", "penal"]
    },
    {
        "title": "Código de Processo Penal",
        "category": "lei",
        "area": "magistratura_federal",
        "source": "planalto",
        "summary": "Lei-base para Processo Penal.",
        "url": "https://www.planalto.gov.br/ccivil_03/decreto-lei/del3689.htm",
        "tags": ["cpp", "processual penal"]
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
        "url": "https://conhecimento.fgv.br/exames/enam/5exame",
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
        normalize(" ".join(item.get("tags", []))),
        normalize(" ".join(item.get("trilhas", []))) if isinstance(item.get("trilhas"), list) else ""
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
    results.sort(key=lambda x: (-x["_score"], x.get("title", x.get("name", ""))))
    return results[:limit]

@app.get("/health")
def health(authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    return {"status": "healthy", "api": "Magistratura Federal Intel API", "version": "3.0.0", "timestamp": now_iso()}

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

@app.get("/v1/materias")
def get_materias(
    q: str = Query(..., min_length=2),
    trilha: Optional[str] = Query(None),
    fase: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    authorization: Optional[str] = Header(default=None)
):
    require_bearer(authorization)
    results = search_collection(q, MATERIAS, None, 50)
    if trilha:
        results = [r for r in results if trilha in r.get("trilhas", [])]
    if fase:
        results = [r for r in results if fase in r.get("fase", [])]
    return {"query": q, "trilha": trilha, "fase": fase, "results": results[:limit], "warnings": []}

@app.get("/v1/materias/{slug}")
def get_materia_by_slug(slug: str, authorization: Optional[str] = Header(default=None)):
    require_bearer(authorization)
    for item in MATERIAS:
        if item["slug"] == slug:
            return item
    raise HTTPException(status_code=404, detail="Materia not found")

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
    results = search_collection(q, EDITAIS, area, 50)
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
def analyze(
    q: str = Query(..., min_length=2),
    trilha: Optional[str] = Query(None),
    fase: Optional[str] = Query(None),
    authorization: Optional[str] = Header(default=None)
):
    require_bearer(authorization)

    materias = search_collection(q, MATERIAS, None, 8)
    if trilha:
        materias = [m for m in materias if trilha in m.get("trilhas", [])]
    if fase:
        materias = [m for m in materias if fase in m.get("fase", [])]

    return {
        "query": q,
        "trilha": trilha,
        "fase": fase,
        "analysis": {
            "diagnostico": f"A consulta '{q}' foi analisada com foco em disciplina, trilha e fase do concurso.",
            "materias_prioritarias": materias[:5],
            "normativos_prioritarios": search_collection(q, NORMATIVOS + RESOLUCOES, None, 4),
            "editais_prioritarios": search_collection(q, EDITAIS, None, 3),
            "jurisprudencia_prioritaria": search_collection(q, JURISPRUDENCIA, None, 3),
            "sumulas_prioritarias": search_collection(q, SUMULAS, None, 3),
            "riscos_estrategicos": [
                "Risco de estudar disciplina errada para a fase errada.",
                "Risco de tratar ENAM e concurso de juiz federal como se fossem iguais.",
                "Risco de negligenciar formação humanística e direitos humanos."
            ],
            "plano_de_acao": [
                "Definir a trilha principal: ENAM ou magistratura federal.",
                "Separar núcleo essencial, matérias federais estratégicas e formação humanística.",
                "Cruzar lei seca, jurisprudência, súmulas e materiais da disciplina-alvo."
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
        "Revisão periódica por disciplina"
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
        "diagnostico": "Plano inicial gerado com foco em aderência à fase, constância e cobertura integral das matérias-base.",
        "prioridades": prioridades,
        "execucao_semanal": [
            {
                "semana": 1,
                "foco": "Núcleo essencial",
                "tarefas": [
                    "Questões de Constitucional, Administrativo e Processo Civil",
                    "Leitura de lei seca",
                    "Revisão de erros"
                ]
            },
            {
                "semana": 2,
                "foco": "Penal + formação humanística",
                "tarefas": [
                    "Questões de Penal e Processo Penal",
                    "Leitura de súmulas relevantes",
                    "Bloco de formação humanística"
                ]
            },
            {
                "semana": 3,
                "foco": "Matérias federais estratégicas",
                "tarefas": [
                    "Tributário, Previdenciário e Internacional",
                    "Jurisprudência",
                    "Mapa de revisão"
                ]
            },
            {
                "semana": 4,
                "foco": "Treino ativo",
                "tarefas": [
                    "Simulado parcial",
                    "Treino escrito conforme fase",
                    "Auditoria da semana"
                ]
            }
        ],
        "data_provavel_prova": payload.data_provavel_prova,
        "warnings": []
    }
