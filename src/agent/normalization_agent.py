"""
TaxFacts Normalization Agent

Responsibility:
Merge partial data from multiple sources (UI, documents, chat) into a single
canonical TaxFacts object with full provenance tracking.

Design Principles:
- Deterministic: Same inputs → Same output (no randomness, no inference)
- Auditable: Every field's source and confidence tracked
- User-controlled: No automatic overrides; conflicts flagged for user review
- Non-invasive: No LLM calls, no tax calculations
- Fail-safe: Missing data → defaults, not inferred values

Data Sources:
  'form16'    - Extracted from Form 16 document
  'manual'    - User entered via UI
  'extracted' - Extracted from other documents (bank statement, etc.)
  'chat'      - Clarified via chat
  'default'   - Not provided; using default value
"""

from typing import Dict, Optional, Tuple, List
from datetime import datetime
from src.core.taxfacts import TaxFacts, UserIdentity, TaxFactsWithIdentity


class ConflictRecord:
    """Tracks a single data conflict for user review."""
    
    def __init__(self, field_name: str, sources: Dict[str, any]):
        self.field_name = field_name
        self.sources = sources  # {source: value, source: value, ...}
        self.resolution = None  # Which source was chosen
        self.user_reviewed = False
    
    def __repr__(self):
        sources_str = " | ".join([f"{k}={v}" for k, v in self.sources.items()])
        return f"Conflict({self.field_name}: {sources_str}) → chosen: {self.resolution}"


class NormalizationResult:
    """Result of normalization with full provenance."""
    
    def __init__(self, tax_facts: TaxFacts, conflicts: List[ConflictRecord] = None):
        self.tax_facts = tax_facts
        self.conflicts = conflicts or []
        self.has_unresolved_conflicts = any(not c.user_reviewed for c in self.conflicts)
    
    def __repr__(self):
        conflict_str = f", {len(self.conflicts)} conflicts" if self.conflicts else ""
        return f"NormalizationResult(tax_facts={self.tax_facts}, {conflict_str})"


