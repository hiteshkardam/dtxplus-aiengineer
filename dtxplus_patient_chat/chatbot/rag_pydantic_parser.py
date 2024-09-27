from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from typing import Optional
from pydantic import BaseModel, Field, model_validator
from langchain_community.llms import Ollama

# Initialize Langchain model
llm = Ollama(model = "llama3.1:8b-instruct-fp16",temperature = 0.2)

# Define the updated schema
class BloodPressure(BaseModel):
    systolic: Optional[str] = Field(None, description="Systolic blood pressure, or null if not mentioned.")
    diastolic: Optional[str] = Field(None, description="Diastolic blood pressure, or null if not mentioned.")


class VitalSigns(BaseModel):
    heart_rate: Optional[str] = Field(None, description="The patient's heart rate, or null if not mentioned.")
    blood_pressure: BloodPressure

    @model_validator(mode='before')
    def convert_numeric_values(cls, values):
        if isinstance(values.get('heart_rate'), int):
            values['heart_rate'] = str(values['heart_rate'])
        if isinstance(values.get('blood_pressure', {}).get('systolic'), int):
            values['blood_pressure']['systolic'] = str(values['blood_pressure']['systolic'])
        if isinstance(values.get('blood_pressure', {}).get('diastolic'), int):
            values['blood_pressure']['diastolic'] = str(values['blood_pressure']['diastolic'])
        return values


class LabTests(BaseModel):
    blood_sugar: Optional[str] = Field(None, description="The patient's blood sugar level, or null if not mentioned.")
    cholesterol: Optional[str] = Field(None, description="The patient's cholesterol level, or null if not mentioned.")

    @model_validator(mode='before')
    def convert_numeric_values(cls, values):
        if isinstance(values.get('blood_sugar'), int):
            values['blood_sugar'] = str(values['blood_sugar'])
        if isinstance(values.get('cholesterol'), int):
            values['cholesterol'] = str(values['cholesterol'])
        return values


class Medication(BaseModel):
    name: Optional[str] = Field(None, description="The name of the medication, or null if not mentioned.")
    frequency: Optional[str] = Field(None, description="The frequency of medication intake, or null if not mentioned.")


class Appointment(BaseModel):
    date: Optional[str] = Field(None, description="The appointment date, or null if not mentioned.")
    time: Optional[str] = Field(None, description="The appointment time, or null if not mentioned.")


class ExtractedEntities(BaseModel):
    appointment: Appointment
    medication: Medication
    weight: Optional[str] = Field(None, description="The patient's weight, or null if not mentioned.")
    vital_signs: VitalSigns
    lab_tests: LabTests
    doctor_notes: Optional[str] = Field(None, description="The doctor's notes, or null if not mentioned.")

# Create a parser for this schema
parser = PydanticOutputParser(pydantic_object=ExtractedEntities)

prompt = PromptTemplate(
    input_variables=["conversation", "user_data"],
    template="""
    Extract the following entities from the conversation and provide the output in a valid JSON format:
    - Appointment
        - Date
        - Time
    - Weight
    - Medication
        - Name
        - Frequency
    - Lab test report consisting of:
        - Blood Sugar
        - Cholesterol
    - Vital signs such as:
        - Heart Rate
        - Blood Pressure
            - Systolic
            - Diastolic
    - Doctor notes

    If something is not mentioned, return "null". Do not assume or infer anything.
    Remeber, For blood pressure, Systolic is larger than Diastolic.
    The output should be in the following JSON format:
    {{
        "appointment": {{
            "date": "<appointment_date>",
            "time": "<appointment_time>"
        }},
        "medication": {{
            "name": "<medication_name>",
            "frequency": "<medication_frequency>"
        }},
        "weight": "<weight_value>",
        "vital_signs": {{
            "heart_rate": "<heart_rate_value>",
            "blood_pressure": {{
                "systolic": "<systolic_value>",
                "diastolic": "<diastolic_value>"
            }}
        }},
        "lab_tests": {{
            "blood_sugar": "<blood_sugar_value>",
            "cholesterol": "<cholesterol_value>"
        }},
        "doctor_notes": "<doctor_notes>"
    }}
    Patient Details: {user_data}
    Conversation: {conversation}
    """,
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

def parser_for_neo4j(user_message, user_data):
    # Use the prompt with the LLM
    llm_response = llm.invoke(prompt.format(conversation=user_message, user_data=user_data))

    # Parse the response to ensure it matches the schema
    parsed_output = parser.parse(llm_response)
    print(type(parsed_output))
    print(parsed_output)

    return parsed_output