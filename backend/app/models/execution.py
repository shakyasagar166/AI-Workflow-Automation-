import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Execution(Base):
    __tablename__ = "executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="PENDING", index=True)  # PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
    trigger = Column(String(50), default="manual")  # manual, webhook, scheduled
    trigger_payload = Column(JSON, default=dict)
    
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True, default=0.0)
    
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    workflow = relationship("Workflow", back_populates="executions")
    step_executions = relationship("StepExecution", back_populates="execution", cascade="all, delete-orphan", order_by="StepExecution.started_at")
    logs = relationship("ExecutionLog", back_populates="execution", cascade="all, delete-orphan", order_by="ExecutionLog.timestamp")

class StepExecution(Base):
    __tablename__ = "step_executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    node_id = Column(String(100), nullable=False, index=True)
    node_type = Column(String(100), nullable=False)
    node_name = Column(String(255), nullable=True)
    
    status = Column(String(50), default="PENDING", index=True)  # PENDING, RUNNING, COMPLETED, FAILED, SKIPPED, RETRYING
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True, default=0.0)
    
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    retry_count = Column(Integer, default=0)
    error = Column(Text, nullable=True)

    execution = relationship("Execution", back_populates="step_executions")

class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    step_execution_id = Column(String(36), nullable=True)
    node_id = Column(String(100), nullable=True, index=True)
    
    level = Column(String(20), default="INFO")  # INFO, WARN, ERROR, DEBUG, AGENT_THOUGHT
    message = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    execution = relationship("Execution", back_populates="logs")
