import os
from dotenv import load_dotenv
from google import genai
from openai import OpenAI

class Model:
    def __init__(self):
        load_dotenv()

    @staticmethod
    def google_gemini(transcript, prompt, extra="", model_type="gemini-2.5-flash"):
        load_dotenv()
        try:
            client = genai.Client(
                api_key=os.getenv("GOOGLE_GEMINI_API_KEY")
            )

            response = client.models.generate_content(
                model=model_type,
                contents=prompt + extra + transcript
            )

            return response.text
        except Exception as e:
            response_error = "⚠️ There is a problem with the API key or with python module."
            return response_error, str(e)
    
    @staticmethod
    def openai_gpt(transcript, prompt, extra="", model_type="gpt-5-nano"):
        load_dotenv()
        try:
            client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )

            response = client.responses.create(
                model=model_type,
                input=prompt + extra + transcript
            )

            return response.output_text
        except Exception as e:
            response_error = "⚠️ There is a problem with the API key or with python module."
            return response_error, str(e)
