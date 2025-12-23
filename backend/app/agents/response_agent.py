"""
Response Agent - Generates personalized responses to complaints
"""
from typing import Any, Dict, List
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.base_agent import BaseAgent, RateLimitError
import json


class ResponseAgent(BaseAgent):
    """Agent responsible for generating personalized responses to complaints."""
    
    TONE_GUIDELINES = {
        "angry": "Be extremely empathetic, acknowledge their frustration explicitly, apologize sincerely, and focus on immediate resolution. Use phrases like 'I completely understand your frustration' and 'You have every right to be upset'.",
        "frustrated": "Be understanding and patient, acknowledge the inconvenience, and clearly outline the steps being taken to resolve the issue.",
        "neutral": "Be professional and helpful, provide clear information, and offer assistance.",
        "positive": "Be warm and appreciative, thank them for their feedback, and continue the positive interaction."
    }
    
    def __init__(self):
        super().__init__(name="ResponseAgent", model="gemini-2.0-flash")
        
        self.system_prompt = """You are an expert customer service representative crafting responses to complaints.
Your responses should be empathetic, professional, and solution-focused.

Guidelines:
1. Always acknowledge the customer's feelings first
2. Take responsibility (don't blame the customer or make excuses)
3. Provide specific actions being taken
4. Include clear next steps
5. End with a commitment to resolution

Return a JSON object with:
{{
    "greeting": "personalized greeting",
    "acknowledgment": "acknowledgment of the issue and empathy",
    "explanation": "brief explanation if needed (no excuses)",
    "actions": ["list of specific actions being taken"],
    "next_steps": "what happens next",
    "closing": "professional closing with commitment",
    "full_response": "the complete formatted response",
    "recommended_actions": ["internal actions for the team"],
    "tone": "the tone used",
    "confidence": 0.0 to 1.0
}}

Return ONLY valid JSON."""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized response to the complaint.
        
        Args:
            input_data: Dict containing:
                - normalized_text: The complaint text
                - classification: Classification results
                - priority: Priority assessment
                - customer_context: Customer history and profile
                - iteration: Current iteration number (for re-generation)
                - previous_feedback: Feedback from validator (if re-generating)
        
        Returns:
            Generated response with recommended actions
        """
        normalized_text = input_data.get("normalized_text", "")
        classification = input_data.get("classification", {})
        priority = input_data.get("priority", {})
        customer_context = input_data.get("customer_context", {})
        iteration = input_data.get("iteration", 1)
        previous_feedback = input_data.get("previous_feedback", "")
        
        # Get tone guidelines based on sentiment
        sentiment = classification.get("sentiment", "neutral")
        tone_guide = self.TONE_GUIDELINES.get(sentiment, self.TONE_GUIDELINES["neutral"])
        
        # Build customer info string
        customer_profile = customer_context.get("customer_profile", {})
        customer_name = customer_profile.get("name", "Valued Customer")
        customer_tier = customer_profile.get("tier", "Standard")
        
        # Build context for response generation
        context_parts = [
            f"Customer Name: {customer_name}",
            f"Customer Tier: {customer_tier}",
            f"Complaint Category: {classification.get('primary_category', 'General')}",
            f"Customer Sentiment: {sentiment}",
            f"Priority Level: {priority.get('level', 'medium')}",
            f"Key Issues: {', '.join(classification.get('key_issues', ['general concern']))}",
        ]
        
        # Add complaint history context
        complaint_metrics = customer_context.get("complaint_metrics", {})
        if complaint_metrics.get("total_complaints", 0) > 1:
            context_parts.append(f"Note: This is their {complaint_metrics['total_complaints'] + 1}th contact")
        
        # Add open complaints context
        open_complaints = customer_context.get("open_complaints", [])
        if open_complaints:
            context_parts.append(f"Note: Customer has {len(open_complaints)} open complaint(s)")
        
        # Add re-generation context
        if iteration > 1 and previous_feedback:
            context_parts.append(f"\n⚠️ IMPORTANT - Previous response was rejected. Feedback: {previous_feedback}")
            context_parts.append("Please address the feedback in this revised response.")
        
        context_str = "\n".join(context_parts)
        
        # Build the prompt
        prompt = f"""Tone Guidelines: {tone_guide}

