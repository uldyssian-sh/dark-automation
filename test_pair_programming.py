#!/usr/bin/env python3
"""
Test suite for pair programming utilities.
Validates functionality and GitHub achievement tracking.
"""

import unittest
import datetime
from unittest.mock import patch, MagicMock
from pair_programming_utils import (
    PairProgrammingManager, 
    PairSession, 
    PairAchievementTracker,
    generate_pair_session_report
)


class TestPairProgrammingManager(unittest.TestCase):
    """Test cases for PairProgrammingManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = PairProgrammingManager()
        self.session_id = "test-session-2025"
        self.participants = ["uldyssian-sh", "necromancer-io"]
    
    def test_start_session(self):
        """Test starting a new pair programming session."""
        session = self.manager.start_session(self.session_id, self.participants)
        
        self.assertIsInstance(session, PairSession)
        self.assertEqual(session.session_id, self.session_id)
        self.assertEqual(session.participants, self.participants)
        self.assertIsInstance(session.start_time, datetime.datetime)
        self.assertIsNone(session.end_time)
        self.assertEqual(session.tasks_completed, [])
    
    def test_duplicate_session_error(self):
        """Test error when creating duplicate session."""
        self.manager.start_session(self.session_id, self.participants)
        
        with self.assertRaises(ValueError):
            self.manager.start_session(self.session_id, self.participants)
    
    def test_end_session(self):
        """Test ending a pair programming session."""
        self.manager.start_session(self.session_id, self.participants)
        session = self.manager.end_session(self.session_id)
        
        self.assertIsNotNone(session.end_time)
        self.assertIsInstance(session.end_time, datetime.datetime)
    
    def test_add_task_completion(self):
        """Test adding completed tasks to session."""
        self.manager.start_session(self.session_id, self.participants)
        task = "Implement GitHub achievement tracking"
        
        self.manager.add_task_completion(self.session_id, task)
        
        session = self.manager.sessions[self.session_id]
        self.assertIn(task, session.tasks_completed)
    
    def test_get_session_metrics(self):
        """Test retrieving session metrics."""
        self.manager.start_session(self.session_id, self.participants)
        self.manager.add_task_completion(self.session_id, "Test task")
        self.manager.end_session(self.session_id)
        
        metrics = self.manager.get_session_metrics(self.session_id)
        
        self.assertEqual(metrics["session_id"], self.session_id)
        self.assertEqual(metrics["participants"], self.participants)
        self.assertEqual(metrics["tasks_completed"], 1)
        self.assertIn("start_time", metrics)
        self.assertIn("end_time", metrics)
        self.assertIn("duration_minutes", metrics)


class TestPairAchievementTracker(unittest.TestCase):
    """Test cases for PairAchievementTracker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = PairAchievementTracker()
    
    def test_initial_achievement_state(self):
        """Test initial state of achievements."""
        achievements = self.tracker.get_achievement_status()
        
        self.assertIn("pair_extraordinaire", achievements)
        self.assertFalse(achievements["pair_extraordinaire"]["earned"])
    
    def test_pair_extraordinaire_requirements(self):
        """Test Pair Extraordinaire achievement requirements check."""
        result = self.tracker.check_pair_extraordinaire_requirements("test_commit", 1)
        
        self.assertTrue(result)
        achievements = self.tracker.get_achievement_status()
        self.assertTrue(achievements["pair_extraordinaire"]["earned"])


class TestReportGeneration(unittest.TestCase):
    """Test cases for report generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = PairProgrammingManager()
        self.session_id = "report-test-session"
        self.participants = ["uldyssian-sh", "necromancer-io"]
    
    def test_generate_session_report(self):
        """Test generating session report."""
        # Create and complete a session
        self.manager.start_session(self.session_id, self.participants)
        self.manager.add_task_completion(self.session_id, "Task 1")
        self.manager.add_task_completion(self.session_id, "Task 2")
        self.manager.end_session(self.session_id)
        
        report = generate_pair_session_report(self.manager, self.session_id)
        
        self.assertIn("Pair Programming Session Report", report)
        self.assertIn(self.session_id, report)
        self.assertIn("uldyssian-sh", report)
        self.assertIn("necromancer-io", report)
        self.assertIn("Task 1", report)
        self.assertIn("Task 2", report)
        self.assertIn("Achievement Progress", report)
    
    def test_report_error_handling(self):
        """Test report generation error handling."""
        report = generate_pair_session_report(self.manager, "nonexistent-session")
        
        self.assertIn("Error generating report", report)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios for pair programming workflow."""
    
    def test_complete_pair_programming_workflow(self):
        """Test complete pair programming workflow with achievement tracking."""
        manager = PairProgrammingManager()
        tracker = PairAchievementTracker()
        session_id = "integration-test-2025"
        participants = ["uldyssian-sh", "necromancer-io"]
        
        # Start session
        session = manager.start_session(session_id, participants)
        self.assertIsNotNone(session)
        
        # Add multiple tasks
        tasks = [
            "Set up pair programming environment",
            "Implement core functionality",
            "Write comprehensive tests",
            "Create documentation"
        ]
        
        for task in tasks:
            manager.add_task_completion(session_id, task)
        
        # End session
        manager.end_session(session_id)
        
        # Generate report
        report = generate_pair_session_report(manager, session_id)
        self.assertIn("4", report)  # Should show 4 completed tasks
        
        # Check achievement
        achievement_earned = tracker.check_pair_extraordinaire_requirements("test_hash", 1)
        self.assertTrue(achievement_earned)
        
        # Verify final state
        metrics = manager.get_session_metrics(session_id)
        self.assertEqual(len(metrics["task_list"]), 4)
        self.assertIn("duration_minutes", metrics)


if __name__ == "__main__":
    # Configure test logging
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    unittest.main(verbosity=2)