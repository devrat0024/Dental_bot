from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate

model_name = "microsoft/phi-2"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype="auto"
)

pipe = pipeline(
    "text-generation",
    tokenizer=tokenizer,
    model=model,
    max_new_tokens=300,
    temperature=0.3
)

llm = HuggingFacePipeline(pipeline=pipe)

dental_prompt = PromptTemplate(
    input_variables=["question"],           # lowercase is conventional
    template="""
You are a professional Dental Health Assistant AI.

Rules:
- Educational information only
- No diagnosis
- No medicine prescription
- Always recommend visiting a dentist

Question:
{question}

Answer:
"""
)

def dental_health(question: str) -> str:
    prompt = dental_prompt.format(question=question)
    return llm.invoke(prompt)               # .invoke() is the modern / preferred method

# Fixed small typos & naming
if __name__ == "__main__":
    while True:
        user_input = input("Ask a dental health question (or type exit): ")
        if user_input.lower() == "exit":
            break
        response = dental_health(user_input)    # ← was dental_chatbot → rename or fix
        print("\nDental Answer:", response)