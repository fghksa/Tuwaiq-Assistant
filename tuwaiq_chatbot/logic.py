import json
import requests
from openai import OpenAI
from datetime import datetime

def fetch_tuwaiq_api(url, category_name):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            raw_data = response.json()
            items = raw_data.get('data', [])
            context = f"\n=== قائمة {category_name} المحدثة ===\n"
            for item in items:
                title = item.get('title', 'غير متوفر')
                scope = item.get('initiativeScopeName', 'عام')
                start_date = item.get('startDate', '')
                is_open = "متاح" if item.get('isRegistrationOpen') else "مغلق"
                slug = item.get('slug', '')
                
                try:
                    date_obj = datetime.fromisoformat(start_date).strftime('%Y-%m-%d') if start_date else "غير محدد"
                except:
                    date_obj = start_date

                context += f"- {title} ({scope}) | البدء: {date_obj} | الحالة: {is_open}\n"
                context += f"  الرابط: https://tuwaiq.edu.sa/bootcamp/{slug}/view\n"
            return context
    except:
        return f"\n(فشل تحديث {category_name})\n"
    return ""

def load_all_knowledge():
    knowledge_base = "=== الأسئلة الشائعة ===\n"
    try:
        with open('data/faq_dataset.json', 'r', encoding='utf-8') as f:
            faq_data = json.load(f)
            for item in faq_data:
                knowledge_base += f"سؤال: {item['instruction']}\nإجابة: {item['output']}\n---\n"
    except:
        pass

    bootcamps_url = "https://tuwaiq.edu.sa/api/GetInitiativePublishesShorten/9/1?category=ac41152d-f228-8af4-8406-e0cda6df6c35&type=NORMAL"
    programs_url = "https://tuwaiq.edu.sa/api/GetInitiativePublishesShorten/9/1?category=8836bde0-68ae-3600-92a2-23dce3c487ca&type=NORMAL"
    
    knowledge_base += fetch_tuwaiq_api(bootcamps_url, "المعسكرات")
    knowledge_base += fetch_tuwaiq_api(programs_url, "البرامج")
    return knowledge_base

def get_ai_response(api_key, messages, context):
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    system_prompt = {
        "role": "system", 
        "content": f"أنت مساعد رسمي لأكاديمية طويق. أجب بناءً على هذه البيانات فقط: {context}"
    }
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[system_prompt] + messages,
        temperature=0.3
    )
    return response.choices[0].message.content