"""
Main demonstration runner script.
Executes all demonstrations and generates comprehensive results.
"""

import os
import sys
import time
from datetime import datetime
import json
from pathlib import Path

# Import demonstration modules
sys.path.append(str(Path(__file__).parent))
from basic_examples.memory_operations import demonstrate_basic_operations
from advanced_examples.multi_modal_memory import demonstrate_multi_modal_operations

class DemonstrationRunner:
    def __init__(self):
        self.results_dir = Path(__file__).parent / "performance_results"
        self.results_dir.mkdir(exist_ok=True)
        
    def run_all_demonstrations(self):
        """Run all demonstrations and collect results."""
        print("\n=== Running All Demonstrations ===\n")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "demonstrations": {},
            "overall_success": True
        }
        
        # Run basic operations demo
        print("\nRunning Basic Operations Demo...")
        try:
            start_time = time.time()
            success = demonstrate_basic_operations()
            duration = time.time() - start_time
            
            results["demonstrations"]["basic_operations"] = {
                "success": success,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"Basic Operations Demo: {'Success' if success else 'Failed'}")
            
        except Exception as e:
            print(f"Error: Basic Operations Demo failed: {str(e)}")
            results["demonstrations"]["basic_operations"] = {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            results["overall_success"] = False
        
        # Run multi-modal operations demo
        print("\nRunning Multi-Modal Operations Demo...")
        try:
            start_time = time.time()
            success = demonstrate_multi_modal_operations()
            duration = time.time() - start_time
            
            results["demonstrations"]["multi_modal_operations"] = {
                "success": success,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"Multi-Modal Operations Demo: {'Success' if success else 'Failed'}")
            
        except Exception as e:
            print(f"Error: Multi-Modal Operations Demo failed: {str(e)}")
            results["demonstrations"]["multi_modal_operations"] = {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            results["overall_success"] = False
        
        # Save results
        results_file = self.results_dir / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("\nDemonstration Results:")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
        return results["overall_success"]

def main():
    """Main entry point for running demonstrations."""
    runner = DemonstrationRunner()
    success = runner.run_all_demonstrations()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
