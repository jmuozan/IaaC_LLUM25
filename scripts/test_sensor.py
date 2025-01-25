from text_sensor import AITextSensor
import os

def test_text_sensor():
    # Ensure API key is set
    if not os.getenv('OPENAI_API_KEY'):
        api_key = input("Please enter your OpenAI API key: ")
        os.environ['OPENAI_API_KEY'] = api_key

    sensor = AITextSensor()
    print("Text Sensor Test Tool")
    print("Type 'quit' to exit")
    print("-" * 50)

    while True:
        text = input("\nEnter text to test: ")
        if text.lower() == 'quit':
            break

        # Get detailed analysis
        details = sensor.get_content_details(text)
        censored_text = sensor.censor_text(text)

        print("\nResults:")
        print("Categories flagged:")
        for category, flagged in details.items():
            print(f"- {category}: {'🚫 YES' if flagged else '✅ NO'}")
        print(f"\nCensored version: {censored_text}")
        print("-" * 50)

if __name__ == "__main__":
    test_text_sensor()