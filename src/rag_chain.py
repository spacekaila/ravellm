from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sentence_transformers import SentenceTransformer
from src.vector_store import PatternVectorStore


class RavelryRAG:
    def __init__(self, model_name="mistral:7b"):
        """Initialize RAG system"""
        self.llm = OllamaLLM(model=model_name, temperature=0.7)
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.vector_store = PatternVectorStore()

        # prompt template
        self.prompt = PromptTemplate(
            input_variables=["query", "context"],
            template="""You are a knowledgeable knitting assistant helping someone find the perfect pattern.

            Based on the following knitting patterns, recommend the best options for this request:
            
            REQUEST{query}
            
            RELEVANT PATTERNS: {context}
            
            Provide 2-3 personalized recommendations. For each pattern, explain:
            1. Why it matches their request
            2. What skill level it requires
            3. Any important details they should know
            4. Provide the ravelry link to the pattern
            
            Be friendly, helpful, and concise.
            
            RECOMMENDATIONS:"""
        )

        #self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        self.chain = self.prompt | self.llm | StrOutputParser()

    def retrieve(self, query, n_results=10):
        """Retrieve relevant patterns"""
        # Embed query
        query_embedding = self.embedder.encode(query)

        # Search vector DB
        results = self.vector_store.search(query_embedding, n_results=n_results)

        return results

    def format_context(self, results):
        """Format retrieved patterns for LLM"""
        context_parts = []

        for i, metadata in enumerate(results["metadatas"][0], 1):
            context_parts.append(
                f"{i}. {metadata["name"]} by {metadata["designer"]}\n"
                f"  Type: {metadata["category"]}\n"
                f"  Yarn weight: {metadata["yarn_weight"]}\n"
                f"  Difficulty: {metadata["difficulty"]:.1f}/10\n"
                f"  Link: {metadata["url"]}"
            )
        return "\n\n".join(context_parts)

    def generate_recommendations(self, query):
        """End-to-end RAG: retrieve and generate"""
        # Retrieve relevant patterns
        results = self.retrieve(query, n_results=5)

        # Format context
        context = self.format_context(results)

        # Generate recommendations
        #response = self.chain.run(query=query, context=context)
        response = self.chain.invoke({"query": query,
                                      "context": context})

        return response, results


def main():
    rag = RavelryRAG()

    query = "i want to knit a chunky cardigan"

    print(f"query: {query}\n")
    print("generating recommendations...\n")

    recommendations, patterns = rag.generate_recommendations(query)

    print(recommendations)
    print(patterns)


if __name__ == "__main__":
    main()
