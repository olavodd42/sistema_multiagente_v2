"""
Testes para a classe ArticleCrew.
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.crew.article_crew import ArticleCrew
from app.models.article import Article, ArticleSection, ArticleMetadata


@pytest.fixture
def mock_researcher_result():
    """Fixture que simula o resultado do agente pesquisador."""
    return json.dumps({
        "topic": "Inteligência Artificial",
        "summary": "A Inteligência Artificial (IA) é um campo da ciência da computação que se concentra no desenvolvimento de sistemas capazes de realizar tarefas que normalmente exigiriam inteligência humana.",
        "main_sections": [
            {
                "title": "História da IA",
                "content": "A história da IA começou na década de 1950, quando cientistas e matemáticos começaram a explorar a possibilidade de criar máquinas que pudessem 'pensar'. O termo 'Inteligência Artificial' foi cunhado por John McCarthy em 1956 durante a conferência de Dartmouth, considerada o evento de nascimento da IA como campo de estudo."
            },
            {
                "title": "Tipos de IA",
                "content": "Existem diferentes categorias de IA, incluindo IA Fraca (ou Estreita), que é projetada para realizar uma tarefa específica, e IA Forte (ou Geral), que teoricamente poderia realizar qualquer tarefa intelectual que um ser humano pode fazer. Atualmente, todos os sistemas de IA existentes são considerados IA Fraca."
            }
        ],
        "keywords": ["Inteligência Artificial", "IA", "Machine Learning", "Redes Neurais", "Algoritmos"],
        "sources": ["Inteligência artificial", "História da inteligência artificial"]
    })


@pytest.fixture
def mock_writer_result():
    """Fixture que simula o resultado do agente redator."""
    return json.dumps({
        "title": "Inteligência Artificial: Conceitos, História e Aplicações",
        "summary": "A Inteligência Artificial (IA) revolucionou a maneira como interagimos com a tecnologia. Este artigo explora os fundamentos da IA, sua evolução histórica e os diferentes tipos existentes atualmente.",
        "sections": [
            {
                "title": "O que é Inteligência Artificial?",
                "content": "A Inteligência Artificial (IA) é um ramo da ciência da computação dedicado ao desenvolvimento de sistemas capazes de realizar tarefas que normalmente exigiriam inteligência humana. Estas tarefas incluem reconhecimento de voz, tomada de decisões, tradução de idiomas e reconhecimento visual. A IA busca não apenas imitar, mas potencialmente superar capacidades humanas em tarefas específicas através de algoritmos e modelos computacionais avançados."
            },
            {
                "title": "História e Evolução",
                "content": "A história da IA começou formalmente na década de 1950, quando cientistas e matemáticos começaram a explorar a possibilidade de criar máquinas pensantes. O termo 'Inteligência Artificial' foi cunhado por John McCarthy em 1956 durante a histórica conferência de Dartmouth, considerada o marco inicial da IA como campo de estudo científico. Desde então, a área passou por diversos ciclos de otimismo e decepção, conhecidos como 'verões e invernos da IA'. O recente avanço em poder computacional, disponibilidade de dados e novos algoritmos levou ao atual renascimento da área."
            },
            {
                "title": "Tipos de Inteligência Artificial",
                "content": "Os sistemas de IA são classificados em diferentes categorias. A IA Fraca (ou Estreita) é projetada para executar uma tarefa específica, como reconhecimento facial ou recomendações de produtos. Todos os sistemas atuais de IA, incluindo assistentes virtuais como Siri e Alexa, são exemplos de IA Fraca. Por outro lado, a IA Forte (ou Geral) representaria sistemas capazes de compreender, aprender e aplicar conhecimento em diferentes domínios, semelhante à inteligência humana. Embora ainda seja um conceito teórico, continua sendo um objetivo de longo prazo para pesquisadores da área."
            }
        ],
        "metadata": {
            "keywords": ["Inteligência Artificial", "IA", "Machine Learning", "Redes Neurais", "Algoritmos", "História da IA"],
            "sources": ["Inteligência artificial", "História da inteligência artificial"],
            "generated_at": "2025-04-18T10:00:00"
        }
    })


@pytest.fixture
def mock_editor_result():
    """Fixture que simula o resultado do agente editor."""
    return json.dumps({
        "title": "Inteligência Artificial: Revolução Tecnológica do Século XXI",
        "summary": "A Inteligência Artificial (IA) representa uma das maiores revoluções tecnológicas da história moderna, transformando significativamente diversos setores da sociedade. Este artigo explora os conceitos fundamentais da IA, sua fascinante trajetória histórica e as diferentes categorias que definem o campo atualmente.",
        "sections": [
            {
                "title": "Compreendendo a Inteligência Artificial",
                "content": "A Inteligência Artificial (IA) constitui um ramo avançado da ciência da computação dedicado ao desenvolvimento de sistemas capazes de realizar tarefas que tradicionalmente demandariam inteligência humana. Estas atividades abrangem desde reconhecimento de voz e visual até tomada de decisões complexas e tradução de idiomas em tempo real. Mais do que simplesmente imitar capacidades humanas, a IA busca potencializar e até mesmo superar estas habilidades em domínios específicos através de algoritmos sofisticados e modelos computacionais de última geração que processam vastas quantidades de dados para aprender e evoluir continuamente."
            },
            {
                "title": "Trajetória Histórica da IA",
                "content": "A jornada da Inteligência Artificial teve seu início formal na década de 1950, quando visionários da ciência começaram a explorar sistematicamente a possibilidade de desenvolver máquinas com capacidade de pensamento autônomo. O próprio termo 'Inteligência Artificial' foi estabelecido por John McCarthy em 1956 durante a pioneira conferência de Dartmouth, evento agora reconhecido universalmente como o nascimento oficial da IA enquanto disciplina científica. Ao longo das décadas seguintes, o campo experimentou diversos ciclos de extraordinário entusiasmo seguidos por períodos de estagnação e desapontamento – fenômenos conhecidos respectivamente como 'verões e invernos da IA'. A revolução contemporânea da área, iniciada na segunda década do século XXI, deve-se principalmente à convergência de três fatores cruciais: poder computacional sem precedentes, disponibilidade massiva de dados e desenvolvimento de algoritmos inovadores, especialmente no campo da aprendizagem profunda."
            },
            {
                "title": "Categorias e Aplicações Modernas",
                "content": "Os sistemas de Inteligência Artificial contemporâneos são categorizados em taxonomias específicas que refletem suas capacidades e limitações. A IA Estreita (também chamada de Fraca) é projetada para executar funções específicas e delimitadas com extrema eficiência, como os sistemas de reconhecimento facial em smartphones, assistentes virtuais como Siri e Alexa, ou algoritmos de recomendação em plataformas de streaming. Todos os sistemas operacionais atualmente representam esta categoria. Em contraste, a IA Geral (ou Forte) permanece como um horizonte teórico e representa sistemas hipotéticos capazes de compreender, aprender e aplicar conhecimento de forma transversal entre diferentes domínios, aproximando-se da versatilidade cognitiva humana. Embora ainda não realizada, a IA Geral continua sendo o santo graal da pesquisa no campo, impulsionando inovações que gradualmente expandem as fronteiras do que consideramos possível na interface entre inteligência natural e artificial."
            }
        ],
        "metadata": {
            "keywords": ["Inteligência Artificial", "IA", "Machine Learning", "Redes Neurais", "Algoritmos", "História da IA", "IA Fraca", "IA Forte"],
            "sources": ["Inteligência artificial", "História da inteligência artificial", "Aprendizado de máquina"],
            "generated_at": "2025-04-18T11:30:00"
        }
    })


class TestArticleCrew:
    """Testes para a classe ArticleCrew."""
    
    @patch('app.crew.article_crew.Crew')
    def test_article_crew_initialization(self, mock_crew):
        """Testa a inicialização da ArticleCrew."""
        crew = ArticleCrew(llm="groq", language="pt", verbose=True)
        
        assert crew.llm == "groq"
        assert crew.language == "pt"
        assert crew.verbose is True
        assert crew.process == "sequential"
    
    @patch('app.crew.article_crew.Task')
    @patch('app.crew.article_crew.Crew')
    @patch('app.crew.article_crew.ResearcherAgent')
    @patch('app.crew.article_crew.WriterAgent')
    @patch('app.crew.article_crew.EditorAgent')
    def test_run_article_generation(self, mock_editor_agent, mock_writer_agent, mock_researcher_agent, mock_crew, mock_task):
        """Testa o método run para geração de artigos."""
        # Configurar mock para Task para não validar
        mock_task.return_value = MagicMock()
        
        # Setup dos mocks de agentes
        mock_researcher = MagicMock(spec=dict)
        mock_writer = MagicMock(spec=dict)
        mock_editor = MagicMock(spec=dict)

        mock_researcher_agent.return_value.create.return_value = mock_researcher
        mock_writer_agent.return_value.create.return_value = mock_writer
        mock_editor_agent.return_value.create.return_value = mock_editor

        mock_crew_instance = MagicMock()
        mock_crew.return_value = mock_crew_instance
        mock_crew_instance.kickoff.return_value = (
            '{"title": "Test Article", "summary": "This is a test summary with enough characters to pass validation. This summary should be long enough for the test to pass without issues.", '
            '"sections": [{"title": "Section 1", "content": "This is section 1 content with at least fifty characters for validation. We need to make sure it passes the validation."},'
            '{"title": "Section 2", "content": "This is section 2 content with at least fifty characters for validation. We need to make sure it passes the validation."}], '
            '"metadata": {"keywords": ["test"], "sources": ["test source"], "generated_at": "2025-04-18T12:00:00"}}'
        )

        # Criar e executar a crew
        crew = ArticleCrew(llm="groq", language="pt")
        result = crew.run("Teste", 300)

        # Verificações
        assert mock_crew.called
        assert mock_crew_instance.kickoff.called
        assert result["status"] == "success"
        assert "article" in result
        assert "processing_time" in result

    @patch('app.crew.article_crew.Crew')
    def test_parse_json_result(self, mock_crew):
        """Testa o método _parse_json_result."""
        crew = ArticleCrew()
        
        # Caso 1: JSON direto
        json_result = '{"title": "Test", "content": "Test content"}'
        parsed = crew._parse_json_result(json_result)
        assert parsed == {"title": "Test", "content": "Test content"}
        
        # Caso 2: JSON delimitado por ```json
        markdown_json = 'Resultado:\n```json\n{"title": "Test", "content": "Markdown content"}\n```'
        parsed = crew._parse_json_result(markdown_json)
        assert parsed == {"title": "Test", "content": "Markdown content"}
    
    @patch('app.crew.article_crew.Crew')
    def test_convert_to_pydantic_model(self, mock_crew):
        """Testa o método _convert_to_pydantic_model."""
        crew = ArticleCrew()
        
        article_data = {
            "title": "Título de Teste",
            "summary": "Este é um resumo de teste com pelo menos cem caracteres para passar na validação do modelo Pydantic. Precisamos garantir que tenha comprimento suficiente.",
            "sections": [
                {
                    "title": "Seção 1",
                    "content": "Conteúdo da seção 1 com pelo menos cinquenta caracteres para validação."
                },
                {
                    "title": "Seção 2",
                    "content": "Conteúdo da seção 2 também com pelo menos cinquenta caracteres para validação."
                }
            ],
            "metadata": {
                "keywords": ["teste", "validação"],
                "sources": ["Fonte de teste"],
                "generated_at": "2025-04-18T12:00:00"
            }
        }
        
        article = crew._convert_to_pydantic_model(article_data)
        
        assert isinstance(article, Article)
        assert article.title == "Título de Teste"
        assert len(article.sections) == 2
        assert isinstance(article.metadata, ArticleMetadata)
        assert "teste" in article.metadata.keywords


@pytest.mark.integration
class TestArticleCrewIntegration:
    """Testes de integração para ArticleCrew."""
    
    @patch('app.crew.article_crew.Task')
    @patch('app.crew.article_crew.Crew')
    def test_complete_article_generation_flow(self, mock_crew, mock_task, mock_researcher_result, mock_writer_result, mock_editor_result):
        """Testa o fluxo completo de geração de artigos simulando as respostas dos agentes."""
        # Configurar mock para Task para não validar
        mock_task.return_value = MagicMock()
        
        # Configurar o mock para retornar sequencialmente os resultados dos agentes
        mock_crew_instance = MagicMock()
        mock_crew.return_value = mock_crew_instance
        mock_crew_instance.kickoff.return_value = mock_editor_result
        
        # Executar a crew
        crew = ArticleCrew(llm="groq", language="pt", verbose=True)
        result = crew.run("Inteligência Artificial", 300)
        
        # Verificações
        assert result["status"] == "success"
        assert "article" in result
        assert result["article"]["title"] == "Inteligência Artificial: Revolução Tecnológica do Século XXI"
        assert len(result["article"]["sections"]) == 3
        assert "keywords" in result["article"]["metadata"]