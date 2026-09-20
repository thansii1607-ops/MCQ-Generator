import streamlit as st
from huggingface_hub import InferenceClient
import re

st.set_page_config(
    page_title="MCQ Generator AI",
    page_icon="📝",
    layout="centered"
)

st.title("📝 MCQ Generator AI")
st.write("Generate Multiple Choice Questions using AI")

# ---------------- INPUT SECTION ----------------

topic = st.text_input(
    "Enter Topic",
    placeholder="Example: Python Programming"
)

num_questions = st.selectbox(
    "Number of Questions",
    [5, 10, 15]
)

difficulty = st.selectbox(
    "Difficulty Level",
    ["Easy", "Medium", "Hard"]
)

# ---------------- GENERATE MCQs ----------------

if st.button("✨ Generate MCQs"):

    if not topic.strip():
        st.warning("Please enter a topic.")
        st.stop()

    try:
        token = st.secrets["HF_TOKEN"]

        client = InferenceClient(
            api_key=token
        )

        prompt = f"""
Generate exactly {num_questions} multiple choice questions
about {topic}.

Difficulty: {difficulty}

Use EXACTLY this format for every question:

QUESTION: What is Python?
A) A programming language
B) A database
C) An operating system
D) A browser
ANSWER: A
EXPLANATION: Python is a high-level programming language.

Rules:
- Generate exactly {num_questions} questions.
- Each question must have exactly 4 options.
- Only one option must be correct.
- Give the correct answer as A, B, C, or D.
- Give a short explanation.
- Keep questions clear and educational.
"""

        with st.spinner("Generating MCQs..."):

            response = client.chat.completions.create(
                model="meta-llama/Llama-3.1-8B-Instruct",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=3500,
                temperature=0.7
            )

        result = response.choices[0].message.content

        # Save generated questions
        st.session_state["mcq_result"] = result

    except KeyError:
        st.error("HF_TOKEN not found. Check your secrets.toml file.")

    except Exception as e:
        st.error(f"Error: {e}")


# ---------------- DISPLAY MCQs ----------------

if "mcq_result" in st.session_state:

    st.markdown("---")
    st.subheader("📚 Your MCQs")

    text = st.session_state["mcq_result"]

    # Split questions
    questions = re.split(
        r"(?=QUESTION:)",
        text
    )

    question_number = 0

    for block in questions:

        block = block.strip()

        if not block.startswith("QUESTION:"):
            continue

        question_number += 1

        # Question
        question_match = re.search(
            r"QUESTION:\s*(.*?)(?=\nA\))",
            block,
            re.DOTALL
        )

        # Options
        option_a = re.search(
            r"A\)\s*(.*?)(?=\nB\))",
            block,
            re.DOTALL
        )

        option_b = re.search(
            r"B\)\s*(.*?)(?=\nC\))",
            block,
            re.DOTALL
        )

        option_c = re.search(
            r"C\)\s*(.*?)(?=\nD\))",
            block,
            re.DOTALL
        )

        option_d = re.search(
            r"D\)\s*(.*?)(?=\nANSWER:)",
            block,
            re.DOTALL
        )

        answer_match = re.search(
            r"ANSWER:\s*([ABCD])",
            block,
            re.IGNORECASE
        )

        explanation_match = re.search(
            r"EXPLANATION:\s*(.*)",
            block,
            re.DOTALL
        )

        if not all([
            question_match,
            option_a,
            option_b,
            option_c,
            option_d,
            answer_match
        ]):
            continue

        question = question_match.group(1).strip()

        options = [
            option_a.group(1).strip(),
            option_b.group(1).strip(),
            option_c.group(1).strip(),
            option_d.group(1).strip()
        ]

        correct_answer = answer_match.group(1).upper()

        explanation = (
            explanation_match.group(1).strip()
            if explanation_match
            else "No explanation available."
        )

        # Question heading
        st.markdown(
            f"### Question {question_number}"
        )

        st.write(question)

        # Radio button
        selected = st.radio(
            "Select your answer:",
            [
                f"A. {options[0]}",
                f"B. {options[1]}",
                f"C. {options[2]}",
                f"D. {options[3]}"
            ],
            key=f"question_{question_number}",
            index=None
        )

        # Submit button
        if st.button(
            "Submit Answer",
            key=f"submit_{question_number}"
        ):

            if selected is None:

                st.warning("Please select an option.")

            else:

                selected_letter = selected[0]

                if selected_letter == correct_answer:

                    st.success(
                        f"✅ Correct Answer: {correct_answer}. "
                        f"{options[ord(correct_answer) - ord('A')]}"
                    )

                else:

                    st.error(
                        f"❌ Incorrect. Correct Answer: "
                        f"{correct_answer}. "
                        f"{options[ord(correct_answer) - ord('A')]}"
                    )

                with st.expander("💡 Explanation"):

                    st.write(explanation)

        st.markdown("---")