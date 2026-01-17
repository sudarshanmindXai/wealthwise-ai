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
    
    print(f"DEBUG /review/transactions: Found {len(all_tasks)} total tasks")
    
    for task in all_tasks:
        print(f"DEBUG Task: id={task.get('task_id')}, status={task.get('status')}, doc_type={task.get('document_type')}")
        
        # Check if task is complete and is a bank statement
        if task.get("status") == "complete" and task.get("document_type") == "bank_statement":
            result = task.get("result", {})
            print(f"DEBUG Result keys: {result.keys() if result else 'None'}")
            
            # Handle both direct and nested raw_data structures
            raw_data = result.get("raw_data", result)
            transactions = raw_data.get("transactions", [])
            
            print(f"DEBUG Found {len(transactions)} transactions in task {task.get('task_id')}")
            
            for idx, txn in enumerate(transactions):
                try:
                    # Create a unique ID for the frontend key
                    txn_id = f"{task['task_id']}_{idx}"
                    
                    # Ensure amount is a float
                    raw_amt = txn.get("amount", 0.0)
                    try:
                        amt = float(raw_amt)
                    except ValueError:
                        amt = 0.0

                    review_items.append(ReviewTransaction(
                        id=txn_id,
                        date=str(txn.get("date", "")), # Ensure string
                        description=str(txn.get("description", "Unknown")),
                        amount=amt,
                        type=str(txn.get("type", "debit")),
                        category=str(txn.get("category", "unsure")),
                        confidence=float(txn.get("confidence", 0.0)),
                        source_file=str(task.get("filename", "unknown"))
                    ))
                except Exception as e:
                    print(f"Skipping malformed transaction in task {task.get('task_id')}: {e}")
                    continue
    
    print(f"DEBUG Returning {len(review_items)} review items")
    return review_items

# Simple in-memory store for classified transactions
# In a real app, this would be in a database
REVIEW_STORE = {
    "classifications": [],
    "is_complete": False
}

class SaveReviewRequest(BaseModel):
    classifications: List[dict]  # {transactionId: str, category: str}

@router.post("/save")
async def save_review(request: SaveReviewRequest):
    """Save user classifications"""
    REVIEW_STORE["classifications"] = request.classifications
    REVIEW_STORE["is_complete"] = True
    return {"status": "success", "count": len(request.classifications)}

@router.get("/summary")
async def get_review_summary():
    """
    Aggregate classifications into income/expense totals for the dashboard.
    Crucial for connecting Review step -> Dashboard.
    """
    # 1. Get all raw transactions to map back IDs
    all_txns = await get_transactions_for_review()
    txn_map = {t.id: t for t in all_txns}
    
    # 2. Aggregate
    summary = {
        "salary": 0.0,
        "business": 0.0,
        "gift": 0.0,
        "personal_expense": 0.0
    }
    
    # If no classifications saved yet (or accessed directly), try to use defaults
    classifications = REVIEW_STORE["classifications"]
    
    for c in classifications:
        tid = c.get("transactionId") or c.get("id") # Handle potential schema mismatch
        cat = c.get("category")
        
        txn = txn_map.get(str(tid)) # Ensure string ID matching
        if txn:
            amount = txn.amount
            if cat == "business":
                summary["business"] += amount
            elif cat == "personal":
                summary["personal_expense"] += amount
            elif cat == "gift":
                summary["gift"] += amount
            # Note: "salary" is usually parsed from salary slips, not bank txns, 
            # but we could infer it if we had a category for it. 
            # For now, we'll leave salary as 0 here and let the Dashboard 
            # fetch it from the Salary/Form16 parser result directly if needed.

    return summary
