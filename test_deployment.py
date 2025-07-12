#!/usr/bin/env python3
"""
Test script to verify the deployment is working correctly
"""

import sys
import os
from pathlib import Path

def test_backend_imports():
    """Test that all backend imports work correctly"""
    print("🔍 Testing backend imports...")
    
    try:
        # Add the current directory to path
        sys.path.append('.')
        
        # Test core modules
        from data_dictionary import DataDictionary
        from database_manager import DatabaseManager
        from llm_connector import LLMConnector
        from agents import process_with_agents
        
        print("✅ All backend modules imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Backend import error: {e}")
        return False

def test_data_dictionary():
    """Test data dictionary functionality"""
    print("🔍 Testing data dictionary...")
    
    try:
        from data_dictionary import DataDictionary
        data_dict = DataDictionary()
        context = data_dict.get_comprehensive_context()
        
        if len(context) > 100:  # Should have substantial context
            print("✅ Data dictionary working correctly")
            return True
        else:
            print("❌ Data dictionary context too small")
            return False
            
    except Exception as e:
        print(f"❌ Data dictionary error: {e}")
        return False

def test_database_manager():
    """Test database manager functionality"""
    print("🔍 Testing database manager...")
    
    try:
        from database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Test demo data creation
        db_manager.create_demo_data()
        
        if len(db_manager.tables_loaded) > 0:
            print(f"✅ Database manager working correctly - {len(db_manager.tables_loaded)} tables loaded")
            return True
        else:
            print("❌ Database manager failed to load tables")
            return False
            
    except Exception as e:
        print(f"❌ Database manager error: {e}")
        return False

def test_agent_system():
    """Test multi-agent system"""
    print("🔍 Testing multi-agent system...")
    
    try:
        from agents import process_with_agents
        from database_manager import DatabaseManager
        from data_dictionary import DataDictionary
        
        # Create test components
        db_manager = DatabaseManager()
        db_manager.create_demo_data()
        data_dict = DataDictionary()
        
        # Test a simple query
        test_query = "SELECT COUNT(*) as total FROM PROD_MQT_CONSULTING_PIPELINE"
        
        result = process_with_agents(
            sql_query=test_query,
            question="How many pipeline records are there?",
            db_manager=db_manager,
            data_dict=data_dict,
            db_type='SQLite'
        )
        
        if result['success']:
            print("✅ Multi-agent system working correctly")
            return True
        else:
            print("❌ Multi-agent system failed")
            return False
            
    except Exception as e:
        print(f"❌ Agent system error: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("🔍 Testing file structure...")
    
    required_files = [
        'frontend/package.json',
        'frontend/app/layout.tsx',
        'frontend/app/page.tsx',
        'frontend/components/QueryInterface.tsx',
        'backend/main.py',
        'backend/requirements.txt',
        'docker-compose.yml',
        'deploy.sh',
        'DEPLOYMENT.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if not missing_files:
        print("✅ All required files present")
        return True
    else:
        print(f"❌ Missing files: {missing_files}")
        return False

def main():
    """Run all tests"""
    print("🚀 IBM Sales Pipeline Analytics - Deployment Test")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Backend Imports", test_backend_imports),
        ("Data Dictionary", test_data_dictionary),
        ("Database Manager", test_database_manager),
        ("Agent System", test_agent_system),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"   ⚠️  {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Deployment is ready.")
        print("\n🚀 Next steps:")
        print("   1. Run: ./deploy.sh")
        print("   2. Open: http://localhost:3000")
        print("   3. Configure LLM in the LLM Setup tab")
        print("   4. Load demo data in the Data Setup tab")
        print("   5. Start asking questions!")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)