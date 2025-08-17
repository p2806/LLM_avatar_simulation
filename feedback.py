import fitz  # PyMuPDF
import ollama

# Function to extract text from a PDF
def analyze(prompt, model):
    try:
        print("\n--- PROMPT SENT TO MODEL ---\n")
        print(prompt)
        #response = ollama.chat(model=model, messages=[{'role': 'user', 'content': str(prompt)}])
        response = model.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
        print("\n--- RESPONSE FROM MODEL ---\n")
        #print(response['message']['content'])
        result = response.choices[0].message.content
        if not result.strip():
            print("Bot omitted a response.")
        return result
    except Exception as e:
        print(f"Error in OpenAI chat: {e}")
        return "Error during analysis."


def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text

# Load the PDFs
def analyze_context(model):
    pdf_files = ["trainingdata/ClinicalNote.pdf","trainingdata/Speakingrate.pdf"]

    # Extract text from both documents
    documents_text = "\n\n".join([extract_text_from_pdf(pdf) for pdf in pdf_files])

    # Define the LLaMA prompt for extraction
    llama_prompt = f"""
    Extract a **detailed and comprehensive** list of **best practices**, **communication techniques**, **nursing conversation strategies**, and **patient interaction methods** from the following text.

    TEXT:
    {documents_text}

    ### INSTRUCTIONS:
    - Identify and list all frameworks related to nursing communication.
    - Extract best practices for nursing conversations, patient engagement, and feedback strategies.
    - Focus on detailed **bullet points**, not summaries.
    - Remove any irrelevant content.
    - Maintain a structured, explicit output.

    """
    summary= analyze(llama_prompt,model)
    return summary


def final_evaluation(debrief_transcript,speechmetrics, model):
    """Synthesize insights from transcript and context analysis to provide a final evaluation."""
    print("\n--- EVALUATING DEBRIEF TRANSCRIPT ---\n")
    print(debrief_transcript)

    reference_doc_analysis = analyze_context(model)
    
    final_prompt = f"""
    Evaluate the following **Debrief Transcript** using the **Nursing Simulation Best Practices Bullet Points**.  

    **You MUST:**  
    - Clearly state **what the Nursing student did well** and **what needs improvement**.  
    - Use **specific bullet points** from the best practices list in your analysis.  
    - Quote or paraphrase **specific lines from the transcript** to support your points.
    - Evaluate **Speech Metrics**, including:
        - **Volume:** {speechmetrics['volume']} – Was this volume appropriate for clear communication?
        - **Pace (WPM):** {speechmetrics['words_per_minute']} – Was this speaking rate too slow or well-paced or too fast?
        - **Pitch & Intonation:** {speechmetrics['pitch']} – Did this student vary tone appropriately for engagement and emphasis?
        - **Pauses:** {speechmetrics['pauses']} – Were there meaningful pauses, or too many hesitations and fillers?

---

    ---

    **Nursing Simulation Best Practices Bullet Points:**  
    {reference_doc_analysis}  

    ---

    **Debrief Transcript:**  
    {debrief_transcript}  

    ---

    Evaluate the student based on:
        1. Which key points they **covered** completely.
        2. Which key points they **missed** or partially covered.
        3. Give a score out of 10.
        4. Provide specific feedback to the student.

        Output your answer in a clear, structured format.
    """

    evaluation = analyze(final_prompt, model)
    print("\n--- FINAL EVALUATION RESPONSE ---\n")
    print(evaluation)
    return evaluation


