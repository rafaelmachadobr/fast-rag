from typing import Any, Dict

import httpx
from fastapi import HTTPException
from sentence_transformers import SentenceTransformer, util

from src.core.settings import settings


class QueryUseCase:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.documents = [
            {
                "id": 1,
                "text": "O impacto das redes sociais na sociedade moderna: As redes sociais transformaram a maneira como nos comunicamos, trabalhamos e interagimos uns com os outros. Elas permitem que as pessoas se conectem instantaneamente, mas também levantam questões sobre privacidade, saúde mental e disseminação de informações falsas. Com a evolução dessas plataformas, é fundamental que os usuários aprendam a navegar por elas de forma responsável.",
            },
            {
                "id": 2,
                "text": "A importância da sustentabilidade: Em um mundo cada vez mais afetado pelas mudanças climáticas, a sustentabilidade se torna um tema crucial. Práticas sustentáveis não apenas ajudam a proteger o meio ambiente, mas também promovem a justiça social e o desenvolvimento econômico. A conscientização sobre o consumo responsável e a preservação dos recursos naturais é essencial para garantir um futuro viável para as próximas gerações.",
            },
            {
                "id": 3,
                "text": "A evolução da tecnologia e seu impacto no trabalho: A tecnologia tem mudado radicalmente o mercado de trabalho. Com a automação e a inteligência artificial, muitas profissões estão se transformando ou desaparecendo. Por outro lado, novas oportunidades estão surgindo em áreas como análise de dados, desenvolvimento de software e cibersegurança. Adaptar-se a essas mudanças é vital para os trabalhadores de hoje.",
            },
            {
                "id": 4,
                "text": "Saúde mental na era digital: A saúde mental é um tema que ganha cada vez mais atenção na sociedade contemporânea. A pressão das redes sociais, o isolamento e a sobrecarga de informações podem afetar o bem-estar psicológico. É importante promover um diálogo aberto sobre saúde mental, oferecendo suporte e recursos para aqueles que enfrentam desafios. A terapia, a meditação e a desconexão das telas são algumas estratégias que podem ajudar.",
            },
        ]
        self.doc_embeddings = {
            doc["id"]: self.model.encode(doc["text"], convert_to_tensor=True)
            for doc in self.documents
        }

    async def find_best_document(self, query: str) -> Dict[str, Any]:
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        best_doc = {}
        best_score = float("-inf")

        for doc in self.documents:
            score = util.cos_sim(query_embedding, self.doc_embeddings[doc["id"]])
            if score > best_score:
                best_score = score
                best_doc = doc

        return best_doc

    async def get_ai_response(self, query: str, context: str) -> str:
        prompt = f"""
        Você é um atendente de uma empresa.
        Seu trabalho é conversar com os clientes, consultando a base de
        conhecimento da empresa, e dar
        uma resposta simples e precisa para ele, baseando na 
        base de dados da empresa fornecida como contexto.

        Contexto: {context}

        Pergunta: {query}
        """

        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": prompt},
            ],
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
            )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        res = response.json()
        return res["choices"][0]["message"]["content"]
