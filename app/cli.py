"""
Interface de linha de comando para geração de artigos.
"""
import os
import sys
import json
import argparse
import traceback
from dotenv import load_dotenv

from crewai import Process

from app.crew.article_crew import ArticleCrew
from app.models.article import Article


def main():
    """Função principal da CLI."""
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Configuração do parser de argumentos
    parser = argparse.ArgumentParser(description="Gerador de Artigos da Wikipedia")
    parser.add_argument("topic", help="Tópico para geração do artigo")
    parser.add_argument("--min-words", type=int, default=300, help="Número mínimo de palavras (padrão: 300)")
    parser.add_argument("--sections", type=int, help="Número desejado de seções")
    parser.add_argument("--language", default="pt", help="Código de idioma para a Wikipedia (padrão: pt)")
    parser.add_argument("--llm", default=os.getenv("DEFAULT_LLM", "groq"), 
                        choices=["groq", "gemini"], help="Modelo LLM a ser usado")
    parser.add_argument("--verbose", action="store_true", help="Mostrar logs detalhados")
    parser.add_argument("--output", "-o", help="Arquivo de saída (opcional)")
    parser.add_argument("--hierarchical", action="store_true", 
                        help="Usar processo hierárquico em vez de sequencial")
    
    args = parser.parse_args()
    
    # Configuração do processo
    process = Process.hierarchical if args.hierarchical else Process.sequential
    
    print(f"🚀 Iniciando geração de artigo sobre '{args.topic}'...")
    print(f"⚙️  Configurações: LLM={args.llm}, Idioma={args.language}, Mín. Palavras={args.min_words}")
    
    try:
        # Criar e executar a crew
        crew = ArticleCrew(
            llm=args.llm,
            language=args.language,
            verbose=args.verbose,
            process=process
        )
        
        result = crew.run(args.topic, args.min_words, args.sections)
        
        if result["status"] == "success":
            article_data = result["article"]
            article = Article(**article_data)
            
            # Exibição do resultado
            print("\n✅ Artigo gerado com sucesso!")
            print(f"📝 Título: {article.title}")
            print(f"⏱️  Tempo de processamento: {result['processing_time']} segundos")
            print(f"📊 Contagem de palavras: {article.word_count}")
            print(f"🔑 Palavras-chave: {', '.join(article.metadata.keywords)}")
            
            # Salvar em arquivo se especificado
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(article_data, f, ensure_ascii=False, indent=2)
                print(f"\n💾 Artigo salvo em: {args.output}")
            else:
                # Exibir resumo
                print("\n📋 Resumo:")
                print(article.summary)
                print("\n🔗 Use --output para salvar o artigo completo em um arquivo")
                
        else:
            print(f"\n❌ Erro na geração do artigo: {result.get('error', 'Erro desconhecido')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        print("\nStack trace completo:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()