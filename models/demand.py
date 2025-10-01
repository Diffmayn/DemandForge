"""Pydantic models for DemandForge tabs and demand structure."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class PowerInterest(str, Enum):
    """Stakeholder power-interest classification."""
    HIGH_HIGH = "High Power/High Interest"
    HIGH_LOW = "High Power/Low Interest"
    LOW_HIGH = "Low Power/High Interest"
    LOW_LOW = "Low Power/Low Interest"


class RiskSeverity(str, Enum):
    """Risk severity levels."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Stakeholder(BaseModel):
    """Stakeholder information."""
    name: str = Field(max_length=100)
    role: str = Field(max_length=100)
    power_interest: PowerInterest = PowerInterest.LOW_LOW
    email: Optional[str] = Field(None, max_length=200)


class IdeationTab(BaseModel):
    """Ideation phase data."""
    problem_statement: str = Field(default="", max_length=2000)
    goals: str = Field(default="", max_length=1000)
    background: str = Field(default="", max_length=1500)
    constraints: str = Field(default="", max_length=1000)
    
    @field_validator('problem_statement', 'goals')
    @classmethod
    def validate_not_empty_critical(cls, v: str, info) -> str:
        """Validate critical fields are not just whitespace."""
        if info.field_name in ['problem_statement'] and v and not v.strip():
            raise ValueError(f"{info.field_name} cannot be only whitespace")
        return v


class RequirementsTab(BaseModel):
    """Requirements phase data."""
    stakeholders: List[Stakeholder] = Field(default_factory=list, max_length=50)
    user_stories: str = Field(default="", max_length=5000)
    features: List[str] = Field(default_factory=list, max_length=100)
    acceptance_criteria: str = Field(default="", max_length=3000)
    vision_document: str = Field(default="", max_length=5000)
    non_functional_requirements: str = Field(default="", max_length=2000)


class AssessmentTab(BaseModel):
    """Assessment phase data."""
    business_case: str = Field(default="", max_length=2000)
    roi_percentage: Optional[float] = Field(None, ge=0, le=1000)
    estimated_cost: Optional[float] = Field(None, ge=0)
    estimated_duration_weeks: Optional[int] = Field(None, ge=0, le=520)
    risks: str = Field(default="", max_length=3000)
    dependencies: str = Field(default="", max_length=2000)
    assumptions: str = Field(default="", max_length=2000)


class DesignTab(BaseModel):
    """Design phase data."""
    architecture_overview: str = Field(default="", max_length=5000)
    technical_stack: str = Field(default="", max_length=1500)
    wireframes_paths: List[str] = Field(default_factory=list, max_length=20)
    data_model: str = Field(default="", max_length=3000)
    integration_points: str = Field(default="", max_length=2000)
    security_considerations: str = Field(default="", max_length=2000)


class BuildTab(BaseModel):
    """Build phase data."""
    tasks: List[str] = Field(default_factory=list, max_length=200)
    sprint_plan: str = Field(default="", max_length=3000)
    sprint_start_date: Optional[str] = None
    sprint_end_date: Optional[str] = None
    jira_epic_id: Optional[str] = Field(None, max_length=50)
    jira_story_ids: List[str] = Field(default_factory=list, max_length=100)
    repository_url: str = Field(default="", max_length=500)
    branch_name: str = Field(default="", max_length=100)


class ValidationTab(BaseModel):
    """Validation phase data."""
    test_cases: str = Field(default="", max_length=5000)
    test_results: str = Field(default="", max_length=3000)
    bug_log: List[Dict[str, Any]] = Field(default_factory=list, max_length=100)
    qa_sign_off: bool = False
    automated_test_coverage: Optional[float] = Field(None, ge=0, le=100)
    manual_test_status: str = Field(default="", max_length=1000)


class DeploymentTab(BaseModel):
    """Deployment phase data."""
    deployment_schedule: Optional[str] = None
    rollout_plan: str = Field(default="", max_length=3000)
    environment_config: str = Field(default="", max_length=2000)
    rollback_plan: str = Field(default="", max_length=2000)
    training_materials: List[str] = Field(default_factory=list, max_length=20)
    communication_plan: str = Field(default="", max_length=1500)
    deployment_checklist: str = Field(default="", max_length=2000)


class ImplementationTab(BaseModel):
    """Implementation/monitoring phase data."""
    success_metrics: Dict[str, float] = Field(default_factory=dict)
    issue_log: str = Field(default="", max_length=3000)
    user_feedback: str = Field(default="", max_length=2000)
    performance_data: str = Field(default="", max_length=2000)
    uptime_percentage: Optional[float] = Field(None, ge=0, le=100)
    adoption_rate: Optional[float] = Field(None, ge=0, le=100)


class ClosingTab(BaseModel):
    """Closing phase data."""
    retrospective: str = Field(default="", max_length=5000)
    lessons_learned: str = Field(default="", max_length=3000)
    sign_offs: Dict[str, bool] = Field(default_factory=dict)
    final_costs: Optional[float] = Field(None, ge=0)
    final_roi: Optional[float] = Field(None)
    archive_location: str = Field(default="", max_length=500)
    knowledge_transfer: str = Field(default="", max_length=2000)


class AuditLogEntry(BaseModel):
    """Audit log entry for tracking changes."""
    timestamp: datetime
    user: str = Field(max_length=100)
    action: str = Field(max_length=500)
    trace_id: str = Field(max_length=100)
    tab_name: Optional[str] = Field(None, max_length=50)
    field_name: Optional[str] = Field(None, max_length=100)


class Demand(BaseModel):
    """Complete demand/project structure."""
    demand_id: str = Field(max_length=50)
    created_at: datetime
    last_modified: datetime
    status: str = Field(default="Draft", max_length=50)
    
    # Tab data
    ideation: IdeationTab = Field(default_factory=IdeationTab)
    requirements: RequirementsTab = Field(default_factory=RequirementsTab)
    assessment: AssessmentTab = Field(default_factory=AssessmentTab)
    design: DesignTab = Field(default_factory=DesignTab)
    build: BuildTab = Field(default_factory=BuildTab)
    validation: ValidationTab = Field(default_factory=ValidationTab)
    deployment: DeploymentTab = Field(default_factory=DeploymentTab)
    implementation: ImplementationTab = Field(default_factory=ImplementationTab)
    closing: ClosingTab = Field(default_factory=ClosingTab)
    
    # Metadata
    progress_percentage: float = Field(default=0, ge=0, le=100)
    audit_log: List[AuditLogEntry] = Field(default_factory=list)
    
    @field_validator('demand_id')
    @classmethod
    def validate_demand_id(cls, v: str) -> str:
        """Validate demand ID format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Demand ID cannot be empty")
        return v
