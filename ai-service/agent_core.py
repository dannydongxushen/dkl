# ai-service/agent_core.py
import os
import sys
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from llm import llm_instance
from rag_engine import rag_engine_instance
from agent_prompts import build_system_prompt
from tool_schemas import TOOLS
# 修复 Pylance 报错：从 backend 包中导入 database 模块
from backend import database

def execute_tool(tool_name: str, args: dict, current_patient_id: str) -> str:
    if tool_name == "search_clinical_knowledge":
        query = args.get("query", "")
        if not query:
            return "No query provided."
        docs = rag_engine_instance.search(query)
        if not docs:
            return "No relevant information found."
        return "\n\n".join([d["text"] for d in docs])
        
    elif tool_name == "get_patient_bookings":
        pid = args.get("patient_id", current_patient_id)
        bookings = database.get_patient_bookings(pid)
        if not bookings:
            return "No bookings found."
        return json.dumps(bookings)
        
    elif tool_name == "create_booking":
        doc_id = args.get("doctor_id", "")
        treat_id = args.get("treatment_id", "")
        date = args.get("booking_date", "")
        time = args.get("booking_time", "")
        
        if not all([doc_id, treat_id, date, time]):
            return "Missing required booking parameters."
            
        return database.create_booking(
            patient_id=current_patient_id,
            doctor_id=doc_id,
            treatment_id=treat_id,
            booking_date=date,
            booking_time=time
        )
            
    return "Unknown tool."

def process_message(messages: list, patient_id: str = "P001") -> str:
    patient_ctx = database.get_patient_context(patient_id)
    
    # 获取今天的真实日期，注入给大模型
    current_date_str = datetime.now().strftime("%Y-%m-%d")
    
    system_prompt = build_system_prompt(
        patient_id=patient_ctx["id"],
        patient_name=patient_ctx["name"],
        patient_allergies=patient_ctx["allergies"],
        current_date=current_date_str
    )
    
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    
    while True:
        response = llm_instance.chat(messages=full_messages, tools=TOOLS)
        response_message = response.choices[0].message
        
        if not response_message.tool_calls:
            return response_message.content
            
        full_messages.append(response_message)
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            try:
                function_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                function_args = {}
                
            tool_result = execute_tool(function_name, function_args, patient_ctx["id"])
            
            full_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": tool_result
            })