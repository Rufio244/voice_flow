from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import shutil
import datetime

app = FastAPI(title="Voice Flow Full System", version="1.0.0")

# กำหนดเส้นทางโฟลเดอร์สำหรับเก็บข้อมูล
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

templates = Jinja2Templates(directory="templates")

class QueryModel(BaseModel):
    question: str
    transcript: str

class ExportModel(BaseModel):
    type: str
    content: str
    summary: str

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return templates.TemplateResponse("index.html", {"request": {}})

@app.post("/api/process-audio")
async def process_audio(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # ระบบวิเคราะห์และจำลองการถอดเสียง (รองรับการต่อ API ภายนอก เช่น OpenAI Whisper / LLM)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mock_category = "การประชุมเชิงปฏิบัติการ / อภิปราย"
    mock_transcript = f"บันทึกเมื่อ: {timestamp}\nไฟล์: {file.filename}\nเนื้อหาโดยละเอียด: ระบบ Voice Flow ได้ทำการแปลงเสียงพูดเป็นข้อความสำเร็จ พร้อมจำแนกประเภทเนื้อหาและสรุปประเด็นสำคัญให้อัตโนมัติ เพื่อให้ผู้ใช้งานสามารถนำไปตรวจสอบ ถาม-ตอบ และดาวน์โหลดเอกสารไปใช้งานต่อได้อย่างสะดวกรวดเร็ว"
    mock_summary = "สรุปประเด็นสำคัญ:\n1. แปลงเสียงเป็นข้อความอัตโนมัติ\n2. จัดหมวดหมู่เนื้อหาและวิเคราะห์ความหมาย\n3. สร้างเอกสารสรุปผลพร้อมดาวน์โหลดทันที"
    
    return {
        "filename": file.filename,
        "category": mock_category,
        "transcript": mock_transcript,
        "summary": mock_summary
    }

@app.post("/api/ask-content")
async def ask_content(data: QueryModel):
    question = data.question
    answer = f"จากเนื้อหาเสียงที่คุณถามว่า '{question}' ระบบวิเคราะห์แล้วพบว่า เน้นการทำงานแบบอัตโนมัติครบวงจรตั้งแต่อัปโหลด ประมวลผล สรุปผล ไปจนถึงการสร้างเอกสารครับ"
    return {"answer": answer}

@app.post("/api/export-document")
async def export_document(data: ExportModel):
    doc_type = data.get("type", "txt")
    if doc_type not in ["txt", "md"]:
        doc_type = "txt"
        
    file_name = f"VoiceFlow_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{doc_type}"
    file_path = os.path.join(OUTPUT_DIR, file_name)
    
    formatted_content = f"""========================================
       VOICE FLOW - EXECUTIVE SUMMARY
========================================
วันที่สร้างรายงาน: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

[ สรุปสาระสำคัญ ]
{data.summary}

[ ข้อความถอดเสียงทั้งหมด (Transcript) ]
{data.content}
========================================
"""
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(formatted_content)
        
    return {"download_url": f"/api/download/{file_name}"}

@app.get("/api/download/{file_name}")
async def download_file(file_name: str):
    file_path = os.path.join(OUTPUT_DIR, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/octet-stream', filename=file_name)
    raise HTTPException(status_code=404, detail="ไม่พบไฟล์ที่ต้องการดาวน์โหลด")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
