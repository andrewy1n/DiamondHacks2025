from datetime import datetime
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from google import genai

load_dotenv()

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class Transcript(BaseModel):
    text: str = Field(..., min_length=10, description="Transcript text (min 10 chars)")
    appointment_id: str = Field(..., description="Appointment ID")

class Note(BaseModel):
    text: str = Field(..., description="AI-generated summary")
    appointment_id: str = Field(..., description="Appointment ID")

class Appointment(BaseModel):
    date: str = Field(..., description="Appointment datetime with timezone", examples=["2024-06-30T20:55:05.926275+00:00"])
    name: str = Field(..., min_length=2, description="Appointment name")
    note_id: Optional[str] = Field(None, description="Reference to generated note")
    transcript_id: Optional[str] = Field(None, description="Reference to transcript")

    @field_validator('date', mode='before')
    def convert_to_iso(cls, v):
        if isinstance(v, dict) and '$date' in v:
            return v['$date']
        if isinstance(v, datetime):
            return v.isoformat()
        return v

class AppointmentUpdate(BaseModel):
    date: Optional[str] = Field(None, description="Appointment datetime with timezone", examples=["2024-06-30T20:55:05.926275+00:00"])
    name: Optional[str] = Field(..., min_length=2, description="Appointment name")

    @field_validator('date', mode='before')
    def convert_to_iso(cls, v):
        if isinstance(v, dict) and '$date' in v:
            return v['$date']
        if isinstance(v, datetime):
            return v.isoformat()
        return v

MONGODB_URI = os.getenv("MONGODB_URI")
try:
    client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
    # Test the connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"MongoDB connection error: {e}")
    raise

app = FastAPI()
db = client["DiamondHacks2025"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def generate_summary(text: str) -> dict:
    """Send text to Gemini and get structured summary"""
    try:
        prompt = f"""
        You are a medical scribe AI summarizing a doctor-patient conversation into a clear, actionable note designed for the patient. Follow these guidelines:

        1. Patient-First Focus:
        Avoid medical jargon (e.g., say "high blood pressure" instead of "hypertension" unless the term was used in the conversation).

        Emphasize takeaways: What the patient should know/do next.

        Include questions the patient asked (and answers given) if relevant.

        2. Structure:
        Summary of Your Visit

        What We Discussed: [2-3 sentences on main concerns, in the patient’s words if possible]

        Key Findings: [Doctor’s observations or test results, simplified]

        Next Steps: [Bullet points of actions for the patient, e.g., medications, tests, lifestyle changes]

        Your Questions Answered: [List any Q&A from the conversation]

        Follow-Up: [Date/time, reason for next visit]

        3. Tone & Style:
        Warm but professional (e.g., "Your doctor suggested..." instead of "The clinician recommends...").

        Highlight uncertainties (e.g., "Your doctor wants to rule out..." instead of "Differential diagnosis includes...").

        Bold important details (e.g., "Start taking ibuprofen as needed for pain.").

        Example Output:
        Summary of Your Visit

        What We Discussed: You reported fatigue and headaches over the past 2 weeks. Your doctor reviewed your blood pressure logs and asked about your sleep habits.
        Key Findings: Your blood pressure is slightly elevated (142/88). No signs of infection were found.
        Next Steps:
        Take: Low-dose aspirin every morning (starting tomorrow).
        Avoid: Caffeine after 2 PM to improve sleep.
        Schedule: Blood test at LabCorp before your next visit.
        Your Questions Answered:
        You asked: "Could this be stress-related?"
        Doctor said: "Yes, but we’ll check your labs to be sure."
        Follow-Up: June 5th to review test results and adjust treatment if needed.
        Now summarize this conversation for the patient:
        {text}
        """
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )

        print(response.text)

        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
    
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/appointments", response_model=list[dict])
async def get_all_appointments():
    try:
        # Project only the fields we want to return
        appointments = db["appointments"].find(
            {},
            {"date": 1, "name": 1}
        )
        
        # Convert to list and add string version of _id
        appointment_list = []
        for appointment in appointments:
            appointment["_id"] = str(appointment["_id"])
            appointment_list.append(appointment)
            
        return appointment_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/appointments", response_model=Appointment)
async def create_appointment(appointment: Appointment):
    try:
        appointment_data = appointment.model_dump()
        
        result = db["appointments"].insert_one(appointment_data)
        new_appointment = db["appointments"].find_one({"_id": result.inserted_id})
        new_appointment["_id"] = str(new_appointment["_id"])
        return new_appointment
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/appointments/{app_id}", response_model=Appointment)
async def get_appointment(app_id: str):
    try:
        appointment = db["appointments"].find_one({"_id": ObjectId(app_id)})
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        appointment["_id"] = str(appointment["_id"])
        
        return appointment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.patch("/appointments/{app_id}", response_model=Appointment)
async def update_appointment(app_id: str, update_data: AppointmentUpdate):
    try:
        update_fields = {}
        if update_data.date is not None:
            update_fields["date"] = update_data.date
        if update_data.name is not None:
            update_fields["name"] = update_data.name
            
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        result = db["appointments"].update_one(
            {"_id": ObjectId(app_id)},
            {"$set": update_fields}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Appointment not found or no changes made")
        
        appointment = db["appointments"].find_one({"_id": ObjectId(app_id)})
        appointment["_id"] = str(appointment["_id"])
        return appointment
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/transcript")
async def process_transcript(transcript: Transcript):
    try:
        appointment = db["appointments"].find_one({"_id": ObjectId(transcript.appointment_id)})
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        transcript_data = transcript.model_dump()
        transcript_result = db["transcripts"].insert_one(transcript_data)

        gemini_response = await generate_summary(transcript.text)

        note_data = {
            "text": gemini_response,
            "appointment_id": transcript.appointment_id
        }
        note_result = db["notes"].insert_one(note_data)

        db["appointments"].update_one(
            {"_id": ObjectId(transcript.appointment_id)},
            {"$set": {
                "transcript_id": str(transcript_result.inserted_id),
                "note_id": str(note_result.inserted_id)
            }}
        )

        return {
            "transcript_id": str(transcript_result.inserted_id),
            "note_id": str(note_result.inserted_id),
            "appointment_id": transcript.appointment_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/transcript/{transcript_id}")
async def get_transcript(transcript_id: str):
    try:
        transcript = db["transcripts"].find_one({"_id": ObjectId(transcript_id)})
        if not transcript:
            raise HTTPException(status_code=404, detail="Transcript not found")
        transcript["_id"] = str(transcript["_id"])
        return transcript
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/note/{note_id}")
async def get_note(note_id: str):
    try:
        note = db["notes"].find_one({"_id": ObjectId(note_id)})
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        note["_id"] = str(note["_id"])
        return note
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
