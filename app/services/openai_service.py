# app/services/openai_service.py
import openai
from .realtime_service import RealtimeAPI
import threading
from sqlalchemy.orm import Session
from app.models import ScheduledCall
import logging

logger = logging.getLogger(__name__)


def generate_ai_message(persona: str, scenario: str, user_input: str) -> str:
    """
    Generates a response from OpenAI's ChatGPT based on user input.

    Args:
        persona (str): The persona of the AI.
        scenario (str): The scenario context for the conversation.
        user_input (str): The input from the user.

    Returns:
        str: The AI-generated response.
    """
    prompt = f"You are {persona}. {scenario}. User says: {user_input}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}  # Use dynamic user input
            ],
            max_tokens=150
        )
        ai_message = response.choices[0].message.content.strip()
        return ai_message
    except Exception as e:
        print(f"Error generating AI message: {e}")
        return "I'm sorry, I couldn't process your request at this time."


def make_call(user_phone_number: str, persona: str, scenario: str, call_id: int):
    db = Session()
    try:
        user_input = "Hello, can you help me?"  # Default input for testing

        # Initialize the Realtime API
        realtime_api = RealtimeAPI(api_key=OPENAI_API_KEY)
        threading.Thread(target=realtime_api.start_connection).start()

        # Send user message to the Realtime API
        realtime_api.send_user_message(user_input)

        # Handle the response in the on_message method of RealtimeAPI
        # You can also implement additional logic to handle audio responses here

        # Update call status to 'Completed'
        call_record = db.query(ScheduledCall).filter(
            ScheduledCall.id == call_id).first()
        if call_record:
            call_record.status = "Completed"
            db.commit()
            logger.info(f"Call ID {call_id} status updated to Completed")
    except Exception as e:
        logger.error(f"Error making call ID {call_id}: {e}")
        # Update call status to 'Failed'
        call_record = db.query(ScheduledCall).filter(
            ScheduledCall.id == call_id).first()
        if call_record:
            call_record.status = "Failed"
            db.commit()
            logger.info(f"Call ID {call_id} status updated to Failed")
    finally:
        db.close()
