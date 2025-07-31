import google.generativeai as genai
from app.loction import get_top_7_hospitals
from app.volunteer_utils import get_all_available_volunteers
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API using environment variable
api_key = os.environ.get('GEMINI_API_KEY')
if api_key and api_key != 'your-gemini-api-key-here':
    genai.configure(api_key=api_key)
    print("✅ Gemini API configured successfully")
else:
    print("❌ Gemini API key not found or invalid")

# Conversation history to store previous exchanges
conversation_history = []

def format_hospitals_for_prompt(hospitals):
    result = []
    for i, h in enumerate(hospitals, 1):
        specialty = ', '.join(h['specialty']) if isinstance(h['specialty'], list) else h['specialty']
        result.append(
            f"{i}. {h['name']} – {h['distance_km']:.1f} km\n"
            f"   specialty: {specialty}\n"
            f"   contact: {h['contact']}\n"
        )
    return "\n".join(result)

def format_volunteers_for_prompt(volunteers):
    if not volunteers:
        return "No doctors are currently available."

    formatted = []
    for i, v in enumerate(volunteers, 1):
        formatted.append(
            f"{i}. {v.name or 'Anonymous'}\n"
            f"   📞 Phone: {v.phone_number}\n"
            f"   🩺 Specialty: {v.specialty or 'Not specified'}\n"
            f"   ⏰ Time: {v.available_times} on {v.available_days}\n"
        )
    return "\n".join(formatted)

# Fallback response when API fails
def get_fallback_response(query, user_coords=None):
    """Provide basic first aid guidance when Gemini API is unavailable"""
    
    # Get hospital and volunteer info
    hospitals = get_top_7_hospitals(user_coords) if user_coords else []
    volunteers = get_all_available_volunteers()
    
    hospital_text = format_hospitals_for_prompt(hospitals) if hospitals else "لا تتوفر معلومات المستشفيات حالياً."
    volunteer_text = format_volunteers_for_prompt(volunteers) if volunteers else "لا يوجد أطباء متطوعون متاحون حالياً."
    
    response = f"""عذراً، الخدمة الذكية غير متاحة حالياً. إليك المعلومات الأساسية:

🏥 أقرب المستشفيات:
{hospital_text}

👨‍⚕️ الأطباء المتطوعون المتاحون:
{volunteer_text}

⚠️ في حالات الطوارئ الطبية:
- اتصل بالطوارئ فوراً: 999
- لا تتردد في طلب المساعدة
- حافظ على الهدوء
- إذا كان الشخص فاقداً للوعي، تأكد من وضعه في وضع الإفاقة

يرجى المحاولة مرة أخرى لاحقاً للحصول على المساعدة الذكية."""
    
    return response

# Simplified prompt without RAG/PDF reference
def make_prompt(query, history, user_coords=None):
    top_hospitals = get_top_7_hospitals(user_coords)
    hospital_info_text = format_hospitals_for_prompt(top_hospitals) if top_hospitals else "Location not available."

    # Volunteer doctor section
    volunteers = get_all_available_volunteers()
    if volunteers:
        volunteers_info = format_volunteers_for_prompt(volunteers)
    else:
        volunteers_info = "لا يوجد طبيب متطوع متاح حالياً. حاول لاحقاً أو تواصل مع أقرب مستشفى."

    history_text = " ".join([f"User: {item['question']}\nBot: {item['answer']}" for item in history])

    prompt = (
        "You are a knowledgeable, calm, and friendly virtual first aid assistant, designed specifically to help people in Sudan. "
        "You provide clear, accurate, step-by-step instructions to help users respond to medical emergencies using your extensive medical knowledge. "
        "Use language that is easy to understand for everyone. Use Sudanese Arabic, and if the question is in English, answer in English. "
        "Avoid medical jargon. Use examples or explanations if needed. "
        "Always prioritize safety, stay factual, and keep answers short, actionable, and reassuring. "
        "If the question is unclear or not directly answerable, politely say that and recommend contacting a licensed healthcare provider. "
        "If the situation described seems life-threatening or urgent, remind the user to seek help from emergency services or a trained person nearby.\n\n"

        f"User location is: {user_coords}\n"
        f"Here are the 7 closest hospitals:\n{hospital_info_text}\n\n"
        "From the list above, choose the most relevant hospital based on the emergency. "
        "If more than one hospital is suitable, pick the closest. Mention which one and explain why.\n\n"

        f"Volunteer doctors currently available:\n{volunteers_info}\n"
        "From the list above, choose the most relevant volunteer doctor based on the emergency. "
        "If there is no doctor that is directly relevant, suggest partially relevant ones.\n\n"

        f"Conversation History:\n{history_text}\n\n"
        "If there is conversation history, use it to understand the context of the user's question and continue the conversation from where you left off.\n\n"
        
        f"QUESTION: '{query}'\n\n"

        "Provide comprehensive first aid guidance based on your medical knowledge. "
        "After you answer the user's question, ask any important follow-up related questions that may help medical professionals later. "
        "Politely and clearly ask the user to provide this information, as it may be critical for diagnosis and treatment when they reach the hospital.\n\n"

        "ANSWER:"
    )

    return prompt

# Function to generate a response using Gemini
def generate_response(user_prompt):
    try:
        # Check if API key is configured
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key or api_key == 'your-gemini-api-key-here':
            return None  # Return None to trigger fallback
        
        # Limit prompt length to avoid issues
        if len(user_prompt) > 10000:
            user_prompt = user_prompt[:10000] + "..."
            
        model = genai.GenerativeModel('gemini-1.5-pro')  # Use more stable version
        response = model.generate_content(user_prompt)
        
        if response and response.text:
            return response.text
        else:
            return None  # Trigger fallback
            
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return None  # Trigger fallback

# Main function to ask a question and store the answer in history (No RAG)
def ask_question(query, user_coords=None):
    try:
        # Try to get Gemini response first
        prompt = make_prompt(
            query,
            history=conversation_history,
            user_coords=user_coords
        )

        answer = generate_response(prompt)
        
        # If Gemini fails, use fallback
        if answer is None:
            answer = get_fallback_response(query, user_coords)

        conversation_history.append({'question': query, 'answer': answer})
        if len(conversation_history) > 5:
            conversation_history.pop(0)

        return answer
    except Exception as e:
        print(f"Ask question error: {str(e)}")
        return get_fallback_response(query, user_coords)
