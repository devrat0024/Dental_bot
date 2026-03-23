import os
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate

class DentalLLMService:
    def __init__(self, model_name="microsoft/phi-2"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.pipe = None
        self.llm = None
        self.medical_context = None

    def ensure_loaded(self):
        if self.llm is not None:
            return
            
        print(f"Loading model {self.model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            torch_dtype="auto"
        )
        self.pipe = pipeline(
            "text-generation",
            tokenizer=self.tokenizer,
            model=self.model,
            max_new_tokens=300,
            temperature=0.3
        )
        self.llm = HuggingFacePipeline(pipeline=self.pipe)
        
        # Load Medical Context
        context_path = os.path.join(os.path.dirname(__file__), "..", "context", "medical_guidelines.txt")
        self.medical_context = ""
        try:
            with open(context_path, "r") as f:
                self.medical_context = f.read()
        except Exception as e:
            print(f"Warning: Could not load medical context from {context_path}. Error: {e}")

        # Improved Prompt Template infused with Context
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a professional Dental Health Assistant AI operating in a production context.

Strict Guidelines:
{context}

Given the above medical guidelines, answer the following user question appropriately.
If the question is out of scope or requires diagnosis, politely decline and instruct them to see a dentist.

Question:
{question}

Answer:
"""
        )
        
    def get_dental_advice(self, question: str) -> str:
        self.ensure_loaded()
        prompt_val = self.prompt_template.format(context=self.medical_context, question=question)
        response = self.llm.invoke(prompt_val)
        
        # Clean up the output to only return what comes after "Answer:" if generated text includes the prompt
        if "Answer:\n" in response:
            response = response.split("Answer:\n")[-1].strip()
            
        return response

# Instantiate a global instance, but it won't load the model until first use
llm_service = DentalLLMService()
