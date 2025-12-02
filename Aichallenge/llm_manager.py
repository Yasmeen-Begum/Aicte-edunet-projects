"""
LLM Manager for summarization
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class LLMManager:
    """Manages summarization using extractive approach"""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.food_recommendations = self._load_food_database()
        self.medication_database = self._load_medication_database()
        self.recovery_time_database = self._load_recovery_time_database()
        logger.info("LLM Manager initialized (using extractive summarization)")
    
    def _load_food_database(self) -> Dict[str, List[str]]:
        """Load food recommendations for various conditions"""
        return {
            "diabetes": [
                "Leafy greens (spinach, kale, collard greens)",
                "Whole grains (brown rice, quinoa, oats)",
                "Fatty fish (salmon, mackerel, sardines)",
                "Nuts and seeds (almonds, walnuts, chia seeds)",
                "Beans and legumes",
                "Greek yogurt (unsweetened)",
                "Berries (blueberries, strawberries)",
                "Avoid: Sugary drinks, white bread, processed foods"
            ],
            "hypertension": [
                "Bananas (high in potassium)",
                "Leafy greens (spinach, Swiss chard)",
                "Berries (rich in antioxidants)",
                "Oats and whole grains",
                "Beets and beet juice",
                "Fatty fish (omega-3 rich)",
                "Garlic and herbs (instead of salt)",
                "Avoid: Excessive salt, processed meats, alcohol"
            ],
            "heart": [
                "Fatty fish (salmon, tuna, sardines)",
                "Walnuts and almonds",
                "Berries and dark chocolate (70%+ cocoa)",
                "Leafy green vegetables",
                "Whole grains (oatmeal, brown rice)",
                "Avocados (healthy fats)",
                "Olive oil (extra virgin)",
                "Avoid: Trans fats, excessive red meat, fried foods"
            ],
            "cholesterol": [
                "Oats and barley (soluble fiber)",
                "Beans and lentils",
                "Nuts (almonds, walnuts)",
                "Fatty fish (omega-3)",
                "Fruits (apples, grapes, strawberries)",
                "Soy products (tofu, soy milk)",
                "Olive oil",
                "Avoid: Saturated fats, trans fats, organ meats"
            ],
            "general": [
                "Colorful vegetables and fruits",
                "Whole grains",
                "Lean proteins (chicken, fish, legumes)",
                "Healthy fats (nuts, seeds, olive oil)",
                "Stay hydrated (8 glasses of water daily)",
                "Limit processed foods and added sugars"
            ]
        }
    
    def generate_summary(self, report_text: str, context_chunks: List[str]) -> tuple:
        """Generate summary using extractive approach
        
        Returns:
            tuple: (summary_text, follow_up_date, detected_diseases, medications, recovery_time)
        """
        
        # Extract key sections
        lines = report_text.split('\n')
        
        # Find important sections
        demographics = self._extract_section(lines, ['patient', 'name', 'age', 'dob', 'gender'])
        diagnoses = self._extract_section(lines, ['diagnosis', 'diagnoses', 'impression', 'assessment'])
        findings = self._extract_section(lines, ['findings', 'results', 'examination', 'test'])
        recommendations = self._extract_section(lines, ['recommendation', 'treatment', 'plan', 'medication', 'prescription'])
        
        # Detect diseases
        detected_diseases = self.detect_diseases(report_text)
        
        # Extract follow-up date
        follow_up_date = self._extract_follow_up_date(report_text)
        
        # Generate medication suggestions
        medication_suggestions = self.suggest_medications(detected_diseases, report_text)
        
        # Estimate recovery time
        recovery_time = self.estimate_recovery_time(detected_diseases, report_text)
        
        # Build structured summary
        summary_parts = []
        
        if demographics:
            summary_parts.append("## Patient Demographics\n" + "\n".join(demographics[:3]))
        
        # Add detected diseases
        summary_parts.append("## Detected Conditions\n" + "\n".join([f"• {disease}" for disease in detected_diseases]))
        
        if diagnoses:
            summary_parts.append("## Primary Diagnoses\n" + "\n".join(diagnoses[:5]))
        
        if findings:
            summary_parts.append("## Key Findings\n" + "\n".join(findings[:5]))
        
        if recommendations:
            summary_parts.append("## Treatment Recommendations\n" + "\n".join(recommendations[:5]))
        
        # Add medication suggestions
        summary_parts.append(medication_suggestions)
        
        # Add recovery time estimation
        summary_parts.append(recovery_time)
        
        # Add follow-up information
        if follow_up_date:
            summary_parts.append(f"## Follow-up\n{follow_up_date}")
        
        # Add dietary recommendations
        food_recommendations = self._get_food_recommendations(report_text)
        if food_recommendations:
            summary_parts.append("## Recommended Foods & Diet\n" + food_recommendations)
        
        if not summary_parts:
            # Fallback: just take first meaningful lines
            meaningful_lines = [line.strip() for line in lines if len(line.strip()) > 20][:15]
            return "## Medical Report Summary\n\n" + "\n".join(meaningful_lines), follow_up_date, detected_diseases, medication_suggestions, recovery_time
        
        return "\n\n".join(summary_parts), follow_up_date, detected_diseases, medication_suggestions, recovery_time
    
    def _extract_section(self, lines: List[str], keywords: List[str]) -> List[str]:
        """Extract lines containing specific keywords"""
        extracted = []
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords):
                # Include this line and next few lines
                extracted.append(line.strip())
                for j in range(i+1, min(i+4, len(lines))):
                    if lines[j].strip():
                        extracted.append(lines[j].strip())
                break
        return extracted
    
    def _get_food_recommendations(self, report_text: str) -> str:
        """Generate food recommendations based on diagnoses"""
        text_lower = report_text.lower()
        recommendations = []
        
        # Check for various conditions
        if any(word in text_lower for word in ['diabetes', 'diabetic', 'glucose', 'blood sugar']):
            recommendations.extend(self.food_recommendations['diabetes'])
        
        if any(word in text_lower for word in ['hypertension', 'high blood pressure', 'bp']):
            recommendations.extend(self.food_recommendations['hypertension'])
        
        if any(word in text_lower for word in ['heart', 'cardiac', 'myocardial', 'coronary']):
            recommendations.extend(self.food_recommendations['heart'])
        
        if any(word in text_lower for word in ['cholesterol', 'lipid', 'ldl', 'hdl']):
            recommendations.extend(self.food_recommendations['cholesterol'])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for item in recommendations:
            if item not in seen:
                seen.add(item)
                unique_recommendations.append(item)
        
        if unique_recommendations:
            return "\n".join([f"• {item}" for item in unique_recommendations])
        else:
            # General recommendations
            return "\n".join([f"• {item}" for item in self.food_recommendations['general']])
    
    def _extract_follow_up_date(self, report_text: str) -> str:
        """Extract follow-up date from report"""
        import re
        from datetime import datetime, timedelta
        
        text_lower = report_text.lower()
        lines = report_text.split('\n')
        
        # Keywords to look for
        follow_up_keywords = ['follow-up', 'follow up', 'next visit', 'return', 'appointment', 'check-up', 'checkup', 'revisit']
        
        # Look for explicit follow-up mentions
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in follow_up_keywords):
                # Check this line and next few lines for dates
                context = ' '.join(lines[i:min(i+3, len(lines))]).lower()
                
                # Look for time periods (e.g., "in 1 week", "after 2 months")
                time_pattern = r'(?:in|after|within)\s+(\d+)\s+(day|days|week|weeks|month|months)'
                match = re.search(time_pattern, context)
                if match:
                    number = int(match.group(1))
                    unit = match.group(2)
                    
                    if 'day' in unit:
                        return f"Follow-up recommended in {number} day(s)"
                    elif 'week' in unit:
                        return f"Follow-up recommended in {number} week(s)"
                    elif 'month' in unit:
                        return f"Follow-up recommended in {number} month(s)"
                
                # Look for specific dates
                date_patterns = [
                    r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # MM/DD/YYYY or DD-MM-YYYY
                    r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # YYYY-MM-DD
                ]
                
                for pattern in date_patterns:
                    match = re.search(pattern, context)
                    if match:
                        return f"Follow-up scheduled: {match.group(0)}"
        
        # Default recommendation based on condition severity
        if any(word in text_lower for word in ['acute', 'severe', 'critical', 'emergency']):
            return "Follow-up recommended in 1 week"
        elif any(word in text_lower for word in ['chronic', 'stable', 'controlled']):
            return "Follow-up recommended in 3 months"
        else:
            return "Follow-up recommended in 1 month"
    
    def _load_medication_database(self) -> Dict[str, Dict]:
        """Load medication recommendations for various conditions"""
        return {
            "diabetes": {
                "medications": [
                    "Metformin 500-1000mg (twice daily)",
                    "Glipizide 5-10mg (before meals)",
                    "Insulin (as prescribed by doctor)"
                ],
                "note": "Consult doctor before taking any medication"
            },
            "hypertension": {
                "medications": [
                    "Lisinopril 10-20mg (once daily)",
                    "Amlodipine 5-10mg (once daily)",
                    "Losartan 50-100mg (once daily)"
                ],
                "note": "Blood pressure should be monitored regularly"
            },
            "heart_attack": {
                "medications": [
                    "Aspirin 81-325mg (once daily)",
                    "Clopidogrel 75mg (once daily)",
                    "Atorvastatin 40-80mg (once daily)",
                    "Beta-blockers (as prescribed)"
                ],
                "note": "Emergency medications - follow cardiologist's prescription"
            },
            "cholesterol": {
                "medications": [
                    "Atorvastatin 10-80mg (once daily)",
                    "Rosuvastatin 5-40mg (once daily)",
                    "Simvastatin 20-40mg (once daily)"
                ],
                "note": "Take in the evening for best results"
            },
            "infection": {
                "medications": [
                    "Amoxicillin 500mg (three times daily)",
                    "Azithromycin 500mg (once daily)",
                    "Ciprofloxacin 500mg (twice daily)"
                ],
                "note": "Complete the full course of antibiotics"
            },
            "pain": {
                "medications": [
                    "Ibuprofen 400-600mg (every 6-8 hours)",
                    "Acetaminophen 500-1000mg (every 4-6 hours)",
                    "Naproxen 250-500mg (twice daily)"
                ],
                "note": "Take with food to avoid stomach upset"
            }
        }
    
    def _load_recovery_time_database(self) -> Dict[str, str]:
        """Load typical recovery times for various conditions"""
        return {
            "diabetes": "Ongoing management - Blood sugar control typically improves in 2-3 months with medication and lifestyle changes",
            "hypertension": "2-4 weeks for blood pressure to stabilize with medication; ongoing management required",
            "heart_attack": "6-8 weeks for initial recovery; 3-6 months for full cardiac rehabilitation",
            "myocardial_infarction": "6-8 weeks for initial recovery; 3-6 months for full cardiac rehabilitation",
            "stroke": "3-6 months for significant recovery; ongoing rehabilitation may be needed",
            "pneumonia": "1-3 weeks with antibiotics; full recovery in 4-6 weeks",
            "bronchitis": "7-10 days for acute bronchitis; 2-3 weeks for full recovery",
            "flu": "5-7 days for symptoms to improve; 1-2 weeks for full recovery",
            "cold": "7-10 days for complete recovery",
            "fracture": "6-8 weeks for bone healing; 3-6 months for full strength recovery",
            "sprain": "2-6 weeks depending on severity",
            "surgery": "2-6 weeks for initial healing; 3-6 months for full recovery (varies by procedure)",
            "infection": "7-14 days with antibiotics; varies by infection type",
            "gastritis": "2-4 weeks with medication and dietary changes",
            "ulcer": "4-8 weeks with medication",
            "asthma": "Ongoing management - symptoms improve in days with proper medication",
            "copd": "Ongoing management - exacerbations improve in 1-2 weeks with treatment",
            "general": "Recovery time varies by condition - follow doctor's advice"
        }
    
    def detect_diseases(self, report_text: str) -> List[str]:
        """Detect diseases mentioned in the report"""
        text_lower = report_text.lower()
        detected_diseases = []
        
        disease_keywords = {
            "Diabetes Mellitus": ['diabetes', 'diabetic', 'hyperglycemia', 'blood sugar', 'glucose'],
            "Hypertension": ['hypertension', 'high blood pressure', 'elevated bp'],
            "Myocardial Infarction (Heart Attack)": ['myocardial infarction', 'heart attack', 'mi', 'stemi', 'nstemi'],
            "Coronary Artery Disease": ['coronary artery disease', 'cad', 'coronary'],
            "Hyperlipidemia": ['hyperlipidemia', 'high cholesterol', 'dyslipidemia'],
            "Pneumonia": ['pneumonia'],
            "Bronchitis": ['bronchitis'],
            "Asthma": ['asthma'],
            "COPD": ['copd', 'chronic obstructive pulmonary'],
            "Stroke": ['stroke', 'cerebrovascular accident', 'cva'],
            "Gastritis": ['gastritis'],
            "Peptic Ulcer": ['ulcer', 'peptic ulcer'],
            "Arthritis": ['arthritis'],
            "Osteoporosis": ['osteoporosis'],
            "Anemia": ['anemia', 'anaemia'],
            "Thyroid Disorder": ['hypothyroid', 'hyperthyroid', 'thyroid'],
            "Kidney Disease": ['kidney disease', 'renal', 'nephropathy'],
            "Liver Disease": ['liver disease', 'hepatitis', 'cirrhosis']
        }
        
        for disease, keywords in disease_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_diseases.append(disease)
        
        return detected_diseases if detected_diseases else ["No specific disease detected"]
    
    def suggest_medications(self, detected_diseases: List[str], report_text: str) -> str:
        """Suggest medications based on detected diseases"""
        text_lower = report_text.lower()
        suggestions = []
        
        # Check for medications already prescribed in the report
        prescribed_meds = self._extract_prescribed_medications(report_text)
        if prescribed_meds:
            suggestions.append("## Currently Prescribed Medications")
            suggestions.append(prescribed_meds)
            suggestions.append("")
        
        # Suggest additional medications based on conditions
        suggestions.append("## Suggested Medications (Consult Doctor)")
        
        condition_found = False
        
        if any('diabetes' in d.lower() for d in detected_diseases):
            meds = self.medication_database['diabetes']
            suggestions.append("\n**For Diabetes:**")
            for med in meds['medications']:
                suggestions.append(f"• {med}")
            suggestions.append(f"*Note: {meds['note']}*")
            condition_found = True
        
        if any('hypertension' in d.lower() for d in detected_diseases):
            meds = self.medication_database['hypertension']
            suggestions.append("\n**For Hypertension:**")
            for med in meds['medications']:
                suggestions.append(f"• {med}")
            suggestions.append(f"*Note: {meds['note']}*")
            condition_found = True
        
        if any('heart' in d.lower() or 'myocardial' in d.lower() for d in detected_diseases):
            meds = self.medication_database['heart_attack']
            suggestions.append("\n**For Heart Condition:**")
            for med in meds['medications']:
                suggestions.append(f"• {med}")
            suggestions.append(f"*Note: {meds['note']}*")
            condition_found = True
        
        if any('cholesterol' in d.lower() or 'lipid' in d.lower() for d in detected_diseases):
            meds = self.medication_database['cholesterol']
            suggestions.append("\n**For High Cholesterol:**")
            for med in meds['medications']:
                suggestions.append(f"• {med}")
            suggestions.append(f"*Note: {meds['note']}*")
            condition_found = True
        
        if any(word in text_lower for word in ['infection', 'pneumonia', 'bronchitis']):
            meds = self.medication_database['infection']
            suggestions.append("\n**For Infection:**")
            for med in meds['medications']:
                suggestions.append(f"• {med}")
            suggestions.append(f"*Note: {meds['note']}*")
            condition_found = True
        
        if any(word in text_lower for word in ['pain', 'ache']):
            meds = self.medication_database['pain']
            suggestions.append("\n**For Pain Management:**")
            for med in meds['medications']:
                suggestions.append(f"• {med}")
            suggestions.append(f"*Note: {meds['note']}*")
            condition_found = True
        
        if not condition_found:
            suggestions.append("• Consult your doctor for appropriate medication")
        
        suggestions.append("\n**IMPORTANT:** All medications should be taken only as prescribed by a qualified healthcare provider.")
        
        return "\n".join(suggestions)
    
    def _extract_prescribed_medications(self, report_text: str) -> str:
        """Extract medications already mentioned in the report"""
        lines = report_text.split('\n')
        medications = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['medication', 'prescription', 'drug', 'taking', 'prescribed']):
                # Get this line and next few lines
                for j in range(i, min(i+5, len(lines))):
                    if lines[j].strip() and not any(skip in lines[j].lower() for skip in ['medication:', 'prescription:', 'current medications:']):
                        medications.append(lines[j].strip())
                break
        
        if medications:
            return "\n".join([f"• {med}" for med in medications[:5]])
        return ""
    
    def estimate_recovery_time(self, detected_diseases: List[str], report_text: str) -> str:
        """Estimate recovery time based on detected diseases"""
        text_lower = report_text.lower()
        recovery_info = []
        
        recovery_info.append("## Estimated Recovery Time")
        
        found_condition = False
        
        for disease in detected_diseases:
            disease_lower = disease.lower()
            
            # Check each condition in recovery database
            for condition, recovery_time in self.recovery_time_database.items():
                if condition in disease_lower or condition in text_lower:
                    recovery_info.append(f"\n**{disease}:**")
                    recovery_info.append(f"• {recovery_time}")
                    found_condition = True
                    break
        
        if not found_condition:
            recovery_info.append(f"\n• {self.recovery_time_database['general']}")
        
        recovery_info.append("\n**Note:** Recovery times are estimates and vary by individual. Follow your doctor's guidance.")
        
        return "\n".join(recovery_info)
