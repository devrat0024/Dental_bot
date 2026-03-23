import re

class TriageHandler:
    @staticmethod
    def process(query: str, state: dict) -> dict:
        q_lower = query.lower()
        current_step = state.get("step", "INIT")
        data = state.get("data", {})
        
        # 1. Parsing and State Advancement
        if current_step == "INIT":
            if any(word in q_lower for word in ["pain", "hurt", "ache", "emergency", "problem", "broken", "bleeding"]):
                state["step"] = "SEVERITY_DURATION"
                return {
                    "answer": "I'm sorry to hear that you're experiencing dental discomfort. To help me understand better, **on a scale of 1 to 10, how severe is the pain, and how long has it been bothering you?**",
                    "new_state": state
                }
            return None # Not a triage case
            
        elif current_step == "SEVERITY_DURATION":
            # Extract severity
            nums = re.findall(r'\d+', q_lower)
            if nums:
                data["severity"] = int(nums[0])
            data["duration_input"] = query
            state["step"] = "SYMPTOMS"
            state["data"] = data
            return {
                "answer": "Thank you. **Are you also experiencing any swelling, bleeding, or is the tooth physically broken?**",
                "new_state": state
            }
            
        elif current_step == "SYMPTOMS":
            data["symptoms_input"] = query
            data["has_swelling"] = "swell" in q_lower or "yes" in q_lower
            data["has_bleeding"] = "bleed" in q_lower or "yes" in q_lower
            data["is_broken"] = "broken" in q_lower or "yes" in q_lower
            state["step"] = "HISTORY_CAUSE"
            state["data"] = data
            return {
                "answer": "I understand. **Did this happen after a recent injury or trauma, or do you notice any visible holes (cavities) in the tooth?**",
                "new_state": state
            }
            
        elif current_step == "HISTORY_CAUSE":
            data["history_input"] = query
            data["has_injury"] = "injury" in q_lower or "trauma" in q_lower or "hit" in q_lower
            data["has_cavity"] = "hole" in q_lower or "cavity" in q_lower
            state["step"] = "COMPLETED"
            state["data"] = data
            return {
                "answer": "Thank you for sharing all those details. Let me summarize everything and provide the best guidance from our clinical records.",
                "new_state": state,
                "trigger_final": True
            }
            
        return None

class ResponseGenerator:
    def __init__(self):
        self.triage = TriageHandler()

    def generate(self, query: str, retrieved_chunks: list, state: dict = None) -> dict:
        q_lower = query.lower()
        
        # 0. Triage Handling
        if state and state.get("step") != "COMPLETED":
            triage_result = self.triage.process(query, state)
            if triage_result:
                # If triage reaches COMPLETED in this turn, we proceed to final summary
                if not triage_result.get("trigger_final"):
                    return {
                        "answer": triage_result["answer"],
                        "intent": "triage_question",
                        "new_state": triage_result["new_state"]
                    }
                # Else, state is updated to COMPLETED, and we continue below to generate the final summary
                state = triage_result["new_state"]

        # 1. Intent Detection: Booking
        if any(word in q_lower for word in ["book", "schedule", "appointment", "visit"]):
            return {
                "answer": "I can certainly help you with that! To book an appointment, please provide the **date and time** (e.g., '2024-10-15 at 10:00 AM'). \n\nYou can also use our dedicated **Appointments** tab in the sidebar.",
                "intent": "booking_request"
            }
            
        if not retrieved_chunks:
            return {
                "answer": "I'm sorry, I couldn't find specific information on that in our records. \n\n**Recommendation:** Please consult a licensed dentist for a professional diagnosis. Would you like me to help you book an appointment?",
                "intent": "unknown"
            }
        
        # 2. Multi-Chunk Synthesis Logic
        all_body_parts = []
        sources = set()
        seen_lines = set()

        for chunk in retrieved_chunks:
            content = chunk['text']
            sources.add(chunk['source'])
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or line in seen_lines: continue
                if any(term in line.lower() for term in ["professional tone", "always maintain", "conclude significant", "ai must not", "educational tool only"]):
                    continue
                seen_lines.add(line)
                if line.startswith('##'):
                    all_body_parts.append(f"\n### {line[2:].strip()}\n")
                elif line.startswith('-') or (len(line) > 2 and line[0].isdigit() and line[1] == '.'):
                    content_text = line[2:].strip() if line[1] == '.' else line[1:].strip()
                    all_body_parts.append(f"- {content_text}")
                else:
                    all_body_parts.append(line)

        source_str = ", ".join(sources)
        
        # 3. Final Summary Construction (Triage Aware)
        if state and state.get("step") == "COMPLETED":
            data = state.get("data", {})
            summary_intro = "**Clinical Assessment Summary:**\n\n"
            summary_intro += f"- **Severity:** {data.get('severity', 'Not stated')}/10\n"
            summary_intro += f"- **Duration:** {data.get('duration_input', 'Not stated')}\n"
            
            symptoms = []
            if data.get("has_swelling"): symptoms.append("Swelling")
            if data.get("has_bleeding"): symptoms.append("Bleeding")
            if data.get("is_broken"): symptoms.append("Broken Tooth")
            summary_intro += f"- **Reported Symptoms:** {', '.join(symptoms) if symptoms else 'None immediate'}\n"
            
            history = []
            if data.get("has_injury"): history.append("Recent Injury")
            if data.get("has_cavity"): history.append("Visible Cavity")
            summary_intro += f"- **Potential Cause/History:** {', '.join(history) if history else 'Unknown'}\n\n"
            summary_intro += "---\n\n"
            
            body = "\n".join([f"{part}\n" if not part.startswith('\n') and not part.startswith('-') else part for part in all_body_parts])
            
            # Urgent Greeting for High Pain levels detected in summary
            greeting = "**Professional Guidance for your condition:**"
            if data.get("severity", 0) >= 7:
                greeting = "**⚠️ URGENT: Highly severe pain detected.** Based on your assessment, please review the emergency signs below immediately."
            
            answer = f"{summary_intro}{greeting}\n\n{body}"
            return {"answer": answer, "intent": "triage_summary", "new_state": state}

        # 4. Standard Response (Non-Triage)
        is_procedural = any(word in q_lower for word in ["step", "procedure", "how to", "follow up", "process"])
        if is_procedural:
            body = "\n".join([f"{part}\n" if not part.startswith('\n') and not part.startswith('-') else part for part in all_body_parts])
        else:
            summary = [p for p in all_body_parts if not p.startswith('\n') and not p.startswith('-')][:2]
            body = " ".join(summary)
            if not body: body = all_body_parts[0] if all_body_parts else ""
            
        answer = f"**I'm here to help you.**\n\n{body}"
        return {"answer": answer, "intent": "informational"}
