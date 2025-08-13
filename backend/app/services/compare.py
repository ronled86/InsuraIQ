"""
Policy Comparison Service
Provides intelligent comparison between multiple insurance policies
"""

import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models import Policy
import logging

logger = logging.getLogger(__name__)

class PolicyComparisonService:
    """Service for comparing multiple insurance policies"""
    
    def __init__(self):
        self.comparison_categories = [
            "basic_information",
            "coverage_details", 
            "financial_terms",
            "policy_limits",
            "deductibles",
            "exclusions",
            "additional_benefits",
            "terms_and_conditions"
        ]
    
    def compare_policies(self, db: Session, policy_ids: List[int], user_id: str) -> Dict[str, Any]:
        """
        Compare multiple policies and return structured comparison
        
        Args:
            db: Database session
            policy_ids: List of policy IDs to compare
            user_id: User ID for authorization
            
        Returns:
            Dict containing comprehensive policy comparison
        """
        try:
            # Fetch policies
            policies = db.query(Policy).filter(
                Policy.id.in_(policy_ids),
                Policy.user_id == user_id
            ).all()
            
            if len(policies) < 2:
                raise ValueError("At least 2 policies are required for comparison")
            
            # Create comparison structure
            comparison = {
                "policies": [self._serialize_policy_for_comparison(p) for p in policies],
                "comparison_matrix": self._create_comparison_matrix(policies),
                "summary": self._create_comparison_summary(policies),
                "recommendations": self._generate_recommendations(policies)
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Policy comparison failed: {str(e)}")
            raise
    
    def _serialize_policy_for_comparison(self, policy: Policy) -> Dict[str, Any]:
        """Serialize policy for comparison display"""
        coverage_details = {}
        if policy.coverage_details:
            try:
                coverage_details = json.loads(policy.coverage_details) if isinstance(policy.coverage_details, str) else policy.coverage_details
            except:
                coverage_details = {}
        
        return {
            "id": policy.id,
            "owner_name": policy.owner_name,
            "insurer": policy.insurer,
            "product_type": policy.product_type,
            "policy_number": policy.policy_number,
            "start_date": policy.start_date,
            "end_date": policy.end_date,
            "premium_monthly": policy.premium_monthly,
            "premium_annual": policy.premium_annual,
            "deductible": policy.deductible,
            "coverage_limit": policy.coverage_limit,
            "coverage_details": coverage_details,
            "policy_language": policy.policy_language,
            "terms_and_conditions": policy.terms_and_conditions,
            "original_filename": policy.original_filename
        }
    
    def _create_comparison_matrix(self, policies: List[Policy]) -> Dict[str, Any]:
        """Create detailed comparison matrix"""
        matrix = {}
        
        # Basic information comparison
        matrix["basic_information"] = self._compare_basic_info(policies)
        
        # Financial comparison
        matrix["financial_terms"] = self._compare_financial_terms(policies)
        
        # Coverage comparison
        matrix["coverage_comparison"] = self._compare_coverage_details(policies)
        
        # Exclusions comparison
        matrix["exclusions"] = self._compare_exclusions(policies)
        
        return matrix
    
    def _compare_basic_info(self, policies: List[Policy]) -> Dict[str, Any]:
        """Compare basic policy information"""
        comparison = {
            "policy_holders": [p.owner_name for p in policies],
            "insurers": [p.insurer for p in policies],
            "policy_types": [p.product_type for p in policies],
            "policy_numbers": [p.policy_number for p in policies],
            "coverage_periods": [
                f"{p.start_date} to {p.end_date}" if p.start_date and p.end_date 
                else "Not specified" for p in policies
            ],
            "languages": [p.policy_language or "en" for p in policies]
        }
        
        # Add analysis
        comparison["analysis"] = {
            "same_insurer": len(set(comparison["insurers"])) == 1,
            "same_type": len(set(comparison["policy_types"])) == 1,
            "different_languages": len(set(comparison["languages"])) > 1
        }
        
        return comparison
    
    def _compare_financial_terms(self, policies: List[Policy]) -> Dict[str, Any]:
        """Compare financial aspects of policies"""
        comparison = {
            "monthly_premiums": [p.premium_monthly or 0 for p in policies],
            "annual_premiums": [p.premium_annual or 0 for p in policies], 
            "deductibles": [p.deductible or 0 for p in policies],
            "coverage_limits": [p.coverage_limit or 0 for p in policies]
        }
        
        # Add financial analysis
        comparison["analysis"] = {
            "cheapest_monthly": min(comparison["monthly_premiums"]) if any(comparison["monthly_premiums"]) else 0,
            "most_expensive_monthly": max(comparison["monthly_premiums"]) if any(comparison["monthly_premiums"]) else 0,
            "lowest_deductible": min(comparison["deductibles"]) if any(comparison["deductibles"]) else 0,
            "highest_coverage_limit": max(comparison["coverage_limits"]) if any(comparison["coverage_limits"]) else 0,
            "cost_difference_monthly": max(comparison["monthly_premiums"]) - min(comparison["monthly_premiums"]) if any(comparison["monthly_premiums"]) else 0
        }
        
        return comparison
    
    def _compare_coverage_details(self, policies: List[Policy]) -> Dict[str, Any]:
        """Compare coverage details across policies"""
        all_coverage_types = set()
        policy_coverages = []
        
        # Extract all coverage types and policy-specific coverage
        for policy in policies:
            coverage = {}
            if policy.coverage_details:
                try:
                    coverage = json.loads(policy.coverage_details) if isinstance(policy.coverage_details, str) else policy.coverage_details
                except:
                    coverage = {}
            
            policy_coverages.append(coverage)
            all_coverage_types.update(coverage.keys())
        
        # Create coverage comparison matrix
        coverage_matrix = {}
        for coverage_type in all_coverage_types:
            coverage_matrix[coverage_type] = []
            for policy_coverage in policy_coverages:
                if coverage_type in policy_coverage:
                    coverage_data = policy_coverage[coverage_type]
                    if isinstance(coverage_data, dict):
                        coverage_matrix[coverage_type].append({
                            "covered": True,
                            "amount": coverage_data.get("amount", "Not specified"),
                            "description": coverage_data.get("description", coverage_type)
                        })
                    else:
                        coverage_matrix[coverage_type].append({
                            "covered": True,
                            "amount": coverage_data,
                            "description": coverage_type
                        })
                else:
                    coverage_matrix[coverage_type].append({
                        "covered": False,
                        "amount": None,
                        "description": f"{coverage_type} not covered"
                    })
        
        return {
            "coverage_matrix": coverage_matrix,
            "unique_coverages": self._find_unique_coverages(coverage_matrix),
            "common_coverages": self._find_common_coverages(coverage_matrix),
            "coverage_gaps": self._find_coverage_gaps(coverage_matrix)
        }
    
    def _compare_exclusions(self, policies: List[Policy]) -> Dict[str, Any]:
        """Compare policy exclusions"""
        exclusions_comparison = []
        
        for policy in policies:
            exclusions = []
            if policy.coverage_details:
                try:
                    coverage = json.loads(policy.coverage_details) if isinstance(policy.coverage_details, str) else policy.coverage_details
                    exclusions = coverage.get("exclusions", [])
                except:
                    exclusions = []
            
            exclusions_comparison.append({
                "policy_id": policy.id,
                "exclusions": exclusions
            })
        
        return {
            "policy_exclusions": exclusions_comparison,
            "common_exclusions": self._find_common_exclusions(exclusions_comparison),
            "unique_exclusions": self._find_unique_exclusions(exclusions_comparison)
        }
    
    def _find_unique_coverages(self, coverage_matrix: Dict) -> Dict[str, List[int]]:
        """Find coverages that are unique to specific policies"""
        unique = {}
        for coverage_type, policy_coverages in coverage_matrix.items():
            covered_policies = [i for i, cov in enumerate(policy_coverages) if cov["covered"]]
            if len(covered_policies) == 1:
                unique[coverage_type] = covered_policies
        return unique
    
    def _find_common_coverages(self, coverage_matrix: Dict) -> List[str]:
        """Find coverages that are common to all policies"""
        common = []
        for coverage_type, policy_coverages in coverage_matrix.items():
            if all(cov["covered"] for cov in policy_coverages):
                common.append(coverage_type)
        return common
    
    def _find_coverage_gaps(self, coverage_matrix: Dict) -> Dict[str, List[int]]:
        """Find coverage gaps (not covered by some policies)"""
        gaps = {}
        for coverage_type, policy_coverages in coverage_matrix.items():
            uncovered_policies = [i for i, cov in enumerate(policy_coverages) if not cov["covered"]]
            if uncovered_policies and len(uncovered_policies) < len(policy_coverages):
                gaps[coverage_type] = uncovered_policies
        return gaps
    
    def _find_common_exclusions(self, exclusions_data: List[Dict]) -> List[str]:
        """Find exclusions common to all policies"""
        if not exclusions_data:
            return []
        
        common = set(exclusions_data[0]["exclusions"])
        for policy_exclusions in exclusions_data[1:]:
            common &= set(policy_exclusions["exclusions"])
        
        return list(common)
    
    def _find_unique_exclusions(self, exclusions_data: List[Dict]) -> Dict[int, List[str]]:
        """Find exclusions unique to each policy"""
        unique = {}
        
        for i, policy_data in enumerate(exclusions_data):
            policy_exclusions = set(policy_data["exclusions"])
            other_exclusions = set()
            
            for j, other_policy in enumerate(exclusions_data):
                if i != j:
                    other_exclusions.update(other_policy["exclusions"])
            
            unique_to_policy = policy_exclusions - other_exclusions
            if unique_to_policy:
                unique[policy_data["policy_id"]] = list(unique_to_policy)
        
        return unique
    
    def _create_comparison_summary(self, policies: List[Policy]) -> Dict[str, Any]:
        """Create high-level comparison summary"""
        return {
            "total_policies": len(policies),
            "policy_types": list(set(p.product_type for p in policies)),
            "insurers": list(set(p.insurer for p in policies)),
            "languages": list(set(p.policy_language or "en" for p in policies)),
            "date_range": {
                "earliest_start": min((p.start_date for p in policies if p.start_date), default=None),
                "latest_end": max((p.end_date for p in policies if p.end_date), default=None)
            },
            "premium_range": {
                "lowest_monthly": min((p.premium_monthly for p in policies if p.premium_monthly), default=0),
                "highest_monthly": max((p.premium_monthly for p in policies if p.premium_monthly), default=0)
            }
        }
    
    def _generate_recommendations(self, policies: List[Policy]) -> List[str]:
        """Generate comparison recommendations"""
        recommendations = []
        
        # Premium comparison
        monthly_premiums = [p.premium_monthly for p in policies if p.premium_monthly]
        if monthly_premiums:
            min_premium = min(monthly_premiums)
            max_premium = max(monthly_premiums)
            if max_premium > min_premium * 1.5:  # More than 50% difference
                recommendations.append(f"Significant premium difference detected: ${min_premium:.2f} vs ${max_premium:.2f} monthly")
        
        # Coverage gaps
        recommendations.append("Review coverage details for gaps and overlaps")
        
        # Language considerations
        languages = set(p.policy_language or "en" for p in policies)
        if len(languages) > 1:
            recommendations.append("Policies are in different languages - ensure you understand all terms")
        
        # Insurer diversity
        insurers = set(p.insurer for p in policies)
        if len(insurers) == 1:
            recommendations.append("All policies are with the same insurer - consider diversifying for risk management")
        
        return recommendations

# Legacy function for backward compatibility
def compare_policies(policies: List[Dict]) -> Dict:
    """Legacy comparison function"""
    table = []
    for p in policies:
        premium = p.get("premium_monthly") or 0.0
        cov = p.get("coverage_limit") or 0.0
        ratio = cov / max(premium, 1)
        table.append({
            "id": p["id"],
            "insurer": p["insurer"],
            "product_type": p["product_type"],
            "premium_monthly": premium,
            "deductible": p.get("deductible",0.0),
            "coverage_limit": cov,
            "coverage_per_shekel": round(ratio, 2)
        })
    table.sort(key=lambda r: (-r["coverage_per_shekel"], r["deductible"]))
    summary = "Sorted by coverage per currency then deductible."
    return {"summary": summary, "table": table}

# Global service instance
comparison_service = PolicyComparisonService()