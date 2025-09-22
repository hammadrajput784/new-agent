import uvicorn
import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse

# agent.py se app ko import karein
from .agent import app as agent_app  
from .tools import populate_db_with_mock_data, get_total_students, get_students_by_department, list_students, get_student

app = FastAPI(
    title="AI Campus Admin Agent API",
    description="A FastAPI server for the AI Campus Admin Agent.",
    version="1.0.0",
)

# Start up event to populate the database
@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    populate_db_with_mock_data()

# --- Sync Chat Endpoint ---
@app.post("/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message")
        
        if not user_message:
            return JSONResponse(status_code=400, content={"error": "Message is required."})

        # LangGraph app ko invoke karein
        config = {"configurable": {"thread_id": "1"}}  # Simple thread ID for memory
        inputs = {"messages": [("human", user_message)]}
        result = agent_app.invoke(inputs, config=config)
        
        final_message = result['messages'][-1].content
        return {"response": final_message}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# --- Streaming Chat Endpoint ---
@app.post("/chat/stream")
async def chat_stream_endpoint(request: Request):
    data = await request.json()
    user_message = data.get("message")

    async def event_generator():
        config = {"configurable": {"thread_id": "1"}}
        inputs = {"messages": [("human", user_message)]}

        async for event in agent_app.astream_events(inputs, config=config, version="v1"):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                token = event["data"]["chunk"]
                if token.content:
                    yield f"data: {json.dumps({'token': token.content})}\n\n"
            elif kind == "on_tool_end":
                output = str(event["data"]["output"])
                yield f"data: {json.dumps({'tool_output': output})}\n\n"
            elif kind == "on_end":
                yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- Analytics Endpoint ---
@app.get("/analytics")
def get_analytics():
    total_students = get_total_students()
    students_by_dept = get_students_by_department()

    analytics_data = {
        "total_students": total_students,
        "students_by_department": students_by_dept,
    }
    return JSONResponse(content=analytics_data)

# --- Students CRUD Endpoints (Optional but useful for testing) ---
@app.get("/students")
def get_all_students():
    return JSONResponse(content=json.loads(list_students()))

@app.get("/students/{student_id}")
def get_student_by_id(student_id: str):
    student = get_student(student_id)
    if student.startswith("Error"):
        return JSONResponse(status_code=404, content={"error": student})
    return JSONResponse(content=json.loads(student))

# --- Additional Campus Information Endpoints ---
@app.get("/campus/cafeteria")
def get_cafeteria_info():
    from .tools import get_cafeteria_timings
    return JSONResponse(content={"timings": get_cafeteria_timings()})

@app.get("/campus/library")
def get_library_info():
    from .tools import get_library_hours
    return JSONResponse(content={"hours": get_library_hours()})

@app.get("/campus/events")
def get_events():
    from .tools import get_event_schedule
    return JSONResponse(content={"events": get_event_schedule()})

# --- Student Management Endpoints ---
@app.post("/students")
async def add_new_student(request: Request):
    try:
        data = await request.json()
        from .tools import add_student
        result = add_student(
            data.get("name"), 
            data.get("department"), 
            data.get("year"), 
            data.get("email")
        )
        if result.startswith("Error"):
            return JSONResponse(status_code=400, content={"error": result})
        return JSONResponse(status_code=201, content=json.loads(result))
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.put("/students/{student_id}")
async def update_student_info(student_id: str, request: Request):
    try:
        data = await request.json()
        from .tools import update_student
        result = update_student(
            student_id,
            data.get("name"), 
            data.get("department"), 
            data.get("year"), 
            data.get("email")
        )
        if result.startswith("Error"):
            return JSONResponse(status_code=404, content={"error": result})
        return JSONResponse(content=json.loads(result))
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.delete("/students/{student_id}")
def delete_student_record(student_id: str):
    from .tools import delete_student
    result = delete_student(student_id)
    if result.startswith("Error"):
        return JSONResponse(status_code=404, content={"error": result})
    return JSONResponse(content={"message": result})

# --- Advanced Analytics Endpoints ---
@app.get("/analytics/recent-onboarded")
def get_recent_onboarded():
    from .tools import get_recent_onboarded_students
    return JSONResponse(content={"recent_students": json.loads(get_recent_onboarded_students())})

@app.get("/analytics/active-students")
def get_active_students():
    from .tools import get_active_students_last_7_days
    return JSONResponse(content={"active_students": json.loads(get_active_students_last_7_days())})

# --- Communication Endpoints ---
@app.post("/communication/email")
async def send_email_to_student(request: Request):
    try:
        data = await request.json()
        from .tools import send_email
        result = send_email(
            data.get("student_id"),
            data.get("subject"),
            data.get("body")
        )
        if result.startswith("Error"):
            return JSONResponse(status_code=400, content={"error": result})
        return JSONResponse(content={"message": result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
