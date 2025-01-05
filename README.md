# TalentScout-Private

## Hiring Assistant Chatbot

### Project Overview
TalentScout is an AI-powered application designed to assist in the recruitment process by analyzing candidates’ resumes, conducting AI-based interviews, and providing insightful feedback based on the candidates' communication and technical skills. It automates the initial stages of the recruitment process, providing recruiters with detailed reports, summaries, and key takeaways to make more informed decisions.

### Features
- **Resume Extraction**: Allows candidates to submit their resumes and extract key details.
- **AI Interview**: Conducts an AI-driven interview with the candidate, testing their technical and communication skills. This includes:
    - **Coding Questions**: Evaluates the candidate's coding abilities through practical coding challenges.
    - **Architecture-Canvas Based Questions**: Assesses the candidate's understanding of system design and architecture through scenario-based questions.
- **Real-Time Reporting**: Provides real-time feedback on the candidate's performance, including ratings for communication and technical skills.
- **AI Analysis**: Uses GPT-powered models to analyze conversations and generate summaries and ratings based on predefined criteria.

### Installation Instructions

#### Prerequisites
Before you can set up the project, make sure you have the following installed on your system:
- Python 3.8 or higher
- Pip (Python's package installer)

#### Setup
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/hiring-assistant-chatbot.git
    cd hiring-assistant-chatbot
    ```
2. Create a Virtual Environment (Optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # For Linux/Mac
    venv\Scripts\activate     # For Windows
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Set up your OpenAI API Key:
    Create an `.env` file in the root of the project and add your API Key as follows:
    ```bash
    OPENAI_API_KEY=your-api-key-here
    ```

5. Run the application:
    ```bash
    streamlit run main.py
    ```
    This will start the application, and you can access it locally in your browser.

### Usage Guide
Once the application is up and running, here’s a guide on how to use it:
1. **Enter GPT API Key**: If you haven’t already entered your OpenAI API Key in the environment file, the app will prompt you to do so.
2. **Submit Candidate Details**: You can either upload a resume or manually fill out a form to provide the candidate's information.
3. **AI Interview**: The chatbot will guide the candidate through a brief AI interview. It will assess both communication and technical skills.
4. **Review the Report**: After the interview, a detailed report will be generated, showing an overall summary, ratings for communication and technical skills, and key takeaways.

### Technical Details

#### Libraries Used:
- **Streamlit**: A web framework to build interactive web apps quickly, used to create the user interface.
- **Pydantic**: For data validation and parsing of structured data like API responses.
- **OpenAI (GPT-4o-mini)-Strucured Outputs**: The core engine that powers the AI analysis and generation of text-based responses.

#### Model Details:
- **GPT-4o-mini**: The application uses OpenAI’s GPT-4o-mini model to generate analysis, summarize conversations, and rate the candidate’s communication and technical skills.
- **Custom Prompts**: Custom prompts are designed to guide the GPT-4o-mini model to generate the appropriate summary and ratings for each conversation.

#### Architectural Decisions:
- **Modular Design**: The code is split into multiple components:
  - `ask_questions`: Handles the AI interview phase.
  - `extract_details`: Handles the process of extracting details from resumes or forms.
  - `report`: Generates and displays the candidate’s detailed report.
  - `call_gpt`: A reusable function to interact with the GPT model.
- **State Management with Streamlit**: Streamlit's session state is used to manage the state of the application across different pages.

### Prompt Design
The GPT-4o-mini prompts are designed to guide the AI model in providing accurate and contextually relevant responses. Here’s how the prompts are structured:
- **System-Level Instructions**: The system prompt provides the GPT model with high-level instructions on what the assistant should do. For example, in the conversation analysis prompt, the model is instructed to analyze a conversation objectively and summarize the candidate’s communication and technical skills.
- **User-Level Input**: The user message contains the actual content to be analyzed (e.g., the conversation history). The user message includes clear instructions about the type of analysis required, such as generating summaries or evaluating specific skills.
- **Summary Structure**: The model returns a structured summary with key takeaways, communication skills rating, technical skills rating, and an overall assessment of the conversation.

### Challenges & Solutions
1. **Integrating GPT-3 for Real-Time Feedback**:
    - **Challenge**: GPT-4o-mini’s responses can be slow depending on the load, which can impact the user experience.
    - **Solution**: Introduced a loading spinner in the UI to inform the user that the application is processing the data. Also, optimized API calls by batching conversations before making a single request.
2. **Handling Different Candidate Interactions**:
    - **Challenge**: The chatbot had to effectively handle varied responses from different candidates, requiring flexible prompt design.
    - **Solution**: The prompts were designed to handle both short and long-form responses, with fallback strategies to ensure consistency in the analysis.
3. **Flexibility and Variety of Questions**:
    - **Challenge**: Ensuring the chatbot can ask a diverse range of questions, including technical, coding, and architecture-based questions.
    - **Solution**: Developed a comprehensive question bank that includes various types of questions, allowing the chatbot to assess different skill sets effectively.

### Contributing
We welcome contributions! If you have suggestions or bug fixes, feel free to submit an issue or a pull request.

### License
This project is licensed under the MIT License - see the LICENSE file for details.
