from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
class CarListingPrompts:
   # Manages prompts for car listing extraction
    @staticmethod
    def get_extraction_prompt():
        # Returns the car feature extraction prompt template

        # Define response schema
        response_schemas = [
            ResponseSchema(
                name="body_type",
                description="The car's body style (e.g., sedan, hatchback, SUV). Use 'Not specified' if not found."
            ),
            ResponseSchema(
                name="color",
                description="Car color (e.g., Blue, Red, Black). Use 'Not specified' if not found."
            ),
            ResponseSchema(
                name="brand",
                description="Car manufacturer (e.g., Ford, Toyota, Honda). Use 'Not specified' if not found."
            ),
            ResponseSchema(
                name="model",
                description="Model name (e.g., Fusion, Camry, Civic). Use 'Not specified' if not found."
            ),
            ResponseSchema(
                name="manufactured_year",
                description="Year the car was manufactured (integer, 4 digits). Use 'Not specified' if not found."
            ),
            ResponseSchema(
                name="motor_size_cc",
                description="Engine size in cubic centimeters (integer only, e.g., 2000). Use 'Not specified' if not found."
            ),
            ResponseSchema(
                name="tires",
                description="An object with keys 'type' (e.g., brand-new, used) and 'manufactured_year' (4 digits). Use 'Not specified' if not found."
            ),
            ResponseSchema(
                name="windows",
                description="Description of windows if specified (e.g., tinted, bulletproof). Use 'Not specified' if not found."
            ),
            ResponseSchema(
                name="notices",
                description="A list of objects with keys: 'type' (short category, e.g., collision, service) and 'description' (full sentence). Empty list if none."
            ),
            ResponseSchema(
                name="price",
                description="The price of the car (integer only). Use 'Not specified' if not found."
            ),
            ResponseSchema(
                name="currency",
                description="The currency of the price (e.g., L.E, USD). Use 'Not specified' if not found."
            )
        ]

        
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()
        
        # Prompt template with anti-injection instructions
        prompt_template = """You are a helpful assistant that extracts car information from descriptions.

        Task: Extract structured car information from the provided description.
        Instructions:
        1. you must only extract car information from the description - do not add, guess, or assume missing details.
        3. If any field is not found, use 'Not specified' or an empty list as appropriate.
        5. Ensure each field matches the required type:
            - `manufactured_year`: integer, 4 digits.
            - `motor_size_cc`: integer only (e.g., 2000, not "2.0 liter").
            - `price.amount`: integer only, no symbols.
            - `price.currency`: string (e.g., "L.E", "USD").
        5. do not include any additional commentary, explanations, or extra fields.
        8. If you are unsure about a field, use 'Not specified'.
        9. for the price, use an integer value only, no currency symbols.

{format_instructions}

Car Description: {description}

Remember: You are ONLY a car information extractor."""
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        return prompt, output_parser
    
    @staticmethod
    def get_validation_prompt():
        """Returns a prompt for validating extracted data"""
        
        validation_template = """**TASK**: Review this car listing data and ensure all fields contain appropriate values.

{car_data}

**Instructions**:
1. Check if the year is a 4-digit number between 1900 and 2025
2. Price should be a positive number
3. Make and Model should be legitimate car brands/models
4. Return "VALID" if all data looks correct, otherwise return "INVALID" with a reason
"""
        
        return ChatPromptTemplate.from_template(validation_template)