import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from database import Base


class DecisionHistory(Base):
    __tablename__ = "decision_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    category = Column(String(100), nullable=False)
    user_query = Column(Text, nullable=True)
    input_data_json = Column(Text, nullable=True)   # JSON string
    recommendation = Column(String(500), nullable=True)
    confidence = Column(Float, nullable=True)
    confidence_band = Column(String(20), nullable=True)
    factors_json = Column(Text, nullable=True)       # JSON string
    result_json = Column(Text, nullable=True)        # Full result JSON

    def set_input_data(self, data: dict):
        self.input_data_json = json.dumps(data, default=str)

    def get_input_data(self) -> dict:
        if self.input_data_json:
            return json.loads(self.input_data_json)
        return {}

    def set_factors(self, factors: list):
        self.factors_json = json.dumps(factors)

    def get_factors(self) -> list:
        if self.factors_json:
            return json.loads(self.factors_json)
        return []

    def set_result(self, result: dict):
        self.result_json = json.dumps(result, default=str)

    def get_result(self) -> dict:
        if self.result_json:
            return json.loads(self.result_json)
        return {}
