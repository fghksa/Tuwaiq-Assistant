import requests
from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_community.llms import LlamaCpp
from langchain_core.prompts import PromptTemplate

# ==========================================
# 1. إدارة الحالة (State Management with Pydantic)
# ==========================================
class BootcampSearchState(BaseModel):
    query: str = Field(
        description="الكلمة المفتاحية للبحث، مثل: ذكاء اصطناعي، ويب، أمن سيبراني",
        default="كل المعسكرات"
    )

# ==========================================
# 2. أداة جلب البيانات عبر الـ API (The API Tool)
# ==========================================
@tool("search_tuwaiq_bootcamps", args_schema=BootcampSearchState)
def search_tuwaiq_bootcamps(query: str) -> str:
    """
    استخدم هذه الأداة دائماً للبحث في قاعدة بيانات أكاديمية طويق (API) عن المعسكرات والبرامج.
    """
    
    api_url = "https://tuwaiq.edu.sa/api/GetInitiativePublishesShorten/9/1?category=ac41152d-f228-8af4-8406-e0cda6df6c35&type=NORMAL"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json'
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # تحويل الاستجابة مباشرة إلى قاموس بايثون
        json_data = response.json()
        
        bootcamps_list = json_data.get("data", [])
        
        if not bootcamps_list:
            return "لم يتم العثور على أي معسكرات حالياً في قاعدة البيانات."
            
        results = []
        
        # المرور على كل معسكر واستخراج البيانات المهمة
        for item in bootcamps_list:
            title = item.get("title", "بدون عنوان")
            location = item.get("locationName", "غير محدد")
            is_open = item.get("isRegistrationOpen", False)
            track = item.get("initiativeScopeName", "")
            
            # فلترة: نأخذ فقط المعسكرات المتاح التسجيل فيها
            if is_open:
                # يمكنك فلترة النتائج بناءً على كلمة البحث (query) إذا أردت
                search_terms = query.replace("،", " ").replace(",", " ").split()
                if query == "كل المعسكرات" or any(term in title or term in track for term in search_terms):
                    results.append(f"- {title} | المسار: {track} | المقر: {location}")
                
        if not results:
            return "توجد معسكرات في قاعدة البيانات، ولكن التسجيل مغلق فيها جميعاً حالياً أو لا تطابق بحثك."
            
        # تجميع النتائج في نص واحد للنموذج
        final_result = "المعسكرات المتاح التسجيل فيها حالياً:\n" + "\n".join(results)
        return final_result
        
    except requests.exceptions.RequestException as e:
        return f"حدث خطأ في الاتصال بخوادم طويق: {str(e)}"
    except Exception as e:
        return f"حدث خطأ غير متوقع: {str(e)}"

# ==========================================
# 3. إعداد النموذج المحلي 
# ==========================================
LOCAL_MODEL_PATH = "model/Tuwaiq-Assistamt-v0.1-Llama-3.1-8B-Instruct.Q4_K_M.gguf"

llm = LlamaCpp(
    model_path=LOCAL_MODEL_PATH,
    temperature=0.1, 
    n_ctx=4096,
    max_tokens=512,
    # علامات التوقف المدمجة لمنع الهلوسة في هندسة ReAct
    # stop=[
    #     "Observation:", 
    #     "\nObservation:", 
    #     "<|eot_id|>", 
    #     "<|end_of_text|>"
    # ],
    verbose=False
)

# ==========================================
# 4. هندسة القالب (Prompt Engineering for ReAct)
# ==========================================
tools = [search_tuwaiq_bootcamps]

agent_template = """أنت مساعد ذكي لأكاديمية طويق. 
للبحث عن المعلومات، يجب عليك استخدام الأدوات المتاحة:
{tools}

أسماء الأدوات المتاحة لك حصرياً هي: [{tool_names}]

يجب أن تستخدم هذا التنسيق بالضبط. الكلمات (Thought, Action, Action Input, Observation, Final Answer) يجب أن تكتب باللغة الإنجليزية حرفياً ليتمكن النظام من فهمك.

--- مثال توضيحي صارم لطريقة عملك ---
السؤال: وش المعسكرات المتاحة للذكاء الاصطناعي؟
Thought: أحتاج للبحث في قاعدة البيانات لمعرفة المعسكرات المتاحة.
Action: search_tuwaiq_bootcamps
Action Input: الذكاء الاصطناعي
Observation: [نتيجة البحث ستظهر هنا]
Thought: الآن حصلت على المعلومات الكافية، سأقوم بصياغة الإجابة النهائية.
Final Answer: المعسكرات المتاحة حالياً للذكاء الاصطناعي هي كذا وكذا...
--- نهاية المثال ---

ابدأ الآن! وتذكر، لا تترجم كلمات (Thought, Action, Final Answer) أبداً.

السؤال: {input}
Thought:{agent_scratchpad}"""

prompt = PromptTemplate.from_template(agent_template)

# ==========================================
# 5. بناء وتشغيل الوكيل (Agent Build & Execute)
# ==========================================
agent = create_react_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, # سيجعلك ترى خطوات التفكير (Thought) واستدعاء الأداة
    handle_parsing_errors=True,
    max_iterations=3
)

def main():
    print("🤖 جاري تشغيل مساعد طويق الذكي...\n")
    
    # جربنا سؤالاً عاماً، الوكيل سيستخدم الأداة ويجيب بناءً على الـ JSON!
    user_query = "وش معسكرات الذكاء الاصطناعي المتاحة حالياً لتسجيل الكبار؟"
    
    print(f"👤 المستخدم: {user_query}")
    print("-" * 50)
    
    response = agent_executor.invoke({"input": user_query})
    
    print("-" * 50)
    print(f"✨ الإجابة النهائية:\n{response['output']}")

if __name__ == "__main__":
    main()