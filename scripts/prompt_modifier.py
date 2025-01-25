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
            system_prompt = """You are an expert art director specializing in cinematic architectural visualization.
            Transform user descriptions into vivid, aesthetic scenes by:
            1. Interpreting metaphors and abstract concepts into visual elements
            2. Adding dramatic architectural elements that complement the core idea
            3. Creating layered lighting scenarios (ambient, accent, and feature lighting)
            4. Incorporating elegant materials (glass, brushed metal, polished stone)
            5. Using rich atmospheric effects (mist, reflections, light beams)
            6. Maintaining balanced composition with clear focal points
            7. Including subtle color harmonies while keeping high contrast
            
            Key guidelines:
            - Transform simple descriptions into rich visual narratives
            - Keep architectural elements as elegant framing devices
            - Use lighting as a story-telling element
            - Maintain a cinematic quality suitable for art installations
            - Create depth through layered elements
            
            Format as a single, flowing paragraph focused on visual description.
            Emphasize the poetry and beauty in the scene while keeping it architecturally grounded."""
            
            context_prompt = f"""
            Context question: {question}
            User description: {user_inputs}
            
            Create a DALL-E 3 optimized prompt that considers and interprets these elements into a cinematic architectural visualization.
            Focus on creating a dramatic, high-contrast scene that would work well for a light installation.
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