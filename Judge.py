import json
import os
from openai import OpenAI
from llama_cpp import Llama
from dotenv import load_dotenv


load_dotenv()
#Paths

LOCAL_MODEL_PATH = "model\\Tuwaiq-Assistamt-v0.1-Llama-3.1-8B-Instruct.Q4_K_M.gguf"

DATASET_PATH ="tuwaiq_dataset_100.json"

OUTPUT_EVAL_PATH = "evaluation_results.json"

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


#Loading The Models

local_model = Llama(
    LOCAL_MODEL_PATH,
    n_gpu_layers=1,
    n_ctx=4096, #We Fine-tuned The model on 2048, but We use 4096 to give it more space (It doesnt harm).
)

deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY,base_url='https://api.deepseek.com')


def generate_local_response(prompt_text):
    formatted_prompt = f"السؤال: {prompt_text}\nالإجابة: "

    response = local_model(
        formatted_prompt,
        max_tokens=512, # Enough for our case
        temperature=0.7,
        stop=["<|eot_id|>", "<|end_of_text|>"]
    )
    print(f"response: {response}")
    print("-" *50)
    generated_text = response['choices'][0]['text']
    print(f"trimed: {generated_text}")
    
    return generated_text.strip()

# Uncomment for test
#generate_local_response("ما هي برامج المسار التأسيسي في طويق؟")

def evaluate_with_deepseek(instruction,reference_answer, model_answer):

    judge_prompt = f'''
    You are an impartial, expert evaluator of AI language models.
    You will be provided with a User Instruction, a Reference Answer (Ground Truth), and a Model Answer.
    Your task is to evaluate the Model Answer based on accuracy, completeness, and relevance to the Instruction, comparing it to the Reference Answer.

    [User Instruction]
    {instruction}

    [Reference Answer]
    {reference_answer}

    [Model Answer]
    {model_answer}

    Please provide your evaluation in the following strict JSON format without any markdown blocks or extra text:
    {{
        "score": <integer from 1 to 5, where 5 is excellent and 1 is completely wrong/irrelevant>,
        "rationale": "<a short explanation of why you gave this score, pointing out strengths or flaws>"
    }}
    '''
    try: 
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a precise JSON-outputting evaluation system."},
                {"role": "user", "content": judge_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        evaluation_result = json.loads(response.choices[0].message.content)
        return evaluation_result
    except Exception as e:
        print(f"Error calling DeepSeek: {e}")
        return {"score": 0, "rationale": f"API Error: {str(e)}"}
    


def main():
    with open(DATASET_PATH,"r",encoding="utf-8") as f:
        dataset = json.load(f)

    results = []

    print("Starting evaluation")

    for idx, item in enumerate(dataset):
        instruction = item.get("instruction","")

        reference_answer = item.get("output",'')

        model_answer = generate_local_response(instruction)

        evaluation = evaluate_with_deepseek(instruction,reference_answer,model_answer)

        result = {
            "id": idx+1,
            "instruction":instruction,
            "reference_answer": reference_answer,
            "model_answer":model_answer,
            "judge_score":evaluation.get("score"),
            "judge_rationale":evaluation.get("rationale")
        }
        results.append(result)

        #so we don't lose data if code stopped after some iterations
        with open(OUTPUT_EVAL_PATH, 'w', encoding='utf-8') as out_f:
            json.dump(results, out_f, ensure_ascii=False, indent=4)
            
        print(f"Score received: {evaluation.get('score')}/5")
    print(f"\nEvaluation Complete! Results saved to {OUTPUT_EVAL_PATH}")


if __name__ == "__main__":
    main()