Customer Context:
{context_str}

Original Complaint:
{normalized_text}

Generate an appropriate response following the JSON format specified."""

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        ai_used = False
        try:
            response = await self.invoke_with_retry(messages)
            result = json.loads(response.content)
            ai_used = True
        except (RateLimitError, json.JSONDecodeError, Exception):
            # Fallback response using templates
            result = self._generate_fallback_response(customer_name, sentiment, classification, priority)
        
        # Ensure full_response exists
        if not result.get("full_response"):
            parts = [
                result.get("greeting", f"Dear {customer_name},"),
                "",
                result.get("acknowledgment", ""),
                "",
                result.get("explanation", ""),
                "",
                "Actions we're taking:",
                *[f"• {action}" for action in result.get("actions", [])],
                "",
                result.get("next_steps", ""),
                "",
                result.get("closing", "Best regards,\nCustomer Support Team")
            ]
            result["full_response"] = "\n".join(parts)
        
        return {
            "draft_response": result.get("full_response", ""),
            "response_parts": {
                "greeting": result.get("greeting", ""),
                "acknowledgment": result.get("acknowledgment", ""),
                "explanation": result.get("explanation", ""),
                "actions": result.get("actions", []),
                "next_steps": result.get("next_steps", ""),
                "closing": result.get("closing", "")
            },
            "recommended_actions": result.get("recommended_actions", []),
            "tone": result.get("tone", sentiment),
            "iteration": iteration,
            "confidence": result.get("confidence", 0.7),
            "ai_processed": ai_used
        }

    def _generate_fallback_response(self, customer_name: str, sentiment: str, classification: Dict, priority: Dict) -> Dict:
        """Generate a template-based response when AI is unavailable."""
        category = classification.get("primary_category", "General")
        priority_level = priority.get("level", "medium")
        
        # Select acknowledgment based on sentiment
        acknowledgments = {
            "angry": "We sincerely apologize for this experience. We completely understand your frustration and take this matter very seriously.",
            "frustrated": "We apologize for the inconvenience you've experienced. We understand how frustrating this must be.",
            "neutral": "Thank you for contacting us. We appreciate you bringing this to our attention.",
            "positive": "Thank you for your feedback! We're glad to hear from you."
        }
        
        # Category-specific actions
        category_actions = {
            "Shipping": ["Tracking your order status", "Contacting our shipping partner", "Expediting delivery if possible"],
            "Billing": ["Reviewing your account", "Investigating the billing discrepancy", "Processing any necessary adjustments"],
            "Product": ["Documenting the product issue", "Arranging for replacement or refund", "Escalating to our quality team"],
            "Technical": ["Creating a support ticket", "Assigning a technical specialist", "Investigating the issue"],
            "Service": ["Reviewing the interaction", "Following up with the team involved", "Implementing service improvements"],
        }
        
        actions = category_actions.get(category, ["Reviewing your case", "Assigning to the appropriate team"])
        
        # Build the response
        greeting = f"Dear {customer_name},"
        acknowledgment = acknowledgments.get(sentiment, acknowledgments["neutral"])
        next_steps = "You will receive an update within 24 hours." if priority_level in ["high", "critical"] else "You will receive an update within 48 hours."
        closing = "We value your business and are committed to resolving this matter to your satisfaction.\n\nBest regards,\nCustomer Support Team"
        
        full_response = f"""{greeting}

{acknowledgment}

We are taking the following actions:
{chr(10).join(f'• {action}' for action in actions)}

{next_steps}

{closing}"""
        
        return {
            "greeting": greeting,
            "acknowledgment": acknowledgment,
            "explanation": "",
            "actions": actions,
            "next_steps": next_steps,
            "closing": closing,
            "full_response": full_response,
            "recommended_actions": ["Review complaint details", "Follow up with customer"],
            "tone": sentiment,
            "confidence": 0.65
        }
