import requests
from langchain_ollama import OllamaLLM 
from langchain_core.prompts import PromptTemplate
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain.tools import tool

# ==========================================
# 1. Search Tool (Smart Version)
# ==========================================
@tool("search_tuwaiq_bootcamps")
def search_tuwaiq_bootcamps(query: str) -> str:
    """Useful for searching about current training programs and bootcamps at Tuwaiq Academy."""
    # API endpoint to fetch live bootcamp data
    api_url = "https://tuwaiq.edu.sa/api/GetInitiativePublishesShorten/9/1?category=ac41152d-f228-8af4-8406-e0cda6df6c35&type=NORMAL"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(api_url, headers=headers, timeout=10)
        bootcamps = response.json().get("data", [])
        
        # Clean the search query by removing common filler words that might hinder search results
        ignore_words = ["المعسكرات", "الحالية", "المتوفرة", "متاحة", "أكاديمية", "طويق", "ابي", "وش", "في"]
        search_term = query
        for word in ignore_words:
            search_term = search_term.replace(word, "").strip()

        # Filter the bootcamps based on registration status and search keyword
        results = [f"**{b['title']}** | المقر: {b['locationName']}" 
                   for b in bootcamps 
                   if b.get("isRegistrationOpen") and (search_term in b['title'] or not search_term)]
        
        if not results:
            return "توجد معسكرات حالية ولكن التسجيل مغلق، أو حاول البحث بكلمة أخرى مثل 'برمجة'."
            
        return "\n\n".join(results)
    except:
        return "عذراً، تعذر جلب البيانات الحية حالياً."

# ==========================================
# 2. Model and Prompt Configuration
# ==========================================
# Initialize the local LLM using Ollama (Llama 3.1 based)
llm = OllamaLLM(model="tuwaiq-model", temperature=0)

# Define the ReAct agent prompt template with English logic and Arabic output
template = """You are a helpful assistant for Tuwaiq Academy (أكاديمية طويق). 
Answer in Arabic. Correct the name to "أكاديمية طويق" always.

You have access to:
{tools}

Use the following format strictly:
Thought: تفكيرك بالعربي
Action: {tool_names}
Action Input: كلمة البحث
Observation: النتيجة
... (repeat if needed)
Final Answer: اكتب ردك النهائي للمستخدم هنا بالعربي مباشرة وبتنسيق نقاط.

Question: {input}
Thought: {agent_scratchpad}"""

prompt = PromptTemplate.from_template(template)

# ==========================================
# 3. Agent Construction and Execution
# ==========================================
# List of tools accessible by the agent
tools = [search_tuwaiq_bootcamps]

# Create the ReAct agent
agent = create_react_agent(llm, tools, prompt)

# Initialize the Agent Executor with error handling and iteration limits
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    handle_parsing_errors=True, # Handles cases where LLM formatting is imperfect
    max_iterations=5            # Maximum loops to prevent infinite logic cycles
)