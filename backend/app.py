from datetime import datetime
import json
import os
from typing import Any, Dict, List, Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx
from pydantic import BaseModel, Field, field_validator
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from google import genai
from urllib.parse import quote
from dateutil.parser import parse

load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
ALGORITHMS = ["RS256"]

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class Auth0User(BaseModel):
    sub: str
    name: Optional[str] = None
    email: Optional[str] = None

class CalendarEvent(BaseModel):
    event_name: str
    google_calendar_link: str

class Transcript(BaseModel):
    text: str = Field(..., min_length=10, description="Transcript text (min 10 chars)")
    appointment_id: str = Field(..., description="Appointment ID")

class Note(BaseModel):
    text: str = Field(..., description="AI-generated summary")
    events: List[CalendarEvent]
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

class AppointmentWithID(BaseModel):
    user_id: str = Field(..., description="User ID")
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

# MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_URI = os.getenv("MONGODB_URI") or "mongodb+srv://a1yin:HY8Xwpmq3cg51Stu@cluster0.konpzhu.mongodb.net/?retryWrites=true&w=majority&tls=true"
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

security = HTTPBearer()

async def get_jwks():
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_url)
        return response.json()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    # In a production environment, you would:
    # 1. Verify the token signature using the JWKS from Auth0
    # 2. Check the token claims (iss, aud, exp, etc.)
    # For simplicity, we'll just call Auth0's userinfo endpoint here
    
    userinfo_url = f"https://{AUTH0_DOMAIN}/userinfo"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(userinfo_url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
async def generate_summary(text: str, date) -> dict:
    """Send text to Gemini and get structured summary"""
    try:
        prompt = f"""
        You are a medical scribe AI summarizing a doctor-patient conversation into a clear, actionable note designed for the patient written in markdown. 
        Follow these guidelines:

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

        Example Output for Summary:
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

        4. Extract ALL date/time information with these rules:
        - Default to Pacific Time (America/Los_Angeles) if no timezone specified
        - For medication times:
            * First dose between 7AM-9AM local time
            * Subsequent doses at reasonable hours (7AM-9PM)
        - For appointments:
            * Normal clinic hours (8AM-6PM)
        - Never suggest times between 10PM-6AM
        - The appointment date is {date}, all times are to be AFTER the appointment date
        2. Return structured JSON with:
        {{
        "summary": "formatted markdown",
        "calendar_events": [
            {{
            "title": "event name",
            "start": "ISO8601 datetime",  // MUST be reasonable hour
            "end": "ISO8601 datetime",    // Start + duration
            "recurrence": "RRULE string", // For repeating events
            "timezone": "America/Los_Angeles", // Enforced default
            "description": "full details",
            "time_constraints": {{        // Added field
                "earliest": "07:00",       // 7AM
                "latest": "21:00"          // 9PM
            }},
            "medication_details": {{      // ONLY for medications
                "dose": "500mg",
                "frequency": "every day",
                "duration": "7 days",
                "preferred_times": ["07:00", "15:00", "23:00"] // Adjusted to reasonable hours
            }}
            }}
        ]
        }}

        IMPORTANT RULES:
        1. NEVER suggest times between 10PM-6AM for any event
        2. First medication dose between 7-9AM
        3. Appointments only between 8AM-6PM
        4. All times MUST be in ISO8601 with timezone

        Now summarize this conversation for the patient:
        {text}
        """
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )

        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

def create_gcal_link(event: dict) -> str:
    base_url = "https://calendar.google.com/calendar/u/0/r/eventedit"
    
    start = parse(event["start"]).strftime('%Y%m%dT%H%M%S')
    end = parse(event["end"]).strftime('%Y%m%dT%H%M%S')

    description = event['description']
    
    if "medication_details" in event and event['medication_details'] is not None:
        med = event.get("medication_details", {})
        description = (
            f"MEDICATION:\n"
            f"• Dose: {med.get('dose', '')}\n"
            f"• Frequency: {med.get('frequency', '')}\n"
            f"• Duration: {med.get('duration', '')}\n\n"
        )
    
    params = {
        'text': event["title"],
        'dates': f"{start}/{end}",
        'details': description,
        'location': event.get("location", ""),
        'ctz': event.get("timezone", "UTC"),
        'recur': event.get("recurrence", "")
    }
    
    # Filter empty params and create URL
    query = '&'.join(f"{k}={quote(v)}" for k,v in params.items() if v)
    return f"{base_url}?{query}"

def parse_gemini_response(response: str) -> Dict[str, Any]:
    try:
        # 1. Extract the text content from the response
        response_text = response
        
        # 2. Clean the response text
        # Remove markdown code block markers if present
        if response_text.startswith('```json'):
            json_str = response_text[7:-3].strip()  # Remove ```json and trailing ```
        elif response_text.startswith('```'):
            json_str = response_text[3:-3].strip()  # Remove ``` and trailing ```
        else:
            json_str = response_text.strip()
        
        # 3. Parse the JSON
        return json.loads(json_str)
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}. Content: {json_str}")
    except AttributeError as e:
        raise ValueError(f"Unexpected response format: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to parse Gemini response: {str(e)}")
    
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/appointments", response_model=list[dict])
async def get_all_appointments(user: dict = Depends(verify_token)):
    try:
        appointments = db["appointments"].find(
            {"user_id": user["sub"]},  # Only get appointments for this user
            {"date": 1, "name": 1}
        )
        
        appointment_list = []
        for appointment in appointments:
            appointment["_id"] = str(appointment["_id"])
            appointment_list.append(appointment)
            
        return appointment_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/appointments", response_model=dict)
async def create_appointment(appointment: Appointment, user: dict = Depends(verify_token)):
    try:
        appointment_data = appointment.model_dump()
        appointment_data["user_id"] = user["sub"]
        
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

        gemini_response = await generate_summary(transcript.text, appointment['date'])

        result = parse_gemini_response(gemini_response)
        print(result)

        events_with_links = []
        for event in result.get("calendar_events", []):
            gcal_link = create_gcal_link(event)
            calendar_event = CalendarEvent(
                event_name=event["title"],
                google_calendar_link=gcal_link
            )
            events_with_links.append(calendar_event.model_dump())
        
        # Embed links in summary text
        summary_with_links = result["summary"]
        for event in events_with_links:
            summary_with_links += f"\n\n[Add '{event['event_name']}' to Calendar]({event['google_calendar_link']})"    

        note_data = {
            "text": summary_with_links,
            "events": events_with_links,
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
