import torch 
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "llama/model/Llama3.2-3B"

tokenizer = AutoTokenizer.from_pretrained(model_name) 
model = AutoModelForCausalLM(tokenizer)#model = AutoModelForCausalLM.from_pretrained(model_name)

# Tenta transferir o modelo pra GPU se não usa a CPU mesmo. 
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

def generate_response(prompt, max_length=2048):
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    outputs = model.generate(
        inputs["inputs_ids"],
        max_length=max_length,
        num_return_sequence=1,
        pad_token_id=tokenizer.eos_token_id,
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response