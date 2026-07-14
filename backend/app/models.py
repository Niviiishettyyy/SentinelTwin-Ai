from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="analyst")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    id = Column(Integer, primary_key=True, index=True)
    scenario_name = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="running")  # running | completed | failed
    steps_json = Column(Text)  # JSON-encoded list of step dicts
    peak_risk = Column(Float, default=0.0)


class Incident(Base):
    """Experience Engine ledger (Section 9.7 / 9b)."""
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    detected_pattern = Column(String, nullable=False)
    action_taken = Column(String, nullable=False)
    outcome = Column(String, nullable=False)  # contained | escalated | ineffective
    risk_reduced = Column(Float, default=0.0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class SettingsPreference(Base):
    __tablename__ = "settings_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)


class AnalystLabel(Base):
    """
    Blind human risk labels, collected independently of the formula's
    own output, used to compute rank correlation (Kendall's tau) between
    the composite risk formula and human judgment -- Analyst Consensus
    Calibration.
    """
    __tablename__ = "analyst_labels"
    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, nullable=False)
    labeler = Column(String, nullable=False)
    risk_rating = Column(Integer, nullable=False)  # 1 (lowest) to 5 (highest), analyst's own judgment
    timestamp = Column(DateTime(timezone=True), server_default=func.now())