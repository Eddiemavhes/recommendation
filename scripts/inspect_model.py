import pickle

def inspect_pickle():
    try:
        with open('ml_models/job_matching_model.pkl', 'rb') as f:
            data = pickle.load(f)
            print("\nPickle file contents:")
            print("Type:", type(data))
            print("\nKeys if dictionary:", data.keys() if isinstance(data, dict) else "Not a dictionary")
            print("\nAttributes if object:", dir(data) if not isinstance(data, dict) else "Is a dictionary")
    except Exception as e:
        print(f"Error inspecting pickle file: {str(e)}")

if __name__ == '__main__':
    inspect_pickle()