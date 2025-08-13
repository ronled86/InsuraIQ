import csv
import json
import re
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
import openai
from ..core.settings import settings

# Configure OpenAI client
openai.api_key = settings.OPENAI_API_KEY
logger = logging.getLogger(__name__)

class PolicyAnalyzer:
    """Enhanced policy analysis with GenAI capabilities"""
    
    def __init__(self):
        self.coverage_categories = [
            "liability_coverage",
            "collision_coverage", 
            "comprehensive_coverage",
            "medical_coverage",
            "property_damage",
            "bodily_injury",
            "uninsured_motorist",
            "personal_injury_protection",
            "rental_car_coverage",
            "roadside_assistance",
            "gap_coverage",
            "deductibles",
            "policy_limits",
            "exclusions",
            "special_provisions"
        ]
        
        # Initialize OpenAI client
        if settings.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            self.ai_enabled = True
        else:
            self.openai_client = None
            self.ai_enabled = False
            logger.warning("OpenAI API key not found. Falling back to regex-only parsing.")
    
    def analyze_policy_text(self, text: str, policy_type: str = "auto") -> Dict[str, Any]:
        """
        Enhanced insurance policy analysis using AI + regex patterns
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Starting AI-enhanced policy analysis for type: {policy_type}")
        logger.info(f"Text length: {len(text)} characters, AI enabled: {self.ai_enabled}")
        
        # First, try AI-powered analysis if available
        ai_analysis = {}
        if self.ai_enabled and len(text) > 100:
            try:
                ai_analysis = self._ai_extract_policy_data(text, policy_type)
                logger.info(f"AI analysis completed successfully")
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                ai_analysis = {}
        
        # Always run regex-based analysis as backup/enhancement
        regex_analysis = {
            "basic_info": self._extract_comprehensive_basic_info(text),
            "financial_info": self._extract_comprehensive_financial_info(text),
            "coverage_details": self._extract_comprehensive_coverage_details(text, policy_type),
            "policy_terms": self._extract_policy_terms(text),
            "beneficiaries": self._extract_beneficiaries(text),
            "exclusions": self._extract_exclusions(text),
            "claims_info": self._extract_claims_information(text),
            "contact_info": self._extract_contact_information(text),
            "legal_info": self._extract_legal_information(text),
            "special_provisions": self._extract_special_provisions(text),
            "document_metadata": self._extract_document_metadata(text),
            "risk_assessment": self._extract_risk_assessment(text),
            "payment_schedule": self._extract_payment_schedule(text),
            "riders_endorsements": self._extract_riders_and_endorsements(text),
            "vehicle_info": self._extract_vehicle_information(text) if policy_type == "auto" else {},
            "property_info": self._extract_property_information(text) if policy_type in ["home", "property"] else {},
            "health_info": self._extract_health_information(text) if policy_type == "health" else {},
            "life_info": self._extract_life_insurance_information(text) if policy_type == "life" else {},
            "business_info": self._extract_business_information(text) if policy_type == "business" else {}
        }
        
        # Merge AI and regex analysis intelligently
        final_analysis = self._merge_analysis_results(ai_analysis, regex_analysis)
        
        # Calculate comprehensive confidence score
        confidence = self._calculate_extraction_confidence(final_analysis, text)
        final_analysis["extraction_confidence"] = confidence
        final_analysis["language"] = self._detect_document_language(text)
        final_analysis["total_parameters_extracted"] = self._count_extracted_parameters(final_analysis)
        final_analysis["ai_enhanced"] = self.ai_enabled and len(ai_analysis) > 0
        
        logger.info(f"Analysis completed. Confidence: {confidence:.2f}, Parameters extracted: {final_analysis['total_parameters_extracted']}, AI enhanced: {final_analysis['ai_enhanced']}")
        
        return final_analysis

    def _ai_extract_policy_data(self, text: str, policy_type: str) -> Dict[str, Any]:
        """Use OpenAI to extract comprehensive policy information"""
        
        # Truncate text if too long (to stay within token limits)
        max_chars = 12000  # Roughly 3000 tokens
        if len(text) > max_chars:
            text = text[:max_chars] + "...[truncated]"
        
        prompt = f"""
You are an expert insurance policy analyst. Analyze the following {policy_type} insurance document and extract ALL possible information in a structured JSON format.

Extract comprehensive details including but not limited to:

BASIC INFORMATION:
- Policy number, insurer name, policyholder name, agent details
- Effective dates, expiration dates, renewal terms
- Product type and coverage type

FINANCIAL DETAILS:
- Premium amounts (annual, monthly, quarterly)
- Deductibles (collision, comprehensive, etc.)
- Coverage limits and maximum payouts
- Co-pays, co-insurance percentages
- Out-of-pocket maximums

COVERAGE DETAILS:
- Liability coverage (bodily injury, property damage)
- Collision and comprehensive coverage
- Medical payments, PIP, uninsured motorist
- Special coverages, riders, endorsements

POLICY TERMS:
- Policy period, renewal terms
- Cancellation conditions
- Payment schedules and methods

CONTACT INFORMATION:
- Phone numbers, email addresses
- Mailing addresses, billing addresses
- Agent contact details

VEHICLE/PROPERTY SPECIFIC (if applicable):
- VIN numbers, vehicle details (make, model, year)
- Property addresses, construction details
- Risk factors and safety features

LEGAL INFORMATION:
- License numbers, regulatory information
- State of issuance, NAIC codes

Extract amounts as numbers where possible. For dates, use YYYY-MM-DD format.
Return only valid JSON with nested objects for categories.

Insurance Document:
{text}

