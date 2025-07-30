from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
import google.generativeai as genai
from app.loction  import get_top_7_hospitals
from app.volunteer_utils import get_all_available_volunteers
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API using environment variable
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))


#  path to the PDF
pdf_path = os.path.join(os.path.dirname(__file__), "pdfs", "first_aid_notes_2019.pdf")

# Load and split documents
loader = PyPDFLoader(pdf_path)
documents = loader.load()

# All documents list
all_documents = documents


# Split the text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
chunks = text_splitter.split_documents(all_documents)

# Load the embedding model and embed the text chunks
huggingface_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Create the FAISS index directly using the embeddings and text chunks
faiss_store = FAISS.from_documents(chunks, huggingface_embeddings)

# Set up a retriever
retriever = faiss_store.as_retriever(search_kwargs={"max_chunks": 5})

# Conversation history to store previous exchanges
conversation_history = []

# Function to retrieve relevant text chunks
def get_relevant_docs(query):
    docs = retriever.get_relevant_documents(query)
    relevant_chunks = [doc.page_content for doc in docs]
    return relevant_chunks

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


# Function to create RAG prompt with conversation memory
def make_rag_prompt(query, relevant_passage, history, top_hospitals=None, user_coords=None):
    relevant_passage = ' '.join(relevant_passage)
    top_hospitals = get_top_7_hospitals(user_coords)
    hospital_info_text = format_hospitals_for_prompt(top_hospitals) if top_hospitals else "Location not available."

    # 🆕 Volunteer doctor section
    volunteers = get_all_available_volunteers()
    if volunteers:
        volunteers_info = format_volunteers_for_prompt(volunteers)
    else:
        volunteers_info = "لا يوجد طبيب متطوع متاح حالياً. حاول لاحقاً أو تواصل مع أقرب مستشفى."

    history_text = " ".join([f"User: {item['question']}\nBot: {item['answer']}" for item in history])

    prompt = (
        "You are a knowledgeable, calm, and friendly virtual first aid assistant, designed specifically to help people in Sudan. "
        "You provide clear, accurate, step-by-step instructions to help users respond to medical emergencies. "
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
        "if there is conversation history, use it to understand the context of the user's question.  and continuing the conversation. form where you left it \n\n"
        f"QUESTION: '{query}'\n"
        f"REFERENCE PASSAGE: '{relevant_passage}'\n\n"

        "After you answer the user's question, ask any important follow-up related questions that may help medical professionals later.  \n"
        "Politely and clearly ask the user to provide this information, as it may be critical for diagnosis and treatment when they reach the hospital.\n\n"

        "ANSWER:"
    )

    return prompt



   

# Function to generate a response using Gemini
def generate_response(user_prompt):
    model = genai.GenerativeModel('gemini-2.5-pro')
    answer = model.generate_content(user_prompt)
    return answer.text

# Main function to ask a question and store the answer in history
def ask_question(query, user_coords=None):
    relevant_text = get_relevant_docs(query)

    # If we received user coordinates, find top hospitals
    top_hospitals = get_top_7_hospitals(user_coords) if user_coords else []

    prompt = make_rag_prompt(
        query,
        relevant_passage=relevant_text,
        history=conversation_history,
        top_hospitals=top_hospitals,
        user_coords=user_coords
    )

    answer = generate_response(prompt)

    conversation_history.append({'question': query, 'answer': answer})
    if len(conversation_history) > 5:
        conversation_history.pop(0)

    return answer


