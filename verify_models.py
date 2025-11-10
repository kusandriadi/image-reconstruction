"""Verify that the two model files are actually different."""
import torch
from pathlib import Path

def verify_models():
    print("=" * 60)
    print("Model Verification Script")
    print("=" * 60)
    print()

    model1_path = Path("backend/model/ConvNext_REAL-ESRGAN.pth")
    model2_path = Path("backend/model/REAL-ESRGAN.pth")

    # Check if files exist
    print("Checking if model files exist...")
    if not model1_path.exists():
        print(f"❌ {model1_path} not found!")
        return
    if not model2_path.exists():
        print(f"❌ {model2_path} not found!")
        return

    print(f"✅ {model1_path.name} exists")
    print(f"✅ {model2_path.name} exists")
    print()

    # Check file sizes
    print("Checking file sizes...")
    size1 = model1_path.stat().st_size / (1024 * 1024)  # MB
    size2 = model2_path.stat().st_size / (1024 * 1024)  # MB

    print(f"  {model1_path.name}: {size1:.2f} MB")
    print(f"  {model2_path.name}: {size2:.2f} MB")
    print()

    if size1 == size2:
        print("⚠️  WARNING: File sizes are identical! Models might be the same.")
    else:
        print("✅ File sizes are different - models are likely different")
    print()

    # Load and check model structure
    print("Loading models (this may take a moment)...")
    try:
        model1 = torch.load(str(model1_path), map_location="cpu", weights_only=False)
        model2 = torch.load(str(model2_path), map_location="cpu", weights_only=False)

        print("✅ Both models loaded successfully")
        print()

        # Check structure
        print("Checking model structure...")

        def get_model_info(model, name):
            if isinstance(model, dict):
                print(f"\n{name}:")
                print(f"  Type: Dictionary checkpoint")
                print(f"  Keys: {list(model.keys())}")

                if 'params_ema' in model:
                    state_dict = model['params_ema']
                elif 'params' in model:
                    state_dict = model['params']
                else:
                    state_dict = model

                if isinstance(state_dict, dict):
                    print(f"  Number of parameters: {len(state_dict)}")
                    print(f"  First few keys: {list(state_dict.keys())[:5]}")

                    # Calculate total parameters
                    total_params = sum(p.numel() for p in state_dict.values() if hasattr(p, 'numel'))
                    print(f"  Total parameters: {total_params:,}")
                    return total_params, list(state_dict.keys())
            else:
                print(f"\n{name}:")
                print(f"  Type: Complete model object")
                print(f"  Class: {type(model).__name__}")
                return None, None

        params1, keys1 = get_model_info(model1, model1_path.name)
        params2, keys2 = get_model_info(model2, model2_path.name)

        print()
        print("=" * 60)
        print("VERIFICATION RESULT")
        print("=" * 60)

        if params1 is not None and params2 is not None:
            if params1 == params2 and keys1 == keys2:
                print("⚠️  WARNING: Models have identical structure!")
                print("   They might be the same model with different names.")
                print("   Parameter count:", params1)
            else:
                print("✅ Models are DIFFERENT!")
                if params1 != params2:
                    print(f"   {model1_path.name}: {params1:,} parameters")
                    print(f"   {model2_path.name}: {params2:,} parameters")
                if keys1 != keys2:
                    print("   Different parameter keys detected")

        print()
        print("To see which model is being used during reconstruction,")
        print("check the backend logs for lines containing:")
        print("  🎯 (model selection)")
        print("  ⚙️ (model loading)")
        print("  🔄 (model switching)")
        print()

    except Exception as e:
        print(f"❌ Error loading models: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_models()