JSON Response:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert insurance document analyzer. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                parsed_result = json.loads(result)
                return parsed_result
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    logger.warning("AI response was not valid JSON")
                    return {}
                    
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return {}

    def _merge_analysis_results(self, ai_analysis: Dict[str, Any], regex_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligently merge AI and regex analysis results"""
        
        if not ai_analysis:
            return regex_analysis
        
        merged = {}
        
        # Standard section mapping between AI and regex results
        section_mappings = {
            "basic_info": ["basic_information", "policy_info", "general", "basic_info"],
            "financial_info": ["financial_details", "financial", "costs", "financial_info"],
            "coverage_details": ["coverage_details", "coverage", "coverages", "benefits"],
            "contact_info": ["contact_information", "contact", "contacts", "contact_info"],
            "vehicle_info": ["vehicle_information", "vehicle", "auto", "car"],
            "property_info": ["property_information", "property", "real_estate", "home"],
            "policy_terms": ["policy_terms", "terms", "conditions", "policy_conditions"],
            "legal_info": ["legal_information", "legal", "regulatory", "compliance"]
        }
        
        # Process each section
        for regex_section, section_data in regex_analysis.items():
            merged[regex_section] = {}
            
            # Start with regex data
            if isinstance(section_data, dict):
                merged[regex_section].update(section_data)
            
            # Find corresponding AI data
            ai_section_data = {}
            if regex_section in section_mappings:
                for possible_ai_key in section_mappings[regex_section]:
                    if possible_ai_key in ai_analysis:
                        ai_section_data = ai_analysis[possible_ai_key]
                        break
            
            # Also check direct section name in AI results
            if regex_section in ai_analysis:
                ai_section_data = ai_analysis[regex_section]
            
            # Merge AI data, prioritizing AI values when they exist
            if isinstance(ai_section_data, dict):
                for key, value in ai_section_data.items():
                    if value and value != "":  # Only use non-empty AI values
                        # Convert AI field names to regex format
                        normalized_key = key.lower().replace(" ", "_").replace("-", "_")
                        merged[regex_section][normalized_key] = value
            
            # Add any additional AI sections not covered by regex
            for ai_key, ai_value in ai_analysis.items():
                if ai_key not in [item for sublist in section_mappings.values() for item in sublist]:
                    if ai_key not in merged:
                        merged[ai_key] = ai_value
        
        return merged

    def _extract_comprehensive_basic_info(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive basic policy information"""
        info = {}
        
        # Policy Number patterns (much more comprehensive)
        policy_patterns = [
            r'(?:Policy\s*(?:Number|No\.?|#)):\s*([A-Z0-9\-]+)',
            r'(?:פוליסה\s*(?:מספר|מס\.?)):\s*([A-Z0-9\-]+)',
            r'(?:Certificate\s*(?:Number|No\.?)):\s*([A-Z0-9\-]+)',
            r'(?:Contract\s*(?:Number|No\.?)):\s*([A-Z0-9\-]+)',
            r'(?:Policy\s*ID):\s*([A-Z0-9\-]+)',
            r'(?:Reference\s*(?:Number|No\.?)):\s*([A-Z0-9\-]+)',
            r'([A-Z]{2,4}[\-]?[0-9]{6,12})',  # Pattern like ABC-123456789
            r'([0-9]{8,15})',  # Numeric policy numbers
        ]
        
        for pattern in policy_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                info['policy_number'] = matches[0] if isinstance(matches[0], str) else matches[0][0]
                break
        
        # Insurer/Company patterns (comprehensive list)
        insurer_patterns = [
            # Major US insurers
            r'(State Farm|Geico|Progressive|Allstate|Farmers|USAA|Liberty Mutual|Nationwide)',
            r'(American Family|Auto-Owners|Amica|Erie|Travelers|Hartford|Chubb)',
            # Major Israeli insurers
            r'(הפניקס|פניקס|Phoenix|הראל|Harel|כלל|Clal|מנורה מבטחים|Menorah|ביטוח ישיר|Bituach Yashir)',
            r'(מגדל|Migdal|אי.די.איי|IDB|שומרה|Shomera|איילון|Ayalon|הכשרה|Hachshara)',
            # International insurers
            r'(AXA|Allianz|Zurich|MetLife|Prudential|AIG|Munich Re|Swiss Re)',
            r'(Aviva|RSA|Admiral|Direct Line|Churchill|Hastings|More Than)',
            # Generic patterns
            r'([A-Z][a-z]+\s+Insurance\s+(?:Company|Corp|Group|Inc)?)',
            r'([A-Z][a-z]+\s+Assurance\s+(?:Company|Corp|Group)?)',
            r'(חברת\s+[א-ת\s]+(?:לביטוח|ביטוח))',
        ]
        
        for pattern in insurer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['insurer'] = match.group(1).strip()
                break
        
        # Policy holder patterns (multiple variations)
        holder_patterns = [
            r'(?:Policy\s*Holder|Named\s*Insured|Insured\s*Person):\s*([^\n\r]{3,50})',
            r'(?:Policyholder|Policy\s*Owner):\s*([^\n\r]{3,50})',
            r'(?:בעל\s*הפוליסה|מבוטח|בעל\s*הביטוח):\s*([^\n\r]{3,50})',
            r'(?:Customer\s*Name|Client\s*Name):\s*([^\n\r]{3,50})',
            r'(?:Insured\s*Name|Member\s*Name):\s*([^\n\r]{3,50})',
            r'(?:First\s*Named\s*Insured):\s*([^\n\r]{3,50})',
        ]
        
        for pattern in holder_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['owner_name'] = match.group(1).strip()
                break
        
        # Agent/Broker information
        agent_patterns = [
            r'(?:Agent|Broker|Producer):\s*([^\n\r]{3,50})',
            r'(?:סוכן|מתווך):\s*([^\n\r]{3,50})',
            r'(?:Agent\s*Name|Broker\s*Name):\s*([^\n\r]{3,50})',
            r'(?:Licensed\s*Agent):\s*([^\n\r]{3,50})',
        ]
        
        for pattern in agent_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['agent_name'] = match.group(1).strip()
                break
        
        # Product type detection (enhanced)
        product_patterns = {
            'auto': [
                r'(?:Auto|Vehicle|Car|Motor|Automobile)\s*(?:Insurance|Policy|Coverage)',
                r'(?:ביטוח\s*רכב|רכב\s*ביטוח)',
                r'Personal\s*Auto\s*Policy',
                r'Commercial\s*Auto\s*Policy'
            ],
            'home': [
                r'(?:Home|House|Property|Dwelling)\s*(?:Insurance|Policy|Coverage)',
                r'(?:ביטוח\s*בית|בית\s*ביטוח|ביטוח\s*דירה)',
                r'Homeowners\s*Policy',
                r'Renters\s*Insurance'
            ],
            'health': [
                r'(?:Health|Medical|Healthcare)\s*(?:Insurance|Policy|Coverage)',
                r'(?:ביטוח\s*בריאות|בריאות\s*ביטוח)',
                r'Major\s*Medical',
                r'Group\s*Health'
            ],
            'life': [
                r'(?:Life|Term\s*Life|Whole\s*Life)\s*(?:Insurance|Policy)',
                r'(?:ביטוח\s*חיים|חיים\s*ביטוח)',
                r'Universal\s*Life',
                r'Variable\s*Life'
            ],
            'business': [
                r'(?:Business|Commercial|General\s*Liability)\s*(?:Insurance|Policy)',
                r'(?:ביטוח\s*עסקי|עסקי\s*ביטוח)',
                r'Professional\s*Liability',
                r'Workers\s*Compensation'
            ]
        }
        
        for product_type, patterns in product_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    info['product_type'] = product_type
                    break
            if 'product_type' in info:
                break
        
        return info

    def _extract_comprehensive_financial_info(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive financial information"""
        financial = {}
        
        # Premium patterns (multiple currencies and formats)
        premium_patterns = [
            r'(?:Annual\s*Premium|Yearly\s*Premium):\s*[$₪€£¥]?([\d,]+\.?\d*)',
            r'(?:Monthly\s*Premium|Monthly\s*Payment):\s*[$₪€£¥]?([\d,]+\.?\d*)',
            r'(?:Total\s*Premium|Premium\s*Amount):\s*[$₪€£¥]?([\d,]+\.?\d*)',
            r'(?:פרמיה\s*שנתית|פרמיה\s*חודשית):\s*[$₪€£¥]?([\d,]+\.?\d*)',
            r'(?:Premium\s*Due):\s*[$₪€£¥]?([\d,]+\.?\d*)',
            r'(?:Policy\s*Premium):\s*[$₪€£¥]?([\d,]+\.?\d*)',
        ]
        
        for pattern in premium_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if 'annual' in pattern.lower() or 'yearly' in pattern.lower() or 'שנתית' in pattern:
                    financial['premium_annual'] = self._parse_amount(matches[0])
                    financial['premium_monthly'] = self._parse_amount(matches[0]) / 12
                elif 'monthly' in pattern.lower() or 'חודשית' in pattern:
                    financial['premium_monthly'] = self._parse_amount(matches[0])
                    financial['premium_annual'] = self._parse_amount(matches[0]) * 12
                else:
                    financial['premium_total'] = self._parse_amount(matches[0])
        
        # Deductible patterns
        deductible_patterns = [
            r'(?:Deductible|Deductible\s*Amount):\s*[$₪€£¥]?([\d,]+\.?\d*)',
            r'(?:Self\s*Insured\s*Retention):\s*[$₪€£¥]?([\d,]+\.?\d*)',
            r'(?:השתתפות\s*עצמית):\s*[$₪€£¥]?([\d,]+\.?\d*)',
            r'(?:Collision\s*Deductible):\s*[$₪€£¥]?([\d,]+\.?\d*)',
            r'(?:Comprehensive\s*Deductible):\s*[$₪€£¥]?([\d,]+\.?\d*)',
        ]
        
        for pattern in deductible_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if 'collision' in pattern.lower():
                    financial['collision_deductible'] = self._parse_amount(matches[0])
                elif 'comprehensive' in pattern.lower():
                    financial['comprehensive_deductible'] = self._parse_amount(matches[0])
                else:
                    financial['deductible'] = self._parse_amount(matches[0])
        
        # Coverage limits and amounts
        limit_patterns = [
            r'(?:Coverage\s*Limit|Policy\s*Limit|Maximum\s*Coverage):\s*[$₪€£¥]?([\d,]+\.?\d*)',
            r'(?:Liability\s*Limit|Per\s*Occurrence\s*Limit):\s*[$₪€£¥]?([\d,]+\.?\d*)',
            r'(?:Aggregate\s*Limit|Annual\s*Aggregate):\s*[$₪€£¥]?([\d,]+\.?\d*)',
            r'(?:Sum\s*Insured|Insured\s*Amount):\s*[$₪€£¥]?([\d,]+\.?\d*)',
            r'(?:סכום\s*ביטוח|גבול\s*כיסוי):\s*[$₪€£¥]?([\d,]+\.?\d*)',
        ]
        
        for pattern in limit_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if 'liability' in pattern.lower():
                    financial['liability_limit'] = self._parse_amount(matches[0])
                elif 'aggregate' in pattern.lower():
                    financial['aggregate_limit'] = self._parse_amount(matches[0])
                else:
                    financial['coverage_limit'] = self._parse_amount(matches[0])
        
        return financial

    def _extract_comprehensive_coverage_details(self, text: str, policy_type: str) -> Dict[str, Any]:
        """Extract detailed coverage information based on policy type"""
        coverage = {}
        
        # General coverage patterns
        general_coverage_patterns = [
            r'([A-Za-z\s]+(?:Coverage|Protection|Benefit)):\s*[$₪€£¥]?([\d,]+\.?\d*)',
            r'([A-Za-z\s]+(?:Limit|Maximum)):\s*[$₪€£¥]?([\d,]+\.?\d*)',
            r'([א-ת\s]+(?:כיסוי|הגנה|הטבה)):\s*[$₪€£¥]?([\d,]+\.?\d*)',
        ]
        
        for pattern in general_coverage_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for coverage_name, amount in matches:
                key = coverage_name.lower().strip().replace(' ', '_')
                coverage[key] = {
                    'amount': self._parse_amount(amount),
                    'description': coverage_name.strip(),
                    'type': 'general'
                }
        
        # Auto-specific coverage
        if policy_type == "auto":
            auto_coverage_patterns = [
                r'(?:Bodily\s*Injury\s*Liability):\s*[$₪€£¥]?([\d,]+\.?\d*)(?:/[$₪€£¥]?([\d,]+\.?\d*))?',
                r'(?:Property\s*Damage\s*Liability):\s*[$₪€£¥]?([\d,]+\.?\d*)',
                r'(?:Collision\s*Coverage):\s*[$₪€£¥]?([\d,]+\.?\d*)',
                r'(?:Comprehensive\s*Coverage):\s*[$₪€£¥]?([\d,]+\.?\d*)',
                r'(?:Uninsured\s*Motorist):\s*[$₪€£¥]?([\d,]+\.?\d*)',
                r'(?:Personal\s*Injury\s*Protection|PIP):\s*[$₪€£¥]?([\d,]+\.?\d*)',
                r'(?:Medical\s*Payments):\s*[$₪€£¥]?([\d,]+\.?\d*)',
                r'(?:Rental\s*Reimbursement):\s*[$₪€£¥]?([\d,]+\.?\d*)',
                r'(?:Towing\s*and\s*Labor):\s*[$₪€£¥]?([\d,]+\.?\d*)',
            ]
            
            for pattern in auto_coverage_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    if 'bodily_injury' in pattern.lower():
                        if len(matches[0]) == 2 and matches[0][1]:  # Per person/per accident format
                            coverage['bodily_injury_per_person'] = {'amount': self._parse_amount(matches[0][0]), 'type': 'auto'}
                            coverage['bodily_injury_per_accident'] = {'amount': self._parse_amount(matches[0][1]), 'type': 'auto'}
                        else:
                            coverage['bodily_injury_liability'] = {'amount': self._parse_amount(matches[0][0]), 'type': 'auto'}
                    elif 'property_damage' in pattern.lower():
                        coverage['property_damage_liability'] = {'amount': self._parse_amount(matches[0]), 'type': 'auto'}
                    elif 'collision' in pattern.lower():
                        coverage['collision_coverage'] = {'amount': self._parse_amount(matches[0]), 'type': 'auto'}
                    elif 'comprehensive' in pattern.lower():
                        coverage['comprehensive_coverage'] = {'amount': self._parse_amount(matches[0]), 'type': 'auto'}
        
        # Home insurance specific coverage
        elif policy_type in ["home", "property"]:
            home_coverage_patterns = [
                r'(?:Dwelling\s*Coverage|Coverage\s*A):\s*[$₪€£¥]?([\d,]+\.?\d*)',
                r'(?:Other\s*Structures|Coverage\s*B):\s*[$₪€£¥]?([\d,]+\.?\d*)',
                r'(?:Personal\s*Property|Coverage\s*C):\s*[$₪€£¥]?([\d,]+\.?\d*)',
                r'(?:Loss\s*of\s*Use|Coverage\s*D):\s*[$₪€£¥]?([\d,]+\.?\d*)',
                r'(?:Personal\s*Liability|Coverage\s*E):\s*[$₪€£¥]?([\d,]+\.?\d*)',
                r'(?:Medical\s*Payments|Coverage\s*F):\s*[$₪€£¥]?([\d,]+\.?\d*)',
                r'(?:Water\s*Damage|Flood\s*Coverage):\s*[$₪€£¥]?([\d,]+\.?\d*)',
                r'(?:Fire\s*Coverage|Fire\s*Damage):\s*[$₪€£¥]?([\d,]+\.?\d*)',
                r'(?:Theft\s*Coverage|Burglary\s*Coverage):\s*[$₪€£¥]?([\d,]+\.?\d*)',
            ]
            
            for pattern in home_coverage_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    coverage_type = pattern.lower().split('|')[0].strip('(?:').replace('\\s*', '_').replace('\\', '')
                    coverage[coverage_type] = {'amount': self._parse_amount(matches[0]), 'type': 'home'}
        
        return coverage

    def _extract_policy_terms(self, text: str) -> Dict[str, Any]:
        """Extract policy terms and conditions"""
        terms = {}
        
        # Policy period patterns
        period_patterns = [
            r'(?:Policy\s*Period|Coverage\s*Period|Term):\s*([0-9/\-\.]{8,12})\s*(?:to|through|[\-–])\s*([0-9/\-\.]{8,12})',
            r'(?:Effective\s*Date):\s*([0-9/\-\.]{8,12})',
            r'(?:Expiration\s*Date|Expires):\s*([0-9/\-\.]{8,12})',
            r'(?:תקופת\s*הביטוח):\s*([0-9/\-\.]{8,12})\s*(?:עד|ל)\s*([0-9/\-\.]{8,12})',
        ]
        
        for pattern in period_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2 and match.group(2):
                    terms['start_date'] = match.group(1).strip()
                    terms['end_date'] = match.group(2).strip()
                elif 'effective' in pattern.lower():
                    terms['start_date'] = match.group(1).strip()
                elif 'expiration' in pattern.lower() or 'expires' in pattern.lower():
                    terms['end_date'] = match.group(1).strip()
                break
        
        # Renewal terms
        renewal_patterns = [
            r'(?:Renewal|Auto[\-\s]*Renewal):\s*([^\n\r]{5,50})',
            r'(?:Cancellation\s*Notice):\s*([^\n\r]{5,50})',
            r'(?:חידוש):\s*([^\n\r]{5,50})',
        ]
        
        for pattern in renewal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'renewal' in pattern.lower() or 'חידוש' in pattern:
                    terms['renewal_terms'] = match.group(1).strip()
                elif 'cancellation' in pattern.lower():
                    terms['cancellation_notice'] = match.group(1).strip()
        
        return terms

    def _extract_beneficiaries(self, text: str) -> Dict[str, Any]:
        """Extract beneficiary information"""
        beneficiaries = {}
        
        beneficiary_patterns = [
            r'(?:Primary\s*Beneficiary|Beneficiary):\s*([^\n\r]{3,50})',
            r'(?:Secondary\s*Beneficiary|Contingent\s*Beneficiary):\s*([^\n\r]{3,50})',
            r'(?:מוטב|מוטב\s*ראשי):\s*([^\n\r]{3,50})',
            r'(?:Spouse|Partner):\s*([^\n\r]{3,50})',
            r'(?:Children|Dependents):\s*([^\n\r]{3,100})',
        ]
        
        for pattern in beneficiary_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if 'primary' in pattern.lower() or 'beneficiary' in pattern.lower() and 'secondary' not in pattern.lower():
                    beneficiaries['primary_beneficiary'] = matches[0].strip()
                elif 'secondary' in pattern.lower() or 'contingent' in pattern.lower():
                    beneficiaries['secondary_beneficiary'] = matches[0].strip()
                elif 'spouse' in pattern.lower():
                    beneficiaries['spouse'] = matches[0].strip()
                elif 'children' in pattern.lower():
                    beneficiaries['children'] = matches[0].strip()
        
        return beneficiaries

    def _extract_exclusions(self, text: str) -> Dict[str, Any]:
        """Extract policy exclusions"""
        exclusions = {}
        
        exclusion_patterns = [
            r'(?:Exclusions?|Not\s*Covered|Excluded):\s*([^\n\r]{10,200})',
            r'(?:לא\s*מכוסה|הוצאות):\s*([^\n\r]{10,200})',
            r'(?:This\s*policy\s*does\s*not\s*cover):\s*([^\n\r]{10,200})',
        ]
        
        exclusion_items = []
        for pattern in exclusion_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            exclusion_items.extend(matches)
        
        if exclusion_items:
            exclusions['general_exclusions'] = exclusion_items
        
        return exclusions

    def _extract_claims_information(self, text: str) -> Dict[str, Any]:
        """Extract claims and contact information"""
        claims = {}
        
        claims_patterns = [
            r'(?:Claims?\s*(?:Phone|Number|Hotline)):\s*([0-9\-\(\)\s\+]+)',
            r'(?:Report\s*a\s*Claim):\s*([0-9\-\(\)\s\+]+)',
            r'(?:24\s*Hour\s*Claims?):\s*([0-9\-\(\)\s\+]+)',
            r'(?:Emergency\s*Claims?):\s*([0-9\-\(\)\s\+]+)',
        ]
        
        for pattern in claims_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                claims['claims_phone'] = matches[0].strip()
                break
        
        return claims

    def _extract_contact_information(self, text: str) -> Dict[str, Any]:
        """Extract contact information"""
        contact = {}
        
        phone_patterns = [
            r'(?:Phone|Tel|Telephone):\s*([0-9\-\(\)\s\+]{10,20})',
            r'(?:Customer\s*Service):\s*([0-9\-\(\)\s\+]{10,20})',
            r'(?:טלפון):\s*([0-9\-\(\)\s\+]{10,20})',
        ]
        
        email_patterns = [
            r'(?:Email|E[\-\s]*mail):\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        ]
        
        address_patterns = [
            r'(?:Address|Mailing\s*Address):\s*([^\n\r]{10,100})',
            r'(?:כתובת):\s*([^\n\r]{10,100})',
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                contact['phone'] = matches[0].strip()
                break
        
        for pattern in email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                contact['email'] = matches[0].strip()
                break
        
        for pattern in address_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                contact['address'] = matches[0].strip()
                break
        
        return contact

    def _extract_legal_information(self, text: str) -> Dict[str, Any]:
        """Extract legal information"""
        legal = {}
        
        legal_patterns = [
            r'(?:License\s*(?:Number|No\.?)):\s*([A-Z0-9\-]+)',
            r'(?:State\s*of\s*(?:Issue|Domicile)):\s*([A-Z]{2}|[A-Za-z\s]+)',
            r'(?:NAIC\s*(?:Number|Code)):\s*([0-9]+)',
            r'(?:Department\s*of\s*Insurance):\s*([^\n\r]{5,50})',
        ]
        
        for pattern in legal_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if 'license' in pattern.lower():
                    legal['license_number'] = matches[0].strip()
                elif 'state' in pattern.lower():
                    legal['state_of_issue'] = matches[0].strip()
                elif 'naic' in pattern.lower():
                    legal['naic_number'] = matches[0].strip()
        
        return legal

    def _extract_special_provisions(self, text: str) -> Dict[str, Any]:
        """Extract special provisions and endorsements"""
        provisions = {}
        
        provision_patterns = [
            r'(?:Special\s*Provisions?):\s*([^\n\r]{10,200})',
            r'(?:Endorsements?):\s*([^\n\r]{10,200})',
            r'(?:Riders?):\s*([^\n\r]{10,200})',
            r'(?:Additional\s*Coverage):\s*([^\n\r]{10,200})',
        ]
        
        provision_items = []
        for pattern in provision_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            provision_items.extend(matches)
        
        if provision_items:
            provisions['special_provisions'] = provision_items
        
        return provisions

    def _extract_document_metadata(self, text: str) -> Dict[str, Any]:
        """Extract document metadata"""
        metadata = {}
        
        metadata_patterns = [
            r'(?:Document\s*(?:Date|Created)):\s*([0-9/\-\.]{8,12})',
            r'(?:Issue\s*Date):\s*([0-9/\-\.]{8,12})',
            r'(?:Version|Revision):\s*([0-9\.]+)',
            r'(?:Form\s*(?:Number|Code)):\s*([A-Z0-9\-]+)',
        ]
        
        for pattern in metadata_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if 'document' in pattern.lower() or 'issue' in pattern.lower():
                    metadata['document_date'] = matches[0].strip()
                elif 'version' in pattern.lower() or 'revision' in pattern.lower():
                    metadata['document_version'] = matches[0].strip()
                elif 'form' in pattern.lower():
                    metadata['form_number'] = matches[0].strip()
        
        return metadata

    def _extract_risk_assessment(self, text: str) -> Dict[str, Any]:
        """Extract risk assessment information"""
        risk = {}
        
        risk_patterns = [
            r'(?:Risk\s*(?:Category|Class|Rating)):\s*([^\n\r]{3,30})',
            r'(?:Territory|Rating\s*Territory):\s*([^\n\r]{3,30})',
            r'(?:Experience\s*Rating):\s*([^\n\r]{3,30})',
            r'(?:Safety\s*Rating):\s*([^\n\r]{3,30})',
        ]
        
        for pattern in risk_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if 'risk' in pattern.lower():
                    risk['risk_category'] = matches[0].strip()
                elif 'territory' in pattern.lower():
                    risk['territory'] = matches[0].strip()
                elif 'experience' in pattern.lower():
                    risk['experience_rating'] = matches[0].strip()
                elif 'safety' in pattern.lower():
                    risk['safety_rating'] = matches[0].strip()
        
        return risk

    def _extract_payment_schedule(self, text: str) -> Dict[str, Any]:
        """Extract payment schedule information"""
        payment = {}
        
        payment_patterns = [
            r'(?:Payment\s*(?:Schedule|Plan)):\s*([^\n\r]{5,50})',
            r'(?:Due\s*Date):\s*([0-9/\-\.]{8,12})',
            r'(?:Payment\s*Method):\s*([^\n\r]{5,30})',
            r'(?:Installments?):\s*([^\n\r]{5,30})',
        ]
        
        for pattern in payment_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if 'schedule' in pattern.lower() or 'plan' in pattern.lower():
                    payment['payment_schedule'] = matches[0].strip()
                elif 'due' in pattern.lower():
                    payment['due_date'] = matches[0].strip()
                elif 'method' in pattern.lower():
                    payment['payment_method'] = matches[0].strip()
                elif 'installment' in pattern.lower():
                    payment['installments'] = matches[0].strip()
        
        return payment

    def _extract_riders_and_endorsements(self, text: str) -> Dict[str, Any]:
        """Extract riders and endorsements"""
        riders = {}
        
        rider_patterns = [
            r'(?:Rider|Endorsement)\s*([A-Z0-9\-]+):\s*([^\n\r]{5,100})',
            r'(?:Additional\s*Coverage)\s*([A-Z0-9\-]+):\s*([^\n\r]{5,100})',
        ]
        
        rider_items = {}
        for pattern in rider_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for rider_id, description in matches:
                rider_items[rider_id.strip()] = description.strip()
        
        if rider_items:
            riders['riders'] = rider_items
        
        return riders
        info = {}
        
        # Policy number patterns
        policy_patterns = [
            r'Policy\s*(?:Number|No\.?)\s*:?\s*([A-Z0-9\-]+)',
            r'פוליסה\s*(?:מספר|מס\.?)\s*:?\s*([A-Z0-9\-]+)',  # Hebrew
            r'Certificate\s*(?:Number|No\.?)\s*:?\s*([A-Z0-9\-]+)'
        ]
        
        for pattern in policy_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['policy_number'] = match.group(1).strip()
                break
        
        # Insurer patterns
        insurer_patterns = [
            r'(?:Insurance Company|Insurer|Company):\s*([^\n]+)',
            r'(?:חברת ביטוח|מבטח):\s*([^\n]+)',  # Hebrew
            r'^([A-Z][A-Za-z\s&]+(?:Insurance|Assurance))'  # Company name with Insurance
        ]
        
        for pattern in insurer_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                info['insurer'] = match.group(1).strip()
                break
        
        # Policy holder patterns
        holder_patterns = [
            r'(?:Policy\s*Holder|Insured|Named Insured):\s*([^\n]+)',
            r'(?:בעל הפוליסה|מבוטח):\s*([^\n]+)',  # Hebrew
        ]
        
        for pattern in holder_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['owner_name'] = match.group(1).strip()
                break
        
        # Date patterns
        date_patterns = [
            r'(?:Policy Period|Coverage Period|Effective):\s*([0-9/\-\.]+)\s*(?:to|through|\-)\s*([0-9/\-\.]+)',
            r'(?:תקופת הביטוח):\s*([0-9/\-\.]+)\s*(?:עד|ל)\s*([0-9/\-\.]+)',  # Hebrew
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['start_date'] = match.group(1).strip()
                info['end_date'] = match.group(2).strip()
                break
        
        return info
    
    def _analyze_coverage(self, text: str, policy_type: str) -> Dict[str, Any]:
        """Analyze coverage details by category"""
        coverage = {}
        
        # Coverage amount patterns
        amount_patterns = [
            r'([A-Za-z\s]+Coverage):\s*\$?([\d,]+)',
            r'([A-Za-z\s]+Limit):\s*\$?([\d,]+)',
            r'([A-Za-z\s]+Deductible):\s*\$?([\d,]+)'
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for coverage_type, amount in matches:
                key = coverage_type.lower().replace(' ', '_')
                coverage[key] = {
                    'amount': self._parse_amount(amount),
                    'description': coverage_type.strip()
                }
        
        # Special provisions and exclusions
        exclusions = self._extract_exclusions(text)
        if exclusions:
            coverage['exclusions'] = exclusions
        
        # Additional benefits
        benefits = self._extract_additional_benefits(text)
        if benefits:
            coverage['additional_benefits'] = benefits
        
        return coverage
    
    def _extract_financial_details(self, text: str) -> Dict[str, Any]:
        """Extract financial information"""
        financial = {}
        
        # Premium patterns
        premium_patterns = [
            r'(?:Annual Premium|Total Premium):\s*\$?([\d,\.]+)',
            r'(?:Monthly Premium):\s*\$?([\d,\.]+)',
            r'(?:דמי ביטוח שנתי):\s*₪?([\d,\.]+)',  # Hebrew
        ]
        
        for pattern in premium_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = self._parse_amount(match.group(1))
                if 'annual' in pattern.lower() or 'שנתי' in pattern:
                    financial['premium_annual'] = amount
                elif 'monthly' in pattern.lower():
                    financial['premium_monthly'] = amount
        
        # Deductible patterns
        deductible_patterns = [
            r'(?:Deductible|Self Risk):\s*\$?([\d,\.]+)',
            r'(?:השתתפות עצמית):\s*₪?([\d,\.]+)',  # Hebrew
        ]
        
        for pattern in deductible_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                financial['deductible'] = self._parse_amount(match.group(1))
                break
        
        return financial
    
    def _extract_terms_and_conditions(self, text: str) -> str:
        """Extract key terms and conditions"""
        # Look for terms section
        terms_patterns = [
            r'(?:Terms and Conditions|General Conditions|Policy Conditions)(.*?)(?:Signatures?|End of Policy|Page \d+)',
            r'(?:תנאי הפוליסה|תנאים כלליים)(.*?)(?:חתימות?|סוף הפוליסה|עמוד \d+)',  # Hebrew
        ]
        
        for pattern in terms_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()[:2000]  # Limit length
        
        # Fallback: extract first 1000 characters as summary
        return text[:1000] + "..." if len(text) > 1000 else text
    
    def _extract_exclusions(self, text: str) -> List[str]:
        """Extract policy exclusions"""
        exclusions = []
        exclusion_patterns = [
            r'(?:Exclusions?|Not Covered|Excluded):\s*([^\n]+)',
            r'(?:אינו מכוסה|החרגות):\s*([^\n]+)',  # Hebrew
        ]
        
        for pattern in exclusion_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            exclusions.extend(matches)
        
        return exclusions
    
    def _extract_additional_benefits(self, text: str) -> List[str]:
        """Extract additional benefits and riders"""
        benefits = []
        benefit_patterns = [
            r'(?:Additional Benefits?|Riders?|Optional Coverage):\s*([^\n]+)',
            r'(?:הטבות נוספות|כיסויים אופציונליים):\s*([^\n]+)',  # Hebrew
        ]
        
        for pattern in benefit_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            benefits.extend(matches)
        
        return benefits
    
    def _detect_language(self, text: str) -> str:
        """Detect text language"""
        # Simple Hebrew detection
        hebrew_chars = len(re.findall(r'[\u0590-\u05FF]', text))
        total_chars = len(re.findall(r'[a-zA-Z\u0590-\u05FF]', text))
        
        if total_chars > 0 and hebrew_chars / total_chars > 0.3:
            return "he"  # Hebrew
        return "en"  # Default to English
    
    def _calculate_confidence(self, text: str, basic_info: Dict, coverage: Dict) -> float:
        """Calculate extraction confidence score"""
        score = 0.0
        
        # Basic info scoring
        if basic_info.get('policy_number'):
            score += 0.3
        if basic_info.get('insurer'):
            score += 0.2
        if basic_info.get('owner_name'):
            score += 0.2
        if basic_info.get('start_date') and basic_info.get('end_date'):
            score += 0.2
        
        # Coverage scoring
        if coverage:
            score += min(0.1, len(coverage) * 0.02)
        
        return min(1.0, score)
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse monetary amount from string"""
        try:
            # Remove commas and non-digit characters except decimal point
            clean_amount = re.sub(r'[^\d\.]', '', amount_str)
            return float(clean_amount) if clean_amount else 0.0
        except:
            return 0.0
    
    def _create_fallback_analysis(self, text: str) -> Dict[str, Any]:
        """Create basic analysis when detailed extraction fails"""
        return {
            "basic_info": {},
            "coverage_details": {},
            "financial_info": {},
            "terms_and_conditions": text[:1000] + "..." if len(text) > 1000 else text,
            "language": self._detect_language(text),
            "extraction_confidence": 0.1,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "policy_type": "unknown"
        }

    def _extract_vehicle_information(self, text: str) -> Dict[str, Any]:
        """Extract vehicle-specific information for auto policies"""
        vehicle = {}
        
        vehicle_patterns = [
            r'(?:Year|Model\s*Year):\s*([0-9]{4})',
            r'(?:Make|Manufacturer):\s*([A-Za-z\s]+)',
            r'(?:Model):\s*([A-Za-z0-9\s\-]+)',
            r'(?:VIN|Vehicle\s*ID):\s*([A-Z0-9]{17})',
            r'(?:License\s*Plate):\s*([A-Z0-9\-\s]+)',
            r'(?:Mileage|Odometer):\s*([\d,]+)',
        ]
        
        for pattern in vehicle_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if 'year' in pattern.lower():
                    vehicle['year'] = matches[0].strip()
                elif 'make' in pattern.lower() or 'manufacturer' in pattern.lower():
                    vehicle['make'] = matches[0].strip()
                elif 'model' in pattern.lower() and 'year' not in pattern.lower():
                    vehicle['model'] = matches[0].strip()
                elif 'vin' in pattern.lower():
                    vehicle['vin'] = matches[0].strip()
                elif 'license' in pattern.lower() or 'plate' in pattern.lower():
                    vehicle['license_plate'] = matches[0].strip()
                elif 'mileage' in pattern.lower() or 'odometer' in pattern.lower():
                    vehicle['mileage'] = matches[0].strip()
        
        return vehicle

    def _extract_property_information(self, text: str) -> Dict[str, Any]:
        """Extract property-specific information for home policies"""
        property_info = {}
        
        property_patterns = [
            r'(?:Property\s*Address|Address):\s*([^\n\r]{10,100})',
            r'(?:Year\s*Built|Construction\s*Year):\s*([0-9]{4})',
            r'(?:Square\s*Feet|Sq\s*Ft):\s*([\d,]+)',
            r'(?:Construction\s*Type|Building\s*Type):\s*([A-Za-z\s]+)',
            r'(?:Roof\s*Type):\s*([A-Za-z\s]+)',
            r'(?:Foundation\s*Type):\s*([A-Za-z\s]+)',
            r'(?:Number\s*of\s*Stories):\s*([0-9\.]+)',
        ]
        
        for pattern in property_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if 'address' in pattern.lower():
                    property_info['property_address'] = matches[0].strip()
                elif 'year' in pattern.lower():
                    property_info['year_built'] = matches[0].strip()
                elif 'square' in pattern.lower() or 'sq' in pattern.lower():
                    property_info['square_feet'] = matches[0].strip()
                elif 'construction' in pattern.lower() or 'building' in pattern.lower():
                    property_info['construction_type'] = matches[0].strip()
                elif 'roof' in pattern.lower():
                    property_info['roof_type'] = matches[0].strip()
                elif 'foundation' in pattern.lower():
                    property_info['foundation_type'] = matches[0].strip()
                elif 'stories' in pattern.lower():
                    property_info['stories'] = matches[0].strip()
        
        return property_info

    def _extract_health_information(self, text: str) -> Dict[str, Any]:
        """Extract health-specific information"""
        health = {}
        
        health_patterns = [
            r'(?:Group\s*Number|Group\s*ID):\s*([A-Z0-9\-]+)',
            r'(?:Member\s*ID|Subscriber\s*ID):\s*([A-Z0-9\-]+)',
            r'(?:Plan\s*Type|Plan\s*Name):\s*([A-Za-z0-9\s\-]+)',
            r'(?:Network|Provider\s*Network):\s*([A-Za-z\s]+)',
            r'(?:PCP|Primary\s*Care\s*Physician):\s*([A-Za-z\s,\.]+)',
            r'(?:Copay|Co[\-\s]*pay):\s*\$?([\d,]+)',
            r'(?:Out[\-\s]*of[\-\s]*Pocket\s*Maximum):\s*\$?([\d,]+)',
        ]
        
        for pattern in health_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if 'group' in pattern.lower():
                    health['group_number'] = matches[0].strip()
                elif 'member' in pattern.lower() or 'subscriber' in pattern.lower():
                    health['member_id'] = matches[0].strip()
                elif 'plan' in pattern.lower():
                    health['plan_type'] = matches[0].strip()
                elif 'network' in pattern.lower():
                    health['network'] = matches[0].strip()
                elif 'pcp' in pattern.lower() or 'primary' in pattern.lower():
                    health['primary_care_physician'] = matches[0].strip()
                elif 'copay' in pattern.lower():
                    health['copay'] = self._parse_amount(matches[0])
                elif 'pocket' in pattern.lower():
                    health['out_of_pocket_max'] = self._parse_amount(matches[0])
        
        return health

    def _extract_life_insurance_information(self, text: str) -> Dict[str, Any]:
        """Extract life insurance specific information"""
        life = {}
        
        life_patterns = [
            r'(?:Death\s*Benefit|Face\s*Amount):\s*\$?([\d,]+)',
            r'(?:Cash\s*Value):\s*\$?([\d,]+)',
            r'(?:Policy\s*Type):\s*([A-Za-z\s]+)',
            r'(?:Premium\s*Mode):\s*([A-Za-z\s]+)',
            r'(?:Dividend\s*Option):\s*([A-Za-z\s]+)',
            r'(?:Loan\s*Value):\s*\$?([\d,]+)',
        ]
        
        for pattern in life_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if 'death' in pattern.lower() or 'face' in pattern.lower():
                    life['death_benefit'] = self._parse_amount(matches[0])
                elif 'cash' in pattern.lower():
                    life['cash_value'] = self._parse_amount(matches[0])
                elif 'type' in pattern.lower():
                    life['policy_type'] = matches[0].strip()
                elif 'mode' in pattern.lower():
                    life['premium_mode'] = matches[0].strip()
                elif 'dividend' in pattern.lower():
                    life['dividend_option'] = matches[0].strip()
                elif 'loan' in pattern.lower():
                    life['loan_value'] = self._parse_amount(matches[0])
        
        return life

    def _extract_business_information(self, text: str) -> Dict[str, Any]:
        """Extract business insurance specific information"""
        business = {}
        
        business_patterns = [
            r'(?:Business\s*Name|Company\s*Name):\s*([^\n\r]{3,50})',
            r'(?:Industry\s*Type|Business\s*Type):\s*([A-Za-z\s]+)',
            r'(?:Number\s*of\s*Employees):\s*([\d,]+)',
            r'(?:Annual\s*Revenue|Gross\s*Revenue):\s*\$?([\d,]+)',
            r'(?:FEIN|Tax\s*ID):\s*([0-9\-]+)',
            r'(?:SIC\s*Code|NAICS\s*Code):\s*([0-9]+)',
        ]
        
        for pattern in business_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if 'business' in pattern.lower() or 'company' in pattern.lower():
                    business['business_name'] = matches[0].strip()
                elif 'industry' in pattern.lower() or 'type' in pattern.lower():
                    business['industry_type'] = matches[0].strip()
                elif 'employees' in pattern.lower():
                    business['num_employees'] = matches[0].strip()
                elif 'revenue' in pattern.lower():
                    business['annual_revenue'] = self._parse_amount(matches[0])
                elif 'fein' in pattern.lower() or 'tax' in pattern.lower():
                    business['tax_id'] = matches[0].strip()
                elif 'sic' in pattern.lower() or 'naics' in pattern.lower():
                    business['industry_code'] = matches[0].strip()
        
        return business

    def _calculate_extraction_confidence(self, analysis: Dict[str, Any], text: str) -> float:
        """Calculate confidence score based on extracted parameters"""
        total_sections = len(analysis)
        filled_sections = sum(1 for section in analysis.values() if section and len(section) > 0)
        
        # Count total parameters extracted
        total_params = 0
        for section in analysis.values():
            if isinstance(section, dict):
                total_params += len([v for v in section.values() if v])
        
        # Base confidence on text length and parameter extraction
        text_confidence = min(len(text) / 5000, 1.0)  # Longer text = higher confidence
        param_confidence = min(total_params / 50, 1.0)  # More params = higher confidence
        section_confidence = filled_sections / total_sections
        
        # Weighted average
        confidence = (text_confidence * 0.3 + param_confidence * 0.5 + section_confidence * 0.2)
        return round(confidence, 2)

    def _count_extracted_parameters(self, analysis: Dict[str, Any]) -> int:
        """Count total number of extracted parameters"""
        count = 0
        for section in analysis.values():
            if isinstance(section, dict):
                count += len([v for v in section.values() if v])
            elif section:
                count += 1
        return count

    def _detect_document_language(self, text: str) -> str:
        """Enhanced language detection"""
        hebrew_chars = len(re.findall(r'[\u0590-\u05FF]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(text)
        
        if total_chars == 0:
            return "unknown"
        
        hebrew_ratio = hebrew_chars / total_chars
        english_ratio = english_chars / total_chars
        
        if hebrew_ratio > 0.1:
            return "he"
        elif english_ratio > 0.5:
            return "en"
        else:
            return "mixed"

def parse_csv(lines) -> List[Dict]:
    """Parse CSV policy data"""
    reader = csv.DictReader(lines)
    rows = []
    for row in reader:
        rows.append({
            "owner_name": row.get("owner_name","").strip(),
            "insurer": row.get("insurer","").strip(),
            "product_type": normalize_product(row.get("product_type","").strip()),
            "policy_number": row.get("policy_number","").strip(),
            "start_date": row.get("start_date","").strip(),
            "end_date": row.get("end_date","").strip(),
            "premium_monthly": float(row.get("premium_monthly",0) or 0),
            "deductible": float(row.get("deductible",0) or 0),
            "coverage_limit": float(row.get("coverage_limit",0) or 0),
            "notes": row.get("notes","").strip()
        })
    return rows

def normalize_product(product: str) -> str:
    """Normalize product type names"""
    m = product.strip().lower()
    aliases = {
        "auto": ["car","vehicle","auto","רכב"],
        "home": ["home","house","property","בית","דירה"],
        "health": ["health","medical","בריאות","רפואי"],
        "life": ["life","term life","whole life","חיים"],
        "disability": ["disability","income protection","נכות"]
    }
    for key, vals in aliases.items():
        if m in vals:
            return key
    return m

# Initialize global analyzer
policy_analyzer = PolicyAnalyzer()