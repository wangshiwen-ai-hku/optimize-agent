"""
检查配置是否正确加载
"""

from pathlib import Path
from src.config.manager import ConfigManager

config_path = Path("src/agent/config.yaml")
config = ConfigManager(config_path)

print("=" * 60)
print("Configuration Check")
print("=" * 60)

# 检查 tutor 配置
try:
    tutor_config = config.get_agent_config("tutor")
    print("\n✅ Tutor Config:")
    print(f"  - Agent Name: {tutor_config.agent_name}")
    print(f"  - Model: {tutor_config.model.model}")
    print(f"  - Temperature: {tutor_config.model.temperature}")
    print(f"  - Prompt: {tutor_config.prompt[:50]}..." if tutor_config.prompt else "  - Prompt: None")
except Exception as e:
    print(f"\n❌ Tutor Config Error: {e}")

# 检查 solver 配置
try:
    solver_config = config.get_agent_config("solver")
    print("\n✅ Solver Config:")
    print(f"  - Agent Name: {solver_config.agent_name}")
    print(f"  - Model: {solver_config.model.model}")
    print(f"  - Temperature: {solver_config.model.temperature}")
    print(f"  - Prompt: {solver_config.prompt[:50]}..." if solver_config.prompt else "  - Prompt: None")
except Exception as e:
    print(f"\n❌ Solver Config Error: {e}")

# 检查 code_executor 配置
try:
    executor_config = config.get_agent_config("code_executor")
    print("\n✅ Code Executor Config:")
    print(f"  - Agent Name: {executor_config.agent_name}")
    print(f"  - Model: {executor_config.model.model}")
    print(f"  - Temperature: {executor_config.model.temperature}")
    print(f"  - Prompt: {executor_config.prompt[:50]}..." if executor_config.prompt else "  - Prompt: None")
except Exception as e:
    print(f"\n❌ Code Executor Config Error: {e}")

print("\n" + "=" * 60)
print("Configuration check complete!")
print("=" * 60)
