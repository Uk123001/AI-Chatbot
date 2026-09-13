#!/usr/bin/env python3
"""
AI Booking Assistant - Project Validation Script
Run this to verify all components are working correctly
"""

import sys
import os
from pathlib import Path

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    print(f"\n{BLUE}{'='*60}")
    print(f"{text.center(60)}")
    print(f"{'='*60}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    print(f"{RED}✗ {text}{RESET}")


def print_warning(text):
    print(f"{YELLOW}⚠ {text}{RESET}")


def print_info(text):
    print(f"{BLUE}ℹ {text}{RESET}")


def check_python_version():
    """Check Python version"""
    print_header("1. Checking Python Version")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print_error(f"Python 3.8+ required, but found {version.major}.{version.minor}")
        return False


def check_required_files():
    """Check if required files exist"""
    print_header("2. Checking Project Files")
    
    required_files = [
        "main.py",
        "config.py",
        "models.py",
        "llm.py",
        "chat_logic.py",
        "rag_pipeline.py",
        "tools.py",
        "admin_dashboard.py",
        "embeddings.py",
        "utils.py",
        "constants.py",
        "logger.py",
        "requirements.txt",
        "README.md",
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print_success(f"Found {file}")
        else:
            print_error(f"Missing {file}")
            all_exist = False
    
    return all_exist


def check_dependencies():
    """Check if required packages are installed"""
    print_header("3. Checking Dependencies")
    
    required_packages = [
        ("streamlit", "Streamlit"),
        ("langchain", "LangChain"),
        ("sqlalchemy", "SQLAlchemy"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
    ]
    
    all_installed = True
    for package, name in required_packages:
        try:
            __import__(package)
            print_success(f"{name} is installed")
        except ImportError:
            print_error(f"{name} is not installed")
            print_info(f"Run: pip install {package}")
            all_installed = False
    
    return all_installed


def check_environment_variables():
    """Check if .env file exists and has required keys"""
    print_header("4. Checking Environment Variables")
    
    if not os.path.exists(".env"):
        print_warning(".env file not found")
        print_info("Copy .env.example to .env and add your API keys")
        return False
    else:
        print_success(".env file found")
    
    # Read and check .env
    env_vars = {}
    try:
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        print_error(f"Error reading .env: {e}")
        return False
    
    # Check for API key
    api_key_found = False
    if env_vars.get("GROQ_API_KEY"):
        print_success("GROQ_API_KEY is set")
        api_key_found = True
    elif env_vars.get("OPENAI_API_KEY"):
        print_success("OPENAI_API_KEY is set")
        api_key_found = True
    elif env_vars.get("GOOGLE_API_KEY"):
        print_success("GOOGLE_API_KEY is set")
        api_key_found = True
    else:
        print_error("No LLM API key found (GROQ_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY)")
        api_key_found = False
    
    return api_key_found


def check_database():
    """Check database configuration"""
    print_header("5. Checking Database")
    
    try:
        from models import init_db, get_session
        
        # Initialize database
        init_db()
        print_success("Database initialized successfully")
        
        # Test connection
        session = get_session()
        session.close()
        print_success("Database connection successful")
        
        return True
    except Exception as e:
        print_error(f"Database error: {e}")
        return False


def check_llm_provider():
    """Check LLM provider configuration"""
    print_header("6. Checking LLM Provider")
    
    try:
        from config import LLM_PROVIDER, GROQ_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY
        
        provider = LLM_PROVIDER.lower()
        print_info(f"Configured provider: {provider}")
        
        if provider == "groq":
            if not GROQ_API_KEY:
                print_error("GROQ_API_KEY not set")
                return False
            print_success("Groq configuration found")
        elif provider == "openai":
            if not OPENAI_API_KEY:
                print_error("OPENAI_API_KEY not set")
                return False
            print_success("OpenAI configuration found")
        elif provider == "google":
            if not GOOGLE_API_KEY:
                print_error("GOOGLE_API_KEY not set")
                return False
            print_success("Google configuration found")
        else:
            print_error(f"Unknown provider: {provider}")
            return False
        
        return True
    except Exception as e:
        print_error(f"LLM configuration error: {e}")
        return False


def check_embeddings():
    """Check embeddings and vector store"""
    print_header("7. Checking Embeddings")
    
    try:
        from embeddings import get_embeddings_model
        
        print_info("Loading embeddings model (this may take a moment)...")
        model = get_embeddings_model()
        print_success("Embeddings model loaded successfully")
        return True
    except Exception as e:
        print_error(f"Embeddings error: {e}")
        return False


def check_imports():
    """Check if all modules can be imported"""
    print_header("8. Checking Module Imports")
    
    modules = [
        "config",
        "constants",
        "logger",
        "utils",
        "models",
        "embeddings",
        "rag_pipeline",
        "llm",
        "chat_logic",
        "tools",
        "admin_dashboard",
    ]
    
    all_importable = True
    for module in modules:
        try:
            __import__(module)
            print_success(f"✓ {module}")
        except Exception as e:
            print_error(f"✗ {module}: {e}")
            all_importable = False
    
    return all_importable


def check_streamlit():
    """Check Streamlit installation"""
    print_header("9. Checking Streamlit")
    
    try:
        import streamlit as st
        version = st.__version__
        print_success(f"Streamlit {version} installed")
        return True
    except ImportError:
        print_error("Streamlit not installed")
        print_info("Run: pip install streamlit")
        return False


def check_optional_features():
    """Check optional dependencies"""
    print_header("10. Checking Optional Features")
    
    optional = [
        ("smtplib", "Email support"),
        ("psycopg2", "PostgreSQL support (optional)"),
        ("gunicorn", "Production server (optional)"),
    ]
    
    for package, description in optional:
        try:
            __import__(package)
            print_success(f"{description} available")
        except ImportError:
            print_warning(f"{description} not installed (optional)")


def run_diagnostics():
    """Run all diagnostics"""
    print_header("AI BOOKING ASSISTANT - PROJECT VALIDATION")
    
    results = []
    
    results.append(("Python Version", check_python_version()))
    results.append(("Project Files", check_required_files()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Environment Variables", check_environment_variables()))
    results.append(("Database", check_database()))
    results.append(("LLM Provider", check_llm_provider()))
    results.append(("Embeddings", check_embeddings()))
    results.append(("Module Imports", check_imports()))
    results.append(("Streamlit", check_streamlit()))
    
    check_optional_features()
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {name:<30} {status}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print_success("\nAll checks passed! You're ready to run the application.")
        print_info("Start the app with: streamlit run main.py")
        return True
    else:
        print_error("\nSome checks failed. Please fix the issues above.")
        print_info("Common solutions:")
        print_info("  - pip install -r requirements.txt")
        print_info("  - cp .env.example .env && edit .env")
        print_info("  - Check Python version (3.8+)")
        return False


def main():
    """Main entry point"""
    try:
        success = run_diagnostics()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nValidation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
