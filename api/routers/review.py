from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel
from api.ingestion.store import get_all_tasks

router = APIRouter(prefix="/review", tags=["review"])

class ReviewTransaction(BaseModel):
    id: str
    date: str
    description: str
    amount: float
    type: str
    category: Optional[str] = "unsure"
    confidence: float
    source_file: str

@router.get("/transactions", response_model=List[ReviewTransaction])
async def get_transactions_for_review():
    """
    Get all transactions from successfully parsed bank statements.
    """
    all_tasks = get_all_tasks()
    review_items = []
    
    for task in all_tasks:
        # Check if task is complete and is a bank statement
        if task.get("status") == "complete" and task.get("document_type") == "bank_statement":
            result = task.get("result", {})
            transactions = result.get("raw_data", {}).get("transactions", [])
            
            for idx, txn in enumerate(transactions):
                # Create a unique ID for the frontend key
                txn_id = f"{task['task_id']}_{idx}"
                
                review_items.append(ReviewTransaction(
                    id=txn_id,
                    date=txn.get("date"),
                    description=txn.get("description"),
                    amount=txn.get("amount"),
                    type=txn.get("type"),
                    category=txn.get("category", "unsure"),
                    confidence=txn.get("confidence", 0.0),
                    source_file=task.get("filename")
                ))
    
    return review_items
