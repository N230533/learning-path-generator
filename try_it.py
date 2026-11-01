from path_generator import generate_learning_path

path = generate_learning_path("Python for data analysis", "Beginner", 5)
for step in path:
    print(f"Stage {step['stage']}: {step['title']} ({step['duration_weeks']} weeks)")