class TaxFactsNormalizationAgent:
    """
    Normalizes partial TaxFacts from multiple sources into a single canonical object.
    
    Workflow:
    1. Accept partial inputs from UI, documents, chat
    2. For each field: gather values from all sources
    3. Resolve conflicts: prefer manual > extracted > form16 > chat > default
    4. Populate source_mapping and confidence_mapping
    5. Return normalized TaxFacts with conflict log
    
    Note: User-entered values (manual) ALWAYS win conflicts.
    """
    
    # Priority order for conflict resolution (higher = preferred)
    SOURCE_PRIORITY = {
        'manual': 4,      # User-entered via UI (highest trust)
        'form16': 3,      # Extracted from Form 16 (usually reliable)
        'extracted': 2,   # Extracted from other documents (less reliable)
        'chat': 1,        # Clarified via chat (needs verification)
        'default': 0,     # Not provided; using default (lowest trust)
    }
    
    # Confidence scores per source
    CONFIDENCE_SCORES = {
        'manual': 1.0,      # User explicitly entered
        'form16': 0.95,     # High-quality structured document
        'extracted': 0.70,  # Extracted from semi-structured data
        'chat': 0.60,       # User clarification but may be approximate
        'default': 0.0,     # No actual data
    }
    
    def __init__(self):
        """Initialize the normalization agent."""
        self.conflicts: List[ConflictRecord] = []
    
    def normalize(
        self,
        user_input: Optional[Dict] = None,
        form16_data: Optional[Dict] = None,
        extracted_data: Optional[Dict] = None,
        chat_data: Optional[Dict] = None,
        user_identity: Optional[UserIdentity] = None,
    ) -> NormalizationResult:
        """
        Normalize TaxFacts from multiple sources.
        
        Args:
            user_input (Dict): Partial TaxFacts from UI (manual entry)
            form16_data (Dict): Extracted from Form 16 document
            extracted_data (Dict): Extracted from other documents
            chat_data (Dict): Clarifications from chat
            user_identity (UserIdentity): Identity info (TIER 3)
        
        Returns:
            NormalizationResult: Normalized TaxFacts with conflict log
        
        Priority for conflicts: manual > form16 > extracted > chat > default
        """
        
        # Merge all sources into single dict
        merged_data = {}
        
        # Track which sources have data
        sources = {
            'manual': user_input or {},
            'form16': form16_data or {},
            'extracted': extracted_data or {},
            'chat': chat_data or {},
        }
        
        # Get all field names from TaxFacts
        tax_facts_fields = self._get_all_fields(TaxFacts)
        source_mapping = {}
        confidence_mapping = {}
        
        # Process each field
        for field_name in tax_facts_fields:
            # Skip metadata fields - they'll be set explicitly
            if field_name in ['source_mapping', 'confidence_mapping', 'last_modified']:
                continue
            
            # Gather values from all sources for this field
            available_values = {}
            for source_name, source_data in sources.items():
                if field_name in source_data and source_data[field_name] is not None:
                    available_values[source_name] = source_data[field_name]
            
            # Resolve value and source
            value, chosen_source = self._resolve_field(field_name, available_values)
            
            # Add to merged data
            merged_data[field_name] = value
            
            # Track source and confidence
            if chosen_source != 'default':
                source_mapping[field_name] = chosen_source
                confidence_mapping[field_name] = self.CONFIDENCE_SCORES[chosen_source]
            else:
                # Field not provided in any source; using default
                source_mapping[field_name] = 'default'
                confidence_mapping[field_name] = 0.0
            
            # Flag conflicts if multiple sources disagree
            if len(available_values) > 1:
                conflict = ConflictRecord(field_name, available_values)
                conflict.resolution = chosen_source
                conflict.user_reviewed = (chosen_source == 'manual')  # Manual is auto-approved
                self.conflicts.append(conflict)
        
        # Explicitly set metadata
        merged_data['source_mapping'] = source_mapping
        merged_data['confidence_mapping'] = confidence_mapping
        merged_data['last_modified'] = datetime.now()
        
        # Create TaxFacts with merged data
        normalized = TaxFacts(**merged_data)
        
        # Return result with conflicts
        return NormalizationResult(normalized, self.conflicts)
    
    def _resolve_field(
        self, 
        field_name: str, 
        available_values: Dict[str, any]
    ) -> Tuple[any, str]:
        """
        Resolve a single field value from multiple sources.
        
        Rules:
        1. If only one source has value, use it
        2. If multiple sources agree on value, use it
        3. If multiple sources disagree:
           - ALWAYS prefer 'manual' (user-entered)
           - Then prefer by SOURCE_PRIORITY order
           - FLAG the conflict
        
        Args:
            field_name (str): Name of the field
            available_values (Dict): {source: value, source: value, ...}
        
        Returns:
            (value, chosen_source): Resolved value and source name
        """
        
        # No values provided; use default
        if not available_values:
            default_value = self._get_default_value(field_name)
            return default_value, 'default'
        
        # Single source; use it
        if len(available_values) == 1:
            source = list(available_values.keys())[0]
            return available_values[source], source
        
        # Multiple sources: check if they agree
        unique_values = set(str(v) for v in available_values.values())
        
        if len(unique_values) == 1:
            # All sources agree on same value; use any
            source = list(available_values.keys())[0]
            return available_values[source], source
        
        # Multiple sources disagree: apply priority
        # Always prefer 'manual' if available
        if 'manual' in available_values:
            return available_values['manual'], 'manual'
        
        # Otherwise, prefer by SOURCE_PRIORITY
        sorted_sources = sorted(
            available_values.keys(),
            key=lambda s: self.SOURCE_PRIORITY.get(s, -1),
            reverse=True
        )
        chosen_source = sorted_sources[0]
        return available_values[chosen_source], chosen_source
    
    def _get_all_fields(self, model_class) -> List[str]:
        """Get all field names from a Pydantic model."""
        return list(model_class.__fields__.keys())
    
    def _get_default_value(self, field_name: str) -> any:
        """Get default value for a field from TaxFacts schema."""
        field = TaxFacts.__fields__.get(field_name)
        if field:
            if field.default is not None:
                return field.default
            elif field.default_factory is not None:
                return field.default_factory()
            else:
                return None
        return None
    
    def get_conflicts_summary(self) -> str:
        """Return human-readable summary of conflicts."""
        if not self.conflicts:
            return "No conflicts detected."
        
        lines = [f"Found {len(self.conflicts)} conflict(s):"]
        unresolved = [c for c in self.conflicts if not c.user_reviewed]
        
        for conflict in unresolved:
            lines.append(f"  ⚠️  {conflict}")
        
        if unresolved:
            lines.append(f"\n⚠️  {len(unresolved)} unresolved conflict(s). Review before proceeding.")
        
        return "\n".join(lines)


