import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class PromptModifier:
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("[INFO] Initializing PromptModifier with OpenAI")
        
    def enhance_prompt(self, question, user_inputs):
        """Create optimized DALL-E 3 prompts from user inputs."""
        try:
            system_prompt = """You are an expert creative director specializing in photorealistic visualization.
            Transform user descriptions into vivid, detailed scenes by:
            1. Interpreting the question's intent and user inputs into a cohesive visual narrative
            2. Creating a natural response scene that directly answers the question
            3. Incorporating sophisticated lighting (natural or artificial depending on context)
            4. Adding rich material details (textures, surfaces, fine details like scratches, fabric weave, or reflections)
            5. Using atmospheric elements to enhance depth (light effects, particles, moisture)
            6. Maintaining professional composition with clear focal points
            7. Implementing natural color palettes with strong contrast
            
            Key guidelines:
            - Create photorealistic, highly detailed scenes
            - Focus on the interaction between subjects and their environment
            - Maintain a professional documentary-style quality
            - Include micro-details that enhance realism
            
            Format as a single, flowing paragraph focused on visual description.
            Emphasize both the main subject and supporting details while keeping a natural, realistic feel."""
            
            context_prompt = f"""
            Context question: {question}
            User description: {user_inputs}
            
            Create a DALL-E 3 optimized prompt that translates these elements into a photorealistic visualization.
            Focus on creating a detailed, high-definition scene that directly answers the question while maintaining
            natural composition and lighting.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context_prompt}
                ],
                temperature=0.5,
                max_tokens=300,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            enhanced = response.choices[0].message.content.strip()
            print(f"[INFO] Generated DALL-E prompt: {enhanced}")
            return enhanced
                
        except Exception as e:
            print(f"[ERROR] OpenAI enhancement failed: {e}")
            # Fallback to basic English prompt
            return f"A cinematic view of {user_inputs} in a futuristic city, dramatic lighting, high contrast"

# Example usage
if __name__ == "__main__":
    modifier = PromptModifier()
    tests = [
        ("How will cities look in the future?", "Flying cars between skyscrapers with gardens"),
        ("How will we live in cities?", "People walking on elevated green paths between buildings"),
        ("What will transportation look like?", "Magnetic levitation trains passing through buildings")
    ]
    
    for question, inputs in tests:
        print(f"\nInput: {inputs}")
        print(f"Enhanced: {modifier.enhance_prompt(question, inputs)}")