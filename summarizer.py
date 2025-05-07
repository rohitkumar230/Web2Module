import asyncio
import json
import google.generativeai as genai

from crawler import WebCrawler 

try:
    import configs
    if not hasattr(configs, 'GEMINI_KEY') or not configs.GEMINI_KEY:
        print("Error: GEMINI_KEY not found.")
        GEMINI_API_KEY = None
    else:
        GEMINI_API_KEY = configs.GEMINI_KEY
except ImportError:
    print("Error: configs.py not found. Please create it with your GEMINI_KEY.")
    GEMINI_API_KEY = None


class ContentSummarizer:
    def __init__(self):
        self.model = None
        self.api_key_configured = False

        if GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                # Using gemini-2.0-flash-001 
                self.model = genai.GenerativeModel(
                    model_name='gemini-2.0-flash-001', 
                    generation_config={"response_mime_type": "application/json"}
                )
                self.api_key_configured = True
                print("ContentSummarizer initialized with Gemini model (gemini-1.5-flash-latest).")
            except Exception as e:
                print(f"Error (Summarizer): Failed to initialize Gemini model: {e}")
        else:
            print("Warning (Summarizer): Gemini API key not configured. Summarizer will not function.")

    def _build_prompt(self, markdown_content: str, url: str) -> str:
        
        prompt = f"""
        Context
        You are provided with content from a documentation or help page accessible via a URL: {url}. Your task is to thoroughly analyze this content and restructure it into a well-organized JSON format that clearly identifies the modules and submodules of the product/service being documented.
        Definitions
        Module: A major functional component or section of the product that typically encompasses multiple related features or capabilities. Modules are managed by product managers and represent distinct areas of functionality.
        Submodule: A specific feature, capability, or process that belongs to a module. Submodules typically perform specific tasks or provide specific functionality within the larger context of their parent module.

        Example
        For instance, if we consider Instagram as a product:
        "Reels" would be a module
        Under the "Reels" module, submodules might include "Create Reels," "Edit Reels," and "Share Reels"
        "Manage Account" would be another module
        Under "Manage Account," submodules might include "Delete Account" and "Activate/Deactivate Account"

        *Task Instructions*
        Carefully read and analyze the provided documentation. The content might contain several useless contents that must be ignored.
        Identify all major modules described in the documentation.

        For each module:
        Create a clear, concise name that reflects its purpose
        Write a detailed description of what the module does
        Identify all submodules that belong to this module
        For each submodule, write a detailed description of its functionality

        Here I have provided you the web crawled content in markdown format:
        ---
        {markdown_content}
        ---

        Structure your output in the following JSON format (a list of module objects):
        ```json
        [
          {{  // Escaped brace
            "module": "Module_Name",
            "Description": "Detailed description of the module, including its overall purpose and functionality",
            "Submodules": {{ // Escaped brace
              "Submodule_Name_1": "Detailed description of the first submodule's functionality",
              "Submodule_Name_2": "Detailed description of the second submodule's functionality",
              "Submodule_Name_3": "Detailed description of the third submodule's functionality"
            }} // Escaped brace
          }}, // Escaped brace
          {{ // Escaped brace
            "module": "Another_Module_Name",
            "Description": "Detailed description of this module",
            "Submodules": {{ // Escaped brace
              "Submodule_Name_1": "Detailed description of this submodule",
              "Submodule_Name_2": "Detailed description of this submodule"
            }} // Escaped brace
          }} // Escaped brace
        ]
        ```

        *Guidelines*

        Be comprehensive - capture all modules and submodules mentioned in the documentation
        Be precise - ensure module and submodule names accurately reflect their functionality
        Be detailed - provide thorough descriptions that clearly explain what each module and submodule does
        Maintain consistent formatting according to the specified JSON structure
        Ensure your descriptions are factual and based solely on the provided documentation
        If a module has no clear submodules, include an empty object for the "Submodules" field: "Submodules": {{}}
        If the documentation structure isn't clear, make your best judgment to organize the content into logical modules and submodules

        *Additional Notes*

        Focus on functional organization rather than navigational or UI organization of the documentation
        Ensure all JSON syntax is valid and properly formatted
        Use descriptive names for modules and submodules that would make sense to product managers and developers
        Descriptions should be comprehensive enough to understand the purpose without being excessively verbose."""
        return prompt

    async def generate_json_summary(self, markdown_content: str, url: str):
        if not self.api_key_configured or not self.model:
            print("Error (Summarizer): Not configured with API key or model.")
            return None 
        
        if not markdown_content or not markdown_content.strip():
            print("Warning (Summarizer): Markdown content is empty. Returning empty list for summary.")
            return []

        prompt = self._build_prompt(markdown_content, url)
        
        response_text_for_error_logging = "" # Initialize for error logging
        try:
            response = await self.model.generate_content_async([prompt])
            response_text_for_error_logging = response.text # Store for potential error log
            
            json_response_text = response.text.strip()
            
            if json_response_text.startswith("```json"):
                json_response_text = json_response_text[7:-3].strip()
            elif json_response_text.startswith("```"):
                 json_response_text = json_response_text[3:-3].strip()

            parsed_json = json.loads(json_response_text)
            return parsed_json
        except json.JSONDecodeError as e:
            print(f"Error (Summarizer): Failed to decode JSON from Gemini response: {e}")
            print(f"Problematic response text (first 1000 chars): {response_text_for_error_logging[:1000]}...")
            return None
        except Exception as e:
            error_message = f"Error (Summarizer): During summary generation: {e}"
            # Try to get more specific feedback if available from the response object
            if 'response' in locals() and hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                error_message += f" - Prompt blocked, reason: {response.prompt_feedback.block_reason}"
            elif 'response' in locals() and not response.candidates:
                 error_message += f" - No candidates in response. Finish reason: {response.prompt_feedback if hasattr(response, 'prompt_feedback') else 'N/A'}"
            print(error_message)
            return None