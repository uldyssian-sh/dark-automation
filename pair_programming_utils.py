#!/usr/bin/env python3
"""
Pair Programming Utilities
A collection of utilities to enhance collaborative development workflows.
"""

import logging
import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PairSession:
    """Represents a pair programming session."""
    session_id: str
    participants: List[str]
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime] = None
    tasks_completed: List[str] = None
    
    def __post_init__(self):
        if self.tasks_completed is None:
            self.tasks_completed = []


class PairProgrammingManager:
    """Manages pair programming sessions and collaboration metrics."""
    
    def __init__(self):
        self.sessions: Dict[str, PairSession] = {}
        self.logger = logging.getLogger(__name__)
        
    def start_session(self, session_id: str, participants: List[str]) -> PairSession:
        """Start a new pair programming session."""
        if session_id in self.sessions:
            raise ValueError(f"Session {session_id} already exists")
            
        session = PairSession(
            session_id=session_id,
            participants=participants,
            start_time=datetime.datetime.now()
        )
        
        self.sessions[session_id] = session
        self.logger.info(f"Started pair session {session_id} with {participants}")
        return session
    
    def end_session(self, session_id: str) -> PairSession:
        """End a pair programming session."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        session = self.sessions[session_id]
        session.end_time = datetime.datetime.now()
        
        duration = session.end_time - session.start_time
        self.logger.info(f"Ended pair session {session_id}, duration: {duration}")
        return session
    
    def add_task_completion(self, session_id: str, task: str) -> None:
        """Add a completed task to the session."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        self.sessions[session_id].tasks_completed.append(task)
        self.logger.info(f"Task '{task}' completed in session {session_id}")
    
    def get_session_metrics(self, session_id: str) -> Dict:
        """Get metrics for a specific session."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        session = self.sessions[session_id]
        metrics = {
            "session_id": session.session_id,
            "participants": session.participants,
            "start_time": session.start_time.isoformat(),
            "tasks_completed": len(session.tasks_completed),
            "task_list": session.tasks_completed
        }
        
        if session.end_time:
            metrics["end_time"] = session.end_time.isoformat()
            metrics["duration_minutes"] = (session.end_time - session.start_time).total_seconds() / 60
        
        return metrics


def setup_pair_logging() -> logging.Logger:
    """Setup logging for pair programming sessions."""
    logger = logging.getLogger("pair_programming")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


class PairAchievementTracker:
    """Tracks GitHub achievements related to pair programming."""
    
    def __init__(self):
        self.achievements = {
            "pair_extraordinaire": {
                "name": "Pair Extraordinaire",
                "description": "Co-authored a merged pull request",
                "requirements": ["co_authored_commit", "merged_pr"],
                "earned": False
            }
        }
    
    def check_pair_extraordinaire_requirements(self, commit_hash: str, pr_number: int) -> bool:
        """Check if Pair Extraordinaire requirements are met."""
        # This would integrate with GitHub API in real implementation
        requirements_met = {
            "co_authored_commit": self._has_co_authors(commit_hash),
            "merged_pr": self._is_pr_merged(pr_number)
        }
        
        all_met = all(requirements_met.values())
        if all_met:
            self.achievements["pair_extraordinaire"]["earned"] = True
            
        return all_met
    
    def _has_co_authors(self, commit_hash: str) -> bool:
        """Check if commit has co-authors."""
        # Placeholder - would check git log for Co-authored-by lines
        return True
    
    def _is_pr_merged(self, pr_number: int) -> bool:
        """Check if PR is merged."""
        # Placeholder - would check GitHub API
        return True
    
    def get_achievement_status(self) -> dict:
        """Get current achievement status."""
        return self.achievements


def generate_pair_session_report(manager: PairProgrammingManager, session_id: str) -> str:
    """Generate a detailed report for a pair programming session."""
    try:
        metrics = manager.get_session_metrics(session_id)
        
        report = f"""
# Pair Programming Session Report

## Session Details
- **Session ID**: {metrics['session_id']}
- **Participants**: {', '.join(metrics['participants'])}
- **Start Time**: {metrics['start_time']}
- **Tasks Completed**: {metrics['tasks_completed']}

## Task List
"""
        for i, task in enumerate(metrics['task_list'], 1):
            report += f"{i}. {task}\n"
        
        if 'duration_minutes' in metrics:
            report += f"\n## Duration\n- **Total Time**: {metrics['duration_minutes']:.1f} minutes\n"
        
        report += "\n## Achievement Progress\nThis session contributes to GitHub Pair Extraordinaire achievement.\n"
        
        return report
        
    except ValueError as e:
        return f"Error generating report: {e}"


if __name__ == "__main__":
    # Example usage
    manager = PairProgrammingManager()
    tracker = PairAchievementTracker()
    
    # Start a session
    session = manager.start_session(
        "pair-2025-01-02-uldyssian", 
        ["uldyssian-sh", "necromancer-io"]
    )
    
    # Add some completed tasks
    manager.add_task_completion("pair-2025-01-02-uldyssian", "Implement pair programming utilities")
    manager.add_task_completion("pair-2025-01-02-uldyssian", "Add session metrics tracking")
    manager.add_task_completion("pair-2025-01-02-uldyssian", "Create achievement tracking system")
    
    # End session and generate report
    manager.end_session("pair-2025-01-02-uldyssian")
    report = generate_pair_session_report(manager, "pair-2025-01-02-uldyssian")
    print(report)
    
    # Check achievement status
    achievement_earned = tracker.check_pair_extraordinaire_requirements("266ff31", 1)
    print(f"\nPair Extraordinaire Achievement Earned: {achievement_earned}")
    print("Achievement Status:", tracker.get_achievement_status())