def normalize_tax_facts(
    user_input: Optional[Dict] = None,
    form16_data: Optional[Dict] = None,
    extracted_data: Optional[Dict] = None,
    chat_data: Optional[Dict] = None,
    user_identity: Optional[UserIdentity] = None,
) -> NormalizationResult:
    """
    Convenience function to normalize TaxFacts.
    
    Usage:
        result = normalize_tax_facts(
            user_input=partial_tax_facts_dict,
            form16_data=extracted_form16_dict,
        )
        
        if result.has_unresolved_conflicts:
            print(result.tax_facts.conflicts)  # Review conflicts
        
        tax_facts = result.tax_facts  # Use normalized TaxFacts
    
    Args:
        user_input: Partial TaxFacts from UI
        form16_data: Data extracted from Form 16
        extracted_data: Data extracted from other documents
        chat_data: Data from chat clarifications
        user_identity: Identity and UI-only fields
    
    Returns:
        NormalizationResult: Normalized TaxFacts with full provenance
    """
    agent = TaxFactsNormalizationAgent()
    return agent.normalize(
        user_input=user_input,
        form16_data=form16_data,
        extracted_data=extracted_data,
        chat_data=chat_data,
        user_identity=user_identity,
    )


# =========================================================================
# Example usage (for testing/documentation)
# =========================================================================

if __name__ == "__main__":
    """
    Example: Normalizing data from UI, Form 16, and chat.
    """
    
    # User entered via UI
    user_input = {
        'assessment_year': '2025-26',
        'residential_status': 'resident',
        'age_category': 'below_60',
        'salary_gross': 1200000,
        'deduction_80c': 150000,
    }
    
    # Extracted from Form 16
    form16_data = {
        'assessment_year': '2025-26',
        'salary_gross': 1500000,  # Conflicts with user input!
        'salary_standard_deduction_claim': True,
        'taxes_tds': 200000,
    }
    
    # Chat clarification
    chat_data = {
        'home_loan_interest_paid': 100000,
        'deduction_80d_self': 25000,
    }
    
    # Normalize
    result = normalize_tax_facts(
        user_input=user_input,
        form16_data=form16_data,
        chat_data=chat_data,
    )
    
    # Check conflicts
    print(result.get_conflicts_summary())
    
    # Use normalized TaxFacts
    print("\nNormalized TaxFacts:")
    print(f"  Salary: ₹{result.tax_facts.salary_gross:,.0f} (source: {result.tax_facts.source_mapping.get('salary_gross')})")
    print(f"  80C Deduction: ₹{result.tax_facts.deduction_80c:,.0f} (source: {result.tax_facts.source_mapping.get('deduction_80c')})")
    print(f"  Home Loan Interest: ₹{result.tax_facts.home_loan_interest_paid:,.0f} (source: {result.tax_facts.source_mapping.get('home_loan_interest_paid')